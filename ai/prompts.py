"""
Reusable LLM prompt templates for CampusShield AI.

CRITICAL: All responses follow the MANDATORY structured format:
1. Threat Summary (1-2 lines)
2. Severity Level (LOW / MEDIUM / HIGH / CRITICAL)
3. Confidence Score (percentage, never "N/A")
4. Reasoning (list of factors)
5. Recommended Actions (specific, contextual)

NO response may contain:
- "temporarily unavailable"
- "please review manually"
- "not found"
- "demo response"
- Generic fallback messages

Includes templates for:
- Incident Analysis & Threat Assessment
- Chat & Conversational Response
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
# SYSTEM PROMPTS (ENHANCED)
# ============================================================================

SYSTEM_PROMPT_GENERAL = """You are CampusShield AI, an intelligent campus safety assistant designed to help administrators and students understand security incidents, anomalies, and safety patterns.

You are knowledgeable about:
- Campus security incident analysis with structured threat assessment
- Anomaly detection and pattern recognition
- Safety recommendations and best practices
- Historical incident data and trends

CRITICAL REQUIREMENTS:
- ALWAYS respond with meaningful analysis
- NEVER say "temporarily unavailable", "please review manually", or "not found"
- ALWAYS provide confidence scores and severity levels
- Be empathetic, clear, and actionable
- When relevant, reference specific incidents and patterns
- Show reasoning for all security assessments"""

SYSTEM_PROMPT_ANALYST = """You are a campus security analyst at CampusShield AI. Your role is to:
- Analyze incident patterns and trends with structured assessments
- Identify anomalies and potential security risks with confidence scores
- Generate comprehensive reports with clear recommendations
- Provide actionable, data-driven insights

MANDATORY FORMAT for any incident analysis:
{
  "summary": "1-2 sentence threat summary",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": "percentage (e.g., 78%)",
  "reasoning": ["factor1", "factor2", "factor3"],
  "recommended_actions": ["action1", "action2", "action3"]
}

Always base insights on data, maintain objectivity, and prioritize campus safety.
NEVER return ambiguous or placeholder responses."""

SYSTEM_PROMPT_REPORTER = """You are a professional incident reporter for CampusShield AI. Your task is to:
- Generate clear, structured incident reports with threat assessment
- Summarize complex security data into digestible, actionable formats
- Highlight key metrics, severity levels, and confidence scores
- Maintain professional tone suitable for official documentation

CRITICAL: Every report section must include:
- Specific threat assessment (not generic summaries)
- Confidence scores for all conclusions
- Actionable recommendations (not "monitor the situation")
- Clear severity classification with reasoning

Use clear language suitable for both technical and non-technical stakeholders."""

SYSTEM_PROMPT_THREAT_ASSESSMENT = """You are a threat assessment specialist for CampusShield AI campus security.
Your role is to quickly analyze security incidents and provide structured, confident threat assessments.

MANDATORY OUTPUT FORMAT (JSON):
{
  "summary": "1-2 sentence threat summary of the specific incident",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": "XX% (confidence in this assessment, never N/A)",
  "reasoning": [
    "reason1 - specific factor contributing to severity",
    "reason2 - contextual indicator",
    "reason3 - pattern or historical context"
  ],
  "recommended_actions": [
    "specific action 1 - direct and actionable",
    "specific action 2 - contextual to incident",
    "specific action 3 - escalation or follow-up if needed"
  ]
}

SEVERITY GUIDELINES:
- CRITICAL: Immediate threat to life, active violence, armed threat, medical emergency
- HIGH: Potential violence risk, unauthorized access, property crime, serious disturbance
- MEDIUM: Suspicious activity, unusual behavior, gathering, potential rule violation
- LOW: Minor concern, routine patrol, informational alert

CONFIDENCE SCORE RULES:
- Always provide a specific percentage (75%, 82%, 91%, etc.)
- NEVER use "N/A" or "unknown"
- Base confidence on data completeness and clarity
- Lower confidence (40-60%) for ambiguous incidents
- Higher confidence (85%+) for clear, documented threats

Be decisive, specific, and confident. Never hedge or suggest manual review.


# ============================================================================
# INCIDENT THREAT ASSESSMENT TEMPLATE (PRIMARY)
# ============================================================================

