"""
Pre-built analysis prompt templates for different document types.

Each document type has a set of analysis tasks with carefully crafted prompts
that instruct the LLM to extract specific information from the retrieved context.

All prompts enforce context-only answering and source citation.
"""

ANALYSIS_PROMPTS = {
    "contract": {
        "summary": {
            "label": "Summarize Contract",
            "icon": "FileText",
            "prompt": (
                "Provide a comprehensive summary of this contract. Include:\n"
                "- The parties involved\n"
                "- The purpose/subject of the contract\n"
                "- Key terms and conditions\n"
                "- Duration and effective dates\n"
                "- Financial terms (if any)\n"
                "Cite the specific pages and sections for each point."
            ),
        },
        "obligations": {
            "label": "Identify Obligations",
            "icon": "ListChecks",
            "prompt": (
                "List all obligations for each party mentioned in this contract. "
                "For each obligation, state:\n"
                "- Which party is responsible\n"
                "- What they must do\n"
                "- Any deadlines or conditions attached\n"
                "Cite the page and section for each obligation."
            ),
        },
        "deadlines": {
            "label": "Find Deadlines",
            "icon": "Calendar",
            "prompt": (
                "Identify ALL deadlines, due dates, time-sensitive clauses, and "
                "notice periods mentioned in this contract. For each deadline:\n"
                "- State the specific date or time period\n"
                "- Describe what action is required\n"
                "- Note any consequences for missing the deadline\n"
                "Cite the page and section for each deadline."
            ),
        },
        "termination": {
            "label": "Termination Clauses",
            "icon": "XCircle",
            "prompt": (
                "Identify all termination clauses and conditions in this contract. "
                "For each, explain:\n"
                "- Under what circumstances the contract can be terminated\n"
                "- Required notice periods\n"
                "- Consequences of termination\n"
                "- Any post-termination obligations\n"
                "Cite the page and section for each clause."
            ),
        },
        "penalties": {
            "label": "Penalties & Remedies",
            "icon": "AlertTriangle",
            "prompt": (
                "List all penalties, liquidated damages, indemnification clauses, "
                "and remedies described in this contract. For each:\n"
                "- State the trigger condition\n"
                "- The amount or type of penalty\n"
                "- Any caps or limitations\n"
                "Cite the page and section for each penalty."
            ),
        },
        "renewal": {
            "label": "Renewal Conditions",
            "icon": "RefreshCw",
            "prompt": (
                "Identify all renewal conditions in this contract, including:\n"
                "- Auto-renewal clauses and their terms\n"
                "- Opt-out or cancellation procedures\n"
                "- Required notice periods for non-renewal\n"
                "- Any changes in terms upon renewal\n"
                "Cite the page and section for each condition."
            ),
        },
    },
    "financial": {
        "summary": {
            "label": "Financial Summary",
            "icon": "FileText",
            "prompt": (
                "Provide a comprehensive summary of this financial document. "
                "Include the key takeaways, overall financial health indicators, "
                "and any notable items. Cite pages for each point."
            ),
        },
        "metrics": {
            "label": "Key Metrics",
            "icon": "BarChart3",
            "prompt": (
                "Extract all key financial figures, ratios, and KPIs from this "
                "document. Present them in a structured format with:\n"
                "- Metric name\n"
                "- Value\n"
                "- Period (if applicable)\n"
                "- Comparison to previous period (if available)\n"
                "Cite the page for each metric."
            ),
        },
        "risks": {
            "label": "Risk Factors",
            "icon": "AlertTriangle",
            "prompt": (
                "Identify all risk factors, warnings, and potential concerns "
                "mentioned in this financial document. For each risk:\n"
                "- Describe the risk\n"
                "- Assess its potential impact (if stated)\n"
                "- Note any mitigation strategies mentioned\n"
                "Cite the page for each risk factor."
            ),
        },
        "trends": {
            "label": "Trends & Projections",
            "icon": "TrendingUp",
            "prompt": (
                "Identify trends, year-over-year changes, and projections "
                "mentioned in this document. For each trend:\n"
                "- Describe the trend direction\n"
                "- Provide the specific figures\n"
                "- Note any explanations given for the trend\n"
                "Cite the page for each trend."
            ),
        },
    },
    "compliance": {
        "summary": {
            "label": "Compliance Summary",
            "icon": "FileText",
            "prompt": (
                "Summarize the compliance requirements and obligations "
                "described in this document. Include the regulatory framework, "
                "key requirements, and overall compliance status. Cite pages."
            ),
        },
        "requirements": {
            "label": "Requirements List",
            "icon": "ListChecks",
            "prompt": (
                "List all regulatory requirements and compliance obligations "
                "described in this document. For each requirement:\n"
                "- State the regulation or standard referenced\n"
                "- Describe the specific requirement\n"
                "- Note the compliance status (if indicated)\n"
                "Cite the page and section for each requirement."
            ),
        },
        "deadlines": {
            "label": "Compliance Deadlines",
            "icon": "Calendar",
            "prompt": (
                "Identify all compliance deadlines, reporting periods, and "
                "filing dates mentioned in this document. For each:\n"
                "- State the specific date or period\n"
                "- Describe the required action\n"
                "- Note any penalties for non-compliance\n"
                "Cite the page for each deadline."
            ),
        },
        "violations": {
            "label": "Issues & Violations",
            "icon": "XCircle",
            "prompt": (
                "Identify any noted violations, deficiencies, findings, or "
                "areas of concern mentioned in this document. For each:\n"
                "- Describe the issue\n"
                "- State the severity (if indicated)\n"
                "- Note any required corrective actions\n"
                "Cite the page for each issue."
            ),
        },
    },
    "medical": {
        "summary": {
            "label": "Report Summary",
            "icon": "FileText",
            "prompt": (
                "Summarize the key findings and observations in this medical "
                "report. Note: This is for document analysis only, not medical "
                "advice. Cite the pages for each finding."
            ),
        },
        "findings": {
            "label": "Key Findings",
            "icon": "Search",
            "prompt": (
                "List all findings, measurements, test results, and "
                "observations documented in this report. For each:\n"
                "- State the finding or measurement\n"
                "- Note any reference ranges (if provided)\n"
                "- Flag any abnormal results (if indicated)\n"
                "Note: This is for document analysis only, not medical advice. "
                "Cite the page for each finding."
            ),
        },
        "recommendations": {
            "label": "Recommendations",
            "icon": "ClipboardList",
            "prompt": (
                "Identify all recommendations, follow-up actions, and next "
                "steps documented in this report. For each:\n"
                "- State the recommendation\n"
                "- Note any timeframes mentioned\n"
                "- Note the priority (if indicated)\n"
                "Note: This is for document analysis only, not medical advice. "
                "Cite the page for each recommendation."
            ),
        },
    },
    "general": {
        "summary": {
            "label": "Document Summary",
            "icon": "FileText",
            "prompt": (
                "Provide a comprehensive summary of this document. Cover:\n"
                "- The main purpose and subject matter\n"
                "- Key points and conclusions\n"
                "- Important details and figures\n"
                "- Any action items or recommendations\n"
                "Cite the page for each point."
            ),
        },
        "key_points": {
            "label": "Key Points",
            "icon": "List",
            "prompt": (
                "List the most important points from this document in order "
                "of significance. For each point, provide a brief explanation "
                "and cite the page where it appears."
            ),
        },
    },
}


def get_analysis_prompt(document_type: str, analysis_type: str) -> str | None:
    """Get the analysis prompt for a given document type and analysis type.
    
    Returns None if the combination is not found.
    """
    doc_prompts = ANALYSIS_PROMPTS.get(document_type, {})
    analysis = doc_prompts.get(analysis_type)
    if analysis:
        return analysis["prompt"]
    return None


def get_available_analyses(document_type: str) -> list[dict]:
    """Get the list of available analysis types for a given document type.
    
    Returns a list of dicts with 'type', 'label', and 'icon' keys.
    """
    doc_prompts = ANALYSIS_PROMPTS.get(document_type, ANALYSIS_PROMPTS["general"])
    return [
        {"type": key, "label": val["label"], "icon": val["icon"]}
        for key, val in doc_prompts.items()
    ]
