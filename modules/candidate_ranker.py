"""
Candidate ranking module for Smart Resume Screener.
Ranks candidates by ATS score and composite metrics.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from modules.recommendation import get_recommendation


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank candidates by ATS score in descending order.
    Assigns rank number and ensures recommendation is set.
    """
    if not candidates:
        return []

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (
            c.get("ats_score", 0),
            c.get("skill_match", 0),
            c.get("total_experience", 0),
        ),
        reverse=True,
    )

    ranked = []
    for idx, candidate in enumerate(sorted_candidates, start=1):
        entry = dict(candidate)
        entry["rank"] = idx
        if not entry.get("recommendation"):
            entry["recommendation"] = get_recommendation(entry.get("ats_score", 0))
        ranked.append(entry)

    return ranked


def candidates_to_dataframe(candidates: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert ranked candidate list to a pandas DataFrame for display."""
    if not candidates:
        return pd.DataFrame()

    ranked = rank_candidates(candidates)
    rows = []

    for c in ranked:
        rows.append({
            "Rank": c.get("rank", 0),
            "Name": c.get("name", "Unknown"),
            "Email": c.get("email", ""),
            "ATS Score": c.get("ats_score", 0),
            "Skill Match %": c.get("skill_match", 0),
            "Experience (Yrs)": c.get("total_experience", 0),
            "Recommendation": c.get("recommendation", ""),
            "Keywords Match %": c.get("keyword_match", 0),
            "Semantic Score": c.get("semantic_score", 0),
        })

    return pd.DataFrame(rows)


def get_top_candidates(
    candidates: List[Dict[str, Any]],
    n: int = 5,
) -> List[Dict[str, Any]]:
    """Return top N candidates by ATS score."""
    ranked = rank_candidates(candidates)
    return ranked[:n]


def filter_by_recommendation(
    candidates: List[Dict[str, Any]],
    recommendation: str,
) -> List[Dict[str, Any]]:
    """Filter candidates by recommendation category."""
    return [
        c for c in candidates
        if c.get("recommendation", "").lower() == recommendation.lower()
    ]


def get_ranking_summary(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for the candidate pool."""
    if not candidates:
        return {
            "total": 0,
            "avg_score": 0,
            "max_score": 0,
            "min_score": 0,
            "highly_recommended": 0,
            "recommended": 0,
            "needs_improvement": 0,
            "rejected": 0,
        }

    scores = [c.get("ats_score", 0) for c in candidates]
    rec_counts = {"Highly Recommended": 0, "Recommended": 0,
                  "Needs Improvement": 0, "Rejected": 0}

    for c in candidates:
        rec = c.get("recommendation", "Needs Improvement")
        if rec in rec_counts:
            rec_counts[rec] += 1

    return {
        "total": len(candidates),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": round(max(scores), 2),
        "min_score": round(min(scores), 2),
        "highly_recommended": rec_counts["Highly Recommended"],
        "recommended": rec_counts["Recommended"],
        "needs_improvement": rec_counts["Needs Improvement"],
        "rejected": rec_counts["Rejected"],
    }