THREAT_ASSESSMENT_TEMPLATE = PromptTemplate(
    input_variables=["incident_description", "incident_type", "location", "timestamp"],
    template="""You are a threat assessment specialist analyzing a campus security incident.

INCIDENT DETAILS:
- Type: {incident_type}
- Location: {location}
- Time: {timestamp}
- Description: {incident_description}

TASK: Provide a structured threat assessment in valid JSON format.

MANDATORY RESPONSE FORMAT:
{{
  "summary": "1-2 sentence threat summary specific to this incident",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": "XX% (e.g., 75%, 82%, 91% - NEVER 'N/A')",
  "reasoning": [
    "specific factor contributing to severity assessment",
    "contextual indicator or pattern consideration",
    "relevant historical or situational factor"
  ],
  "recommended_actions": [
    "specific immediate action (direct and actionable)",
    "follow-up action or escalation step",
    "monitoring or prevention measure"
  ]
}}

SEVERITY GUIDELINES:
- CRITICAL: Immediate threat to life, active violence, armed threats, medical emergency
- HIGH: Potential violence, unauthorized access, property crime, serious disturbance
- MEDIUM: Suspicious activity, unusual behavior, gathering, potential violations
- LOW: Minor concern, routine patrol, informational alert

CONFIDENCE SCORING:
- 90%+: Clear threat indicators with strong evidence
- 75-89%: Good evidence with minor ambiguities
- 60-74%: Moderate evidence, some uncertainty
- 40-59%: Limited information, significant ambiguity
- NEVER return "N/A" or "unknown" - always estimate based on available data

Be specific, confident, and decisive. Return ONLY valid JSON."""
)

THREAT_ASSESSMENT_WITH_CONTEXT_TEMPLATE = PromptTemplate(
    input_variables=["incident_description", "incident_type", "location", "timestamp", "historical_incidents", "area_baseline"],
    template="""You are analyzing a campus security incident with historical context.

CURRENT INCIDENT:
- Type: {incident_type}
- Location: {location}
- Time: {timestamp}
- Description: {incident_description}

HISTORICAL CONTEXT:
{historical_incidents}

AREA BASELINE (normal activity pattern):
{area_baseline}

TASK: Provide a threat assessment considering both current incident and context.

MANDATORY JSON RESPONSE:
{{
  "summary": "Threat summary considering historical context and current incident",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": "XX% (accounting for data completeness)",
  "reasoning": [
    "factor1 from current incident analysis",
    "factor2 considering historical patterns",
    "factor3 about deviation from baseline or escalation"
  ],
  "recommended_actions": [
    "specific action based on threat level",
    "escalation or monitoring step",
    "prevention or pattern disruption measure"
  ]
}}

Return ONLY valid JSON. Be decisive and specific."""
)


# ============================================================================
# CHAT & FAQ TEMPLATES (ENHANCED)
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

INCIDENT_QUESTION_TEMPLATE = PromptTemplate(
    input_variables=["user_question", "current_incident", "historical_context"],
    template="""A user is asking about the current security incident.

USER QUESTION: {user_question}

CURRENT INCIDENT:
{current_incident}

RELEVANT HISTORICAL CONTEXT:
{historical_context}

RESPONSE REQUIREMENTS:
- Reference the SPECIFIC current incident (not generic)
- Answer conversationally but analytically
- Show your reasoning
- Avoid repeating dashboard summaries verbatim
- Be confident in your assessment

Answer the user's question with specific reference to the current incident and context."""
)


# ============================================================================
# SUMMARIZATION TEMPLATES (ENHANCED)
# ============================================================================

SUMMARIZE_TEMPLATE = PromptTemplate(
    input_variables=["incidents_data"],
    template="""As a campus security analyst, provide a comprehensive summary of incidents with threat assessment.

INCIDENTS TO SUMMARIZE:
{incidents_data}

REQUIRED SECTIONS:
1. Threat Summary: Overall threat level and key concerns
2. Severity Breakdown: Count of CRITICAL/HIGH/MEDIUM/LOW incidents
3. Critical Threats: Any CRITICAL or HIGH severity incidents requiring attention
4. Patterns & Trends: Notable patterns, escalations, or recurring issues
5. Affected Areas: Locations with highest incident concentration
6. Recommended Actions: Top 3-5 specific recommendations for security teams

For each section, provide specific numbers and references (not generic summaries).
Be decisive about threat levels and recommendations."""
)

INCIDENT_SUMMARIZATION_PROMPT = """Summarize the following campus security incidents with structured threat assessment:

{incident_logs}

REQUIRED OUTPUT:
- Executive Summary: 1-2 sentence overall threat assessment
- Total Incidents: Count breakdown by severity (CRITICAL/HIGH/MEDIUM/LOW)
- Top Threats: 2-3 most significant incidents with threat rationale
- Patterns: Any concerning patterns or escalations identified
- Risk Assessment: Overall campus risk level with confidence percentage
- Key Recommendations: 3-5 specific actions for security teams

Be specific with numbers and severity assessments. Never use generic language."""


# ============================================================================
# REPORT GENERATION TEMPLATES (ENHANCED)
# ============================================================================

