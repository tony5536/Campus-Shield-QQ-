"""
Core LLM utilities for CampusShield AI.

Provides multi-turn conversation, summarization, report generation,
and anomaly explanation using LangChain orchestration.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI

# Try to import LangChain components - handle missing modules gracefully
# In LangChain 1.x, some modules were restructured or removed
try:
    from langchain.chains import LLMChain, RetrievalQA
except ImportError:
    # Try alternative import paths for LangChain 1.x
    try:
        from langchain_core.chains import LLMChain
        RetrievalQA = None  # May not be available in newer versions
    except ImportError:
        LLMChain = None
        RetrievalQA = None
        logging.warning("LLMChain not available - some features may be disabled")

try:
    from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
except ImportError:
    # Try alternative import paths
    try:
        from langchain_core.memory import ConversationBufferMemory, ConversationSummaryMemory
    except ImportError:
        ConversationBufferMemory = None
        ConversationSummaryMemory = None
        logging.warning("ConversationMemory not available - some features may be disabled")

try:
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
except ImportError:
    # Use langchain_core.prompts which is available in LangChain 1.x
    try:
        from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    except ImportError:
        PromptTemplate = None
        ChatPromptTemplate = None
        logging.warning("PromptTemplate not available - some features may be disabled")

try:
    from langchain.callbacks import StreamingStdOutCallbackHandler
except ImportError:
    try:
        from langchain_core.callbacks import StreamingStdOutCallbackHandler
    except ImportError:
        StreamingStdOutCallbackHandler = None

from .prompts import (
    CHAT_TEMPLATE,
    CONTEXTUAL_CHAT_TEMPLATE,
    SUMMARIZE_TEMPLATE,
    DAILY_REPORT_TEMPLATE,
    WEEKLY_REPORT_TEMPLATE,
    ANOMALY_EXPLANATION_TEMPLATE,
    PATTERN_ANALYSIS_TEMPLATE,
    format_incidents_for_context,
    create_chat_history_string,
    create_anomaly_context,
)
from .vector_store import get_vector_store, VectorStore

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

class LLMConfig:
    """Configuration for LLM behavior."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        top_p: float = 0.95,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize LLM configuration.
        
        Args:
            model: OpenAI model name
            temperature: Sampling temperature (0-2)
            max_tokens: Max response tokens
            top_p: Nucleus sampling parameter
            system_prompt: Custom system prompt
        """
        self.model = model
        self.temperature = max(0, min(2, temperature))  # Clamp to 0-2
        self.max_tokens = max(1, min(4000, max_tokens))  # Clamp to 1-4000
        self.top_p = max(0, min(1, top_p))  # Clamp to 0-1
        self.system_prompt = system_prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """Export config as dictionary."""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
        }


# ============================================================================
# CORE LLM CHAIN MANAGER
# ============================================================================

class LLMChainManager:
    """
    Manages LLM chains for various tasks.
    Handles initialization, caching, and execution.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM chain manager.
        
        Args:
            config: LLMConfig instance
        """
        self.config = config or LLMConfig()
        self.llm = self._initialize_llm()
        self.chains = {}
        self.conversation_memories = {}
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize ChatOpenAI instance."""
        try:
            return ChatOpenAI(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                api_key=os.getenv('OPENAI_API_KEY'),
                streaming=False,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def update_config(self, config: LLMConfig):
        """Update LLM configuration."""
        self.config = config
        self.llm = self._initialize_llm()
        self.chains.clear()  # Clear cached chains
    
    def _get_or_create_chain(
        self,
        chain_name: str,
        prompt: PromptTemplate,
        use_memory: bool = False,
    ) -> LLMChain:
        """Get or create an LLM chain."""
        if LLMChain is None:
            raise RuntimeError("LLMChain is not available. Please install required LangChain packages.")
        
        if prompt is None:
            raise RuntimeError("PromptTemplate is not available. Please install required LangChain packages.")
        
        if chain_name in self.chains:
            return self.chains[chain_name]
        
        if use_memory:
            memory = self._get_or_create_memory(chain_name)
            chain = LLMChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                verbose=False,
            )
        else:
            chain = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=False,
            )
        
        self.chains[chain_name] = chain
        return chain
    
    def _get_or_create_memory(self, memory_name: str) -> ConversationBufferMemory:
        """Get or create conversation memory."""
        if ConversationBufferMemory is None:
            raise RuntimeError("ConversationBufferMemory is not available. Please install required LangChain packages.")
        
        if memory_name not in self.conversation_memories:
            self.conversation_memories[memory_name] = ConversationBufferMemory(
                ai_prefix="Assistant",
                human_prefix="User",
            )
        return self.conversation_memories[memory_name]
    
    def clear_memory(self, memory_name: Optional[str] = None):
        """Clear conversation memory."""
        if memory_name:
            if memory_name in self.conversation_memories:
                self.conversation_memories[memory_name].clear()
        else:
            self.conversation_memories.clear()


