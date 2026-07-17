"""
Recommendation engine for Smart Resume Screener.
Generates hiring recommendations based on ATS scores.
"""


def get_recommendation(ats_score: float) -> str:
    """
    Map ATS score to a hiring recommendation category.
    Highly Recommended: >= 80, Recommended: >= 65,
    Needs Improvement: >= 45, Rejected: < 45.
    """
    if ats_score >= 80:
        return "Highly Recommended"
    if ats_score >= 65:
        return "Recommended"
    if ats_score >= 45:
        return "Needs Improvement"
    return "Rejected"


def get_recommendation_details(ats_score: float) -> dict:
    """Return recommendation label with explanation and action items."""
    recommendation = get_recommendation(ats_score)

    details = {
        "Highly Recommended": {
            "label": "Highly Recommended",
            "icon": "🌟",
            "color": "#00C853",
            "summary": "Excellent match for the role. Strong skills and experience alignment.",
            "action": "Schedule interview immediately. Priority candidate.",
        },
        "Recommended": {
            "label": "Recommended",
            "icon": "✅",
            "color": "#69F0AE",
            "summary": "Good match with minor gaps. Worth interviewing.",
            "action": "Proceed to technical screening or phone interview.",
        },
        "Needs Improvement": {
            "label": "Needs Improvement",
            "icon": "⚠️",
            "color": "#FFD600",
            "summary": "Partial match. Missing key skills or experience.",
            "action": "Consider for junior role or request skill assessment.",
        },
        "Rejected": {
            "label": "Rejected",
            "icon": "❌",
            "color": "#FF1744",
            "summary": "Poor match for this role. Significant skill gaps.",
            "action": "Do not proceed. Consider for alternative positions.",
        },
    }

    return details.get(recommendation, details["Needs Improvement"])
