"""
Reusable LLM prompt templates for CampusShield AI.

Includes templates for:
- Chat & FAQ
- Incident Summarization
- Report Generation
- Anomaly Explanation
"""

# Use langchain_core.prompts for LangChain 1.x compatibility
try:
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
except ImportError:
    # Fallback to old import path if available
    try:
        from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    except ImportError:
        raise ImportError("Cannot import PromptTemplate. Please ensure langchain-core is installed.")


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT_GENERAL = """You are CampusShield AI, an intelligent campus safety assistant designed to help administrators and students understand security incidents, anomalies, and safety patterns.

You are knowledgeable about:
- Campus security incident analysis
- Anomaly detection and pattern recognition
- Safety recommendations and best practices
- Historical incident data and trends

Provide clear, actionable, and contextual responses. When relevant, reference historical incidents and patterns.
Be empathetic when discussing sensitive security matters."""

SYSTEM_PROMPT_ANALYST = """You are a campus security analyst at CampusShield. Your role is to:
- Analyze incident patterns and trends
- Identify anomalies and potential security risks
- Generate comprehensive reports
- Provide actionable recommendations

Always base insights on data, maintain objectivity, and prioritize campus safety."""

SYSTEM_PROMPT_REPORTER = """You are a professional incident reporter. Your task is to:
- Generate clear, structured incident reports
- Summarize complex security data into digestible formats
- Highlight key metrics and actionable insights
- Maintain professional tone

Use clear language suitable for both technical and non-technical stakeholders."""


# ============================================================================
# CHAT & FAQ TEMPLATES
# ============================================================================

CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_GENERAL),
    HumanMessagePromptTemplate.from_template("{user_input}\n\nContext:\n{context}")
])

CONTEXTUAL_CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_GENERAL),
    HumanMessagePromptTemplate.from_template(
        "Chat History:\n{chat_history}\n\nCurrent Question: {user_input}\n\nRelevant Historical Incidents:\n{relevant_incidents}"
    )
])


# ============================================================================
# SUMMARIZATION TEMPLATES
# ============================================================================

SUMMARIZE_TEMPLATE = PromptTemplate(
    input_variables=["incidents_data"],
    template="""As a campus security analyst, summarize the following incidents concisely.

Incidents:
{incidents_data}

Provide:
1. Key Themes: Main patterns or types of incidents
2. Critical Issues: Any urgent or high-severity matters
3. Affected Areas: Locations or departments most impacted
4. Trend Analysis: Notable patterns or escalations
5. Recommendations: Top 3 actionable recommendations

Format your response clearly with sections."""
)

INCIDENT_SUMMARIZATION_PROMPT = """Summarize the following campus security incidents in a structured format:

{incident_logs}

Include:
- Total incidents and severity breakdown
- Most common incident types
- Key locations and times
- Trend observations
- Risk level assessment

Keep summary concise but comprehensive."""


# ============================================================================
# REPORT GENERATION TEMPLATES
# ============================================================================

DAILY_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["date", "incidents_count", "incidents_summary", "critical_events"],
    template="""Generate a professional daily security report for {date}.

Incident Summary:
- Total Incidents: {incidents_count}
- Overview: {incidents_summary}

Critical Events:
{critical_events}

Format as a professional report with sections:
1. Executive Summary
2. Incident Statistics
3. Critical Events & Response
4. Key Insights
5. Recommendations for Next Day

Keep the tone professional and suitable for campus administration."""
)

WEEKLY_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["week_dates", "total_incidents", "severity_breakdown", "trend_analysis", "hotspots"],
    template="""Generate a comprehensive weekly security report for {week_dates}.

Statistics:
- Total Incidents: {total_incidents}
- Severity Breakdown: {severity_breakdown}

Trend Analysis:
{trend_analysis}

Hotspots:
{hotspots}

Include:
1. Weekly Overview (statistics, trends)
2. High-Risk Areas & Times
3. Incident Type Analysis
4. Comparative Analysis (week-over-week)
5. Strategic Recommendations
6. Resource Allocation Suggestions

Make it actionable for decision-makers."""
)