# ============================================================================
# MULTI-TURN CHAT
# ============================================================================

class MultiTurnChat:
    """Handles multi-turn conversations with context awareness."""
    
    def __init__(
        self,
        chain_manager: LLMChainManager,
        vector_store: Optional[VectorStore] = None,
        max_history: int = 10,
        use_context_retrieval: bool = True,
    ):
        """
        Initialize multi-turn chat.
        
        Args:
            chain_manager: LLMChainManager instance
            vector_store: Optional vector store for context
            max_history: Max messages to keep in history
            use_context_retrieval: Enable historical incident retrieval
        """
        self.chain_manager = chain_manager
        self.vector_store = vector_store or get_vector_store()
        self.max_history = max_history
        self.use_context_retrieval = use_context_retrieval
        self.chat_history = []
    
    def add_message(self, role: str, content: str):
        """Add message to chat history."""
        self.chat_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Trim history if exceeds max
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def chat(self, user_input: str, conversation_id: str = "default") -> str:
        """
        Process user input and generate response.
        
        Args:
            user_input: User message
            conversation_id: Conversation identifier for memory
        
        Returns:
            Assistant response
        """
        try:
            self.add_message("user", user_input)
            
            # Retrieve relevant context if enabled
            context = ""
            if self.use_context_retrieval and self.vector_store:
                similar_incidents = self.vector_store.retrieve_similar_incidents(
                    user_input,
                    top_k=3,
                    filters={'min_severity': 0.5}
                )
                if similar_incidents:
                    context = format_incidents_for_context(similar_incidents)
            
            # Create chat history string
            chat_history_str = create_chat_history_string(self.chat_history[:-1])
            
            # Execute chain
            chain = self.chain_manager._get_or_create_chain(
                f"chat_{conversation_id}",
                CONTEXTUAL_CHAT_TEMPLATE,
                use_memory=True,
            )
            
            response = chain.run(
                user_input=user_input,
                chat_history=chat_history_str,
                relevant_incidents=context,
            )
            
            self.add_message("assistant", response)
            return response
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_response = "I encountered an error processing your request. Please try again."
            self.add_message("assistant", error_response)
            return error_response
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get current chat history."""
        return self.chat_history.copy()
    
    def clear_history(self):
        """Clear chat history."""
        self.chat_history = []


# ============================================================================
# INCIDENT SUMMARIZATION
# ============================================================================

class IncidentSummarizer:
    """Generates concise summaries of incident data."""
    
    def __init__(self, chain_manager: LLMChainManager):
        """Initialize summarizer."""
        self.chain_manager = chain_manager
    
    def summarize_incidents(
        self,
        incidents: List[Dict[str, Any]],
        focus: Optional[str] = None,
    ) -> str:
        """
        Summarize incident list.
        
        Args:
            incidents: List of incident dictionaries
            focus: Optional focus area (e.g., 'security', 'health')
        
        Returns:
            Summary text
        """
        try:
            # Format incidents
            incidents_text = format_incidents_for_context(incidents)
            
            prompt = SUMMARIZE_TEMPLATE
            chain = self.chain_manager._get_or_create_chain(
                "summarizer",
                prompt,
            )
            
            summary = chain.run(incidents_data=incidents_text)
            return summary
        
        except Exception as e:
            logger.error(f"Error summarizing incidents: {e}")
            return "Error generating summary."
    
    def summarize_period(
        self,
        incidents: List[Dict[str, Any]],
        period: str = "day",
    ) -> str:
        """
        Summarize incidents for a time period.
        
        Args:
            incidents: List of incidents
            period: 'day', 'week', or 'month'
        
        Returns:
            Period summary
        """
        # Group by severity
        high_severity = [i for i in incidents if i.get('severity', 0) > 0.7]
        medium_severity = [i for i in incidents if 0.3 < i.get('severity', 0) <= 0.7]
        low_severity = [i for i in incidents if i.get('severity', 0) <= 0.3]
        
        summary = f"""
{period.upper()} INCIDENT SUMMARY
Total Incidents: {len(incidents)}

