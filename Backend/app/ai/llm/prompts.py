"""
Reusable LLM prompt templates for CampusShield AI.
"""
from typing import List, Dict, Any


# System Prompts
SYSTEM_PROMPT_GENERAL = """You are CampusShield AI, an intelligent campus safety assistant.
You help administrators understand security incidents, patterns, and provide actionable recommendations.
Be clear, professional, and prioritize campus safety."""

SYSTEM_PROMPT_ANALYST = """You are a campus security analyst. Analyze incidents, identify patterns,
provide root cause analysis, and recommend actions. Base insights on data and maintain objectivity."""

SYSTEM_PROMPT_POLICY = """You are a policy compliance agent. Check incidents against campus security policies,
identify violations, and recommend corrective actions based on established rules."""

SYSTEM_PROMPT_FORECASTING = """You are a risk forecasting agent. Analyze historical patterns to predict
future risks, explain predictions clearly, and provide actionable prevention strategies."""

SYSTEM_PROMPT_REPORTER = """You are a professional incident reporter. Generate clear, structured reports
suitable for both technical and non-technical stakeholders."""


# Incident Analysis Prompts
INCIDENT_ANALYSIS_PROMPT = """Analyze the following incident and provide:

1. Severity Classification: Low / Medium / High / Critical
2. Root Cause Inference: What likely caused this incident?
3. Pattern Matching: Similar historical incidents (if any)
4. Recommended Actions: Immediate and preventive measures
5. Confidence Score: 0.0 to 1.0

Incident Data:
{incident_data}

Historical Context:
{historical_context}

Provide structured JSON response."""


# RAG QA Prompts
RAG_QA_SYSTEM = """You are CampusShield AI answering questions about campus security.
You MUST only use information from the provided context. If the context doesn't contain
enough information, say "Insufficient data to provide a reliable answer."
Always cite your sources."""

RAG_QA_PROMPT = """Context from CampusShield AI knowledge base:
{context}

Question: {question}

Answer the question using ONLY the provided context. Cite sources. If context is insufficient, say so."""


# Risk Forecasting Prompts
RISK_FORECAST_PROMPT = """Based on historical incident data, predict future risks:

Historical Data:
{historical_data}

Zones Analyzed: {zones}
Time Range: {time_range}

Provide:
1. Zone-wise risk predictions (probability scores)
2. Time-based patterns
3. Hotspot identification
4. Natural language explanation of predictions
5. Confidence levels"""


# Report Generation
INCIDENT_REPORT_PROMPT = """Generate a professional incident report:

Incident: {incident_data}
Analysis: {analysis}

Include:
1. Executive Summary
2. Incident Details
3. Analysis & Root Cause
4. Recommendations
5. Conclusion"""