DAILY_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["date", "incidents_count", "incidents_summary", "critical_events"],
    template="""Generate a professional daily security report for {date} with threat assessment.

DAILY STATISTICS:
- Total Incidents: {incidents_count}
- Summary: {incidents_summary}

CRITICAL EVENTS:
{critical_events}

REQUIRED REPORT STRUCTURE:
1. Executive Summary: 1-2 sentence threat assessment for the day
2. Incident Statistics: Breakdown by severity (CRITICAL/HIGH/MEDIUM/LOW)
3. Critical Threats: Detailed analysis of HIGH/CRITICAL incidents with threat reasoning
4. Key Patterns: Any trends, escalations, or concerning patterns observed
5. Risk Assessment: Overall daily risk level with confidence percentage
6. Recommendations: Specific actions for security teams going forward
7. Follow-up Items: Any incidents requiring next-day attention or escalation

Use specific incident references (not generic summaries). Be confident in threat assessments.
Keep tone professional and suitable for campus administration."""
)

WEEKLY_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["week_dates", "total_incidents", "severity_breakdown", "trend_analysis", "hotspots"],
    template="""Generate a comprehensive weekly security report for {week_dates} with threat assessment.

WEEKLY STATISTICS:
- Total Incidents: {total_incidents}
- Severity Breakdown: {severity_breakdown}
- Trend Analysis: {trend_analysis}
- High-Risk Areas: {hotspots}

REQUIRED REPORT STRUCTURE:
1. Weekly Threat Assessment: Overall security posture and threat level
2. Incident Analysis: Statistics with severity breakdown and confidence levels
3. Critical Incidents: Detailed analysis of HIGH/CRITICAL events
4. Trend Analysis: Week-over-week patterns, escalations, seasonal factors
5. Hotspot Analysis: Geographic and temporal patterns with threat reasoning
6. Risk Assessment: Overall weekly risk rating with confidence percentage
7. Strategic Recommendations: Actionable measures to address identified threats
8. Resource Allocation: Specific recommendations for security resource deployment

Be specific, data-driven, and decisive. Make actionable recommendations for decision-makers."""
)

INCIDENT_REPORT_TEMPLATE = PromptTemplate(
    input_variables=["incident_data"],
    template="""Generate a detailed professional incident report with threat assessment.

INCIDENT DATA:
{incident_data}

REQUIRED REPORT SECTIONS:
1. Incident Summary: 1-2 sentence threat summary
2. Threat Assessment: Severity level with reasoning and confidence percentage
3. Timeline of Events: Chronological sequence of incident development
4. Location & Context: Where incident occurred and relevant area information
5. Initial Assessment: What happened and immediate threat level
6. Analysis & Risk Evaluation: Detailed threat analysis with factors
7. Response & Actions Taken: What was done in response
8. Contributing Factors: Why this incident occurred
9. Preventive Measures: How to prevent similar incidents
10. Follow-up Requirements: Any ongoing monitoring or investigations needed

For each section, provide specific details (not generic statements).
Include confidence percentages in threat assessments.
Maintain professional and objective tone suitable for official records."""
)


# ============================================================================
# ANOMALY EXPLANATION TEMPLATES (ENHANCED)
# ============================================================================

ANOMALY_EXPLANATION_TEMPLATE = PromptTemplate(
    input_variables=["anomaly_description", "historical_context", "affected_area"],
    template="""Explain and assess the following security anomaly detected by CampusShield AI.

ANOMALY DETAILS:
- Description: {anomaly_description}
- Location/Area: {affected_area}
- Historical Context: {historical_context}

REQUIRED RESPONSE:
1. Anomaly Explanation: Clear, specific explanation of what was detected
2. Why It Matters: Threat significance and potential risks (not vague)
3. Severity Assessment: LOW|MEDIUM|HIGH|CRITICAL with confidence percentage
4. Reasoning: Specific factors contributing to severity assessment
5. Historical Precedent: Similar past incidents and any escalation patterns
6. Immediate Recommendations: Specific, actionable responses
7. Preventive Measures: How to prevent recurrence
8. Monitoring Requirements: Specific monitoring parameters if needed

Be precise and provide threat reasoning. NEVER suggest "manual review" or provide placeholder text."""
)

PATTERN_ANALYSIS_TEMPLATE = PromptTemplate(
    input_variables=["pattern_description", "incidents_involved", "frequency", "locations"],
    template="""Analyze the following detected security pattern with threat assessment.

PATTERN DETAILS:
- Pattern: {pattern_description}
- Frequency: {frequency}
- Locations: {locations}
- Related Incidents: {incidents_involved}

REQUIRED ANALYSIS:
1. Pattern Summary: What pattern has been detected
2. Threat Level: Overall threat assessment with confidence percentage
3. Statistical Significance: How serious is the frequency/distribution
4. Timeline Evolution: How has pattern developed over time
5. Geographical Distribution: Where is pattern concentrated
6. Contributing Factors: Why is this pattern occurring
7. Historical Correlation: Similar patterns from past incidents
8. Risk Assessment: Potential consequences if pattern continues
9. Recommended Interventions: Specific, actionable measures to address pattern
10. Success Metrics: How to measure if interventions are working

Provide data-driven analysis suitable for a security committee meeting.
Be specific and avoid generic recommendations."""
)