INCIDENT_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["incident_data"],
    template="""Generate a detailed incident report based on:

{incident_data}

Include:
1. Incident Summary
2. Timeline of Events
3. Locations & Individuals Involved
4. Severity Assessment
5. Root Cause Analysis (if applicable)
6. Response & Actions Taken
7. Lessons Learned
8. Preventive Measures

Maintain professional and objective tone."""
)


# ============================================================================
# ANOMALY EXPLANATION TEMPLATES
# ============================================================================

ANOMALY_EXPLANATION_TEMPLATE = PromptTemplate(
    input_variables=["anomaly_description", "historical_context", "affected_area"],
    template="""Explain the following security anomaly detected by CampusShield AI:

Anomaly: {anomaly_description}
Location/Area: {affected_area}
Historical Context: {historical_context}

Provide:
1. What Was Detected: Clear explanation of the anomaly
2. Why It Matters: Significance and potential risks
3. Historical Precedent: Similar past incidents (if any)
4. Immediate Actions: Recommended responses
5. Preventive Measures: How to prevent recurrence
6. Risk Level: Assessment (Low/Medium/High/Critical)

Be precise and actionable."""
)

PATTERN_ANALYSIS_TEMPLATE = PromptTemplate(
    input_variables=["pattern_description", "incidents_involved", "frequency", "locations"],
    template="""Analyze the following detected security pattern:

Pattern: {pattern_description}
Frequency: {frequency}
Locations: {locations}
Related Incidents: {incidents_involved}

Provide:
1. Pattern Overview
2. Statistical Significance
3. Timeline Evolution
4. Geographical Distribution
5. Risk Assessment
6. Correlation with External Factors (if applicable)
7. Recommended Interventions

Structure your analysis for a security committee meeting."""
)


# ============================================================================
# HELPER FUNCTIONS FOR PROMPT CREATION
# ============================================================================

def create_chat_history_string(chat_history: list) -> str:
    """Convert chat history list to formatted string.
    
    Args:
        chat_history: List of {'role': 'user'|'assistant', 'content': str}
    
    Returns:
        Formatted chat history string
    """
    if not chat_history:
        return ""
    
    formatted = []
    for message in chat_history:
        role = message.get('role', 'Unknown').upper()
        content = message.get('content', '')
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)


def format_incidents_for_context(incidents: list) -> str:
    """Format incident list for LLM context.
    
    Args:
        incidents: List of incident dictionaries
    
    Returns:
        Formatted incident string
    """
    if not incidents:
        return "No relevant historical incidents found."
    
    formatted = []
    for idx, incident in enumerate(incidents, 1):
        incident_str = f"""
Incident #{idx}:
- Type: {incident.get('incident_type', 'Unknown')}
- Severity: {incident.get('severity', 'N/A')}
- Location: {incident.get('location', 'Unknown')}
- Timestamp: {incident.get('timestamp', 'Unknown')}
- Description: {incident.get('description', 'N/A')}
"""
        formatted.append(incident_str)
    
    return "\n".join(formatted)


def create_anomaly_context(anomaly_score: float, threshold: float, comparisons: list) -> str:
    """Create context string for anomaly explanations.
    
    Args:
        anomaly_score: Detected anomaly score (0-1)
        threshold: Threshold that triggered anomaly
        comparisons: List of comparison metrics
    
    Returns:
        Formatted anomaly context
    """
    context = f"""
Anomaly Score: {anomaly_score:.4f}
Threshold: {threshold:.4f}
Deviation: {((anomaly_score - threshold) / threshold * 100):.2f}%

Comparison Metrics:
"""
    for metric in comparisons:
        context += f"- {metric.get('name', 'Unknown')}: {metric.get('value', 'N/A')} (Normal: {metric.get('normal_range', 'N/A')})\n"
    
    return context