High Severity ({len(high_severity)}): {', '.join([i.get('incident_type', 'Unknown') for i in high_severity[:3]])}
Medium Severity ({len(medium_severity)}): {', '.join([i.get('incident_type', 'Unknown') for i in medium_severity[:3]])}
Low Severity ({len(low_severity)}): {', '.join([i.get('incident_type', 'Unknown') for i in low_severity[:3]])}
"""
        return summary


# ============================================================================
# REPORT GENERATION
# ============================================================================

class ReportGenerator:
    """Generates professional incident reports."""
    
    def __init__(self, chain_manager: LLMChainManager):
        """Initialize report generator."""
        self.chain_manager = chain_manager
    
    def generate_daily_report(
        self,
        incidents: List[Dict[str, Any]],
        report_date: Optional[str] = None,
    ) -> str:
        """
        Generate daily security report.
        
        Args:
            incidents: List of incidents for the day
            report_date: Report date (default: today)
        
        Returns:
            Report text
        """
        try:
            report_date = report_date or datetime.now().strftime("%Y-%m-%d")
            
            # Calculate statistics
            critical = [i for i in incidents if i.get('severity', 0) > 0.8]
            total = len(incidents)
            
            incidents_summary = format_incidents_for_context(incidents[:5])
            critical_events = format_incidents_for_context(critical)
            
            prompt = DAILY_REPORT_TEMPLATE
            chain = self.chain_manager._get_or_create_chain(
                "daily_report",
                prompt,
            )
            
            report = chain.run(
                date=report_date,
                incidents_count=total,
                incidents_summary=incidents_summary,
                critical_events=critical_events,
            )
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return "Error generating report."
    
    def generate_weekly_report(
        self,
        incidents: List[Dict[str, Any]],
        week_start: Optional[str] = None,
    ) -> str:
        """
        Generate weekly security report.
        
        Args:
            incidents: List of incidents for the week
            week_start: Week start date (default: 7 days ago)
        
        Returns:
            Report text
        """
        try:
            if not week_start:
                week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            week_end = datetime.now().strftime("%Y-%m-%d")
            week_dates = f"{week_start} to {week_end}"
            
            # Calculate statistics
            severity_breakdown = self._calculate_severity_breakdown(incidents)
            trends = self._analyze_trends(incidents)
            hotspots = self._find_hotspots(incidents)
            
            prompt = WEEKLY_REPORT_TEMPLATE
            chain = self.chain_manager._get_or_create_chain(
                "weekly_report",
                prompt,
            )
            
            report = chain.run(
                week_dates=week_dates,
                total_incidents=len(incidents),
                severity_breakdown=severity_breakdown,
                trend_analysis=trends,
                hotspots=hotspots,
            )
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return "Error generating report."
    
    @staticmethod
    def _calculate_severity_breakdown(incidents: List[Dict[str, Any]]) -> str:
        """Calculate severity distribution."""
        critical = sum(1 for i in incidents if i.get('severity', 0) > 0.8)
        high = sum(1 for i in incidents if 0.6 < i.get('severity', 0) <= 0.8)
        medium = sum(1 for i in incidents if 0.3 < i.get('severity', 0) <= 0.6)
        low = sum(1 for i in incidents if i.get('severity', 0) <= 0.3)
        
        return f"Critical: {critical}, High: {high}, Medium: {medium}, Low: {low}"
    
    @staticmethod
    def _analyze_trends(incidents: List[Dict[str, Any]]) -> str:
        """Analyze incident trends."""
        incident_types = {}
        for incident in incidents:
            itype = incident.get('incident_type', 'Unknown')
            incident_types[itype] = incident_types.get(itype, 0) + 1
        
        sorted_types = sorted(incident_types.items(), key=lambda x: x[1], reverse=True)
        trend_text = "Top incident types: " + ", ".join(
            [f"{itype}({count})" for itype, count in sorted_types[:5]]
        )
        
        return trend_text
    
    @staticmethod
    def _find_hotspots(incidents: List[Dict[str, Any]]) -> str:
        """Identify incident hotspots."""
        locations = {}
        for incident in incidents:
            loc = incident.get('location', 'Unknown')
            locations[loc] = locations.get(loc, 0) + 1
        
        sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)
        hotspot_text = "Top locations: " + ", ".join(
            [f"{loc}({count})" for loc, count in sorted_locs[:5]]
        )
        
        return hotspot_text


# ============================================================================
# ANOMALY EXPLANATION
# ============================================================================

class AnomalyExplainer:
    """Explains detected anomalies in context."""
    
    def __init__(
        self,
        chain_manager: LLMChainManager,
        vector_store: Optional[VectorStore] = None,
    ):
        """Initialize anomaly explainer."""
        self.chain_manager = chain_manager
        self.vector_store = vector_store or get_vector_store()
    
    def explain_anomaly(
        self,
        anomaly_score: float,
        anomaly_type: str,
        affected_area: str,
        threshold: float = 0.7,
        comparisons: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Explain an anomaly detection.
        
        Args:
            anomaly_score: Score of detected anomaly
            anomaly_type: Type of anomaly
            affected_area: Location/area affected
            threshold: Anomaly threshold
            comparisons: Metric comparisons
        
        Returns:
            Explanation text
        """
        try:
            # Get historical context
            similar_incidents = self.vector_store.retrieve_similar_incidents(
                f"{anomaly_type} {affected_area}",
                top_k=3,
            )
            historical_context = format_incidents_for_context(similar_incidents)
            
            # Create anomaly context
            comparison_list = comparisons or []
            anomaly_context = create_anomaly_context(
                anomaly_score,
                threshold,
                comparison_list,
            )
            
            prompt = ANOMALY_EXPLANATION_TEMPLATE
            chain = self.chain_manager._get_or_create_chain(
                "anomaly_explainer",
                prompt,
            )
            
            explanation = chain.run(
                anomaly_description=f"{anomaly_type} (Score: {anomaly_score:.2f})\n{anomaly_context}",
                historical_context=historical_context,
                affected_area=affected_area,
            )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error explaining anomaly: {e}")
            return "Error explaining anomaly."
    
    def analyze_pattern(
        self,
        pattern_description: str,
        incidents: List[Dict[str, Any]],
        frequency: str = "recurring",
    ) -> str:
        """
        Analyze a detected pattern.
        
        Args:
            pattern_description: Description of pattern
            incidents: Related incidents
            frequency: Pattern frequency
        
        Returns:
            Pattern analysis
        """
        try:
            # Extract locations
            locations = set(i.get('location', 'Unknown') for i in incidents)
            locations_text = ", ".join(list(locations)[:5])
            
            incidents_text = format_incidents_for_context(incidents)
            
            prompt = PATTERN_ANALYSIS_TEMPLATE
            chain = self.chain_manager._get_or_create_chain(
                "pattern_analyzer",
                prompt,
            )
            
            analysis = chain.run(
                pattern_description=pattern_description,
                incidents_involved=incidents_text,
                frequency=frequency,
                locations=locations_text,
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing pattern: {e}")
            return "Error analyzing pattern."


# ============================================================================
# UNIFIED LLM SERVICE
# ============================================================================

class LLMService:
    """Unified service for all LLM operations."""
    
    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        vector_store: Optional[VectorStore] = None,
    ):
        """
        Initialize LLM service.
        
        Args:
            config: LLMConfig instance
            vector_store: Vector store for context
        """
        self.config = config or LLMConfig()
        self.chain_manager = LLMChainManager(self.config)
        self.vector_store = vector_store or get_vector_store()
        
        # Initialize components
        self.chat = MultiTurnChat(
            self.chain_manager,
            self.vector_store,
        )
        self.summarizer = IncidentSummarizer(self.chain_manager)
        self.reporter = ReportGenerator(self.chain_manager)
        self.explainer = AnomalyExplainer(self.chain_manager, self.vector_store)
    
    def update_config(self, config: LLMConfig):
        """Update LLM configuration."""
        self.config = config
        self.chain_manager.update_config(config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.to_dict()


# Create global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service(
    config: Optional[LLMConfig] = None,
    vector_store: Optional[VectorStore] = None,
) -> LLMService:
    """
    Get or create global LLM service.
    
    Args:
        config: Optional LLMConfig
        vector_store: Optional vector store
    
    Returns:
        LLMService instance
    """
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService(config, vector_store)
    
    return _llm_service


def reset_llm_service():
    """Reset global LLM service instance."""
    global _llm_service
    _llm_service = None