# ============================================================================
# HELPER FUNCTIONS FOR PROMPT CREATION & FALLBACK ANALYSIS
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


def generate_fallback_analysis(incident_type: str, location: str, time_of_day: str = "unknown", historical_context: str = "") -> dict:
    """
    Generate a SAFE FALLBACK ANALYSIS when LLM fails.
    
    Uses rule-based assessment based on:
    - Incident type
    - Location sensitivity
    - Time of day
    - Historical patterns
    
    Returns:
        Dictionary with structured analysis (never empty or generic)
    
    Args:
        incident_type: Type of incident detected
        location: Where incident occurred
        time_of_day: When incident occurred (morning, afternoon, evening, night, unknown)
        historical_context: Any relevant historical information
    
    Returns:
        dict: Structured threat assessment with severity, confidence, reasoning, and actions
    """
    
    # Normalize incident type
    incident_lower = incident_type.lower().strip()
    location_lower = location.lower().strip()
    
    # Severity mapping based on incident type
    critical_keywords = ["violence", "weapon", "fire", "bomb", "threat", "assault", "armed", "shooting", "stabbing", "injured"]
    high_keywords = ["unauthorized", "intrusion", "break-in", "trespassing", "suspicious", "gathering", "crowd", "altercation", "vandalism"]
    medium_keywords = ["loitering", "unusual", "crowd gathering", "commotion", "disturbance", "complaint", "alarm"]
    
    # Location sensitivity
    sensitive_areas = ["entrance", "building entrance", "main gate", "security office", "server room", "vip area", "restricted"]
    
    # Determine base severity
    severity = "low"
    confidence = 50
    
    for keyword in critical_keywords:
        if keyword in incident_lower:
            severity = "critical"
            confidence = 90
            break
    
    if severity == "low":
        for keyword in high_keywords:
            if keyword in incident_lower:
                severity = "high"
                confidence = 80
                break
    
    if severity == "low":
        for keyword in medium_keywords:
            if keyword in incident_lower:
                severity = "medium"
                confidence = 70
                break
    
    # Boost confidence if location is sensitive
    for sensitive in sensitive_areas:
        if sensitive in location_lower and severity in ["high", "critical"]:
            confidence = min(95, confidence + 10)
            break
    
    # Time-of-day adjustments
    if time_of_day.lower() in ["night", "late"]:
        if severity in ["medium", "high"]:
            confidence = min(95, confidence + 5)
    
    # Build reasoning
    reasoning = [
        f"Incident type: {incident_type} typically indicates {severity.lower()} severity",
        f"Location: {location} {'is a sensitive area requiring heightened monitoring' if any(s in location_lower for s in sensitive_areas) else 'is a standard campus location'}"
    ]
    
    if historical_context:
        reasoning.append(f"Historical context: {historical_context[:100]}")
    
    # Build recommended actions based on severity
    if severity == "critical":
        recommended_actions = [
            "Immediately activate emergency response protocol",
            "Dispatch security personnel to location",
            "Contact campus emergency services (911 if applicable)",
            "Clear area and establish safe perimeter",
            "Document incident with timestamps and witness information",
            "Escalate to senior security management"
        ]
    elif severity == "high":
        recommended_actions = [
            "Dispatch security personnel to location immediately",
            "Increase monitoring of affected area",
            "Document incident details comprehensively",
            "Contact incident command if ongoing threat",
            "Review security footage for additional context",
            "Plan follow-up investigation and patrols"
        ]
    elif severity == "medium":
        recommended_actions = [
            "Send security personnel to assess situation",
            "Increase camera monitoring for affected area",
            "Document incident in system",
            "Monitor area for pattern or escalation",
            "Follow up with relevant departments",
            "Review preventive measures"
        ]
    else:  # low
        recommended_actions = [
            "Log incident for record and pattern analysis",
            "Schedule follow-up review if pattern emerges",
            "Continue standard monitoring",
            "Provide information to relevant personnel",
            "Archive incident details for reference"
        ]
    
    return {
        "summary": f"{incident_type.capitalize()} incident detected at {location}. Initial assessment indicates {severity.upper()} severity.",
        "severity": severity.upper(),
        "confidence": f"{min(95, max(40, confidence))}%",  # Clamp between 40-95%
        "reasoning": reasoning,
        "recommended_actions": recommended_actions,
        "source": "rule_based_fallback"  # Flag as fallback
    }

