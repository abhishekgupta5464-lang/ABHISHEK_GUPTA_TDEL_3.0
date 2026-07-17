"""
Analytics module for Smart Resume Screener.
Computes aggregate statistics and data for dashboard visualizations.
"""

from collections import Counter
from typing import Any, Dict, List

import numpy as np

from modules.candidate_ranker import get_ranking_summary, rank_candidates


def compute_skill_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count frequency of each skill across all candidates."""
    skill_counter: Counter = Counter()
    for candidate in candidates:
        for skill in candidate.get("skills", []):
            skill_counter[skill.lower()] += 1
    return dict(skill_counter.most_common(20))


def compute_score_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Bucket ATS scores into ranges for histogram display."""
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}

    for candidate in candidates:
        score = candidate.get("ats_score", 0)
        if score <= 20:
            buckets["0-20"] += 1
        elif score <= 40:
            buckets["21-40"] += 1
        elif score <= 60:
            buckets["41-60"] += 1
        elif score <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    return buckets


def compute_recommendation_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count candidates in each recommendation category."""
    counts = {
        "Highly Recommended": 0,
        "Recommended": 0,
        "Needs Improvement": 0,
        "Rejected": 0,
    }
    for candidate in candidates:
        rec = candidate.get("recommendation", "Needs Improvement")
        if rec in counts:
            counts[rec] += 1
    return counts


def compute_experience_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Bucket candidates by years of experience."""
    buckets = {"0-1 yrs": 0, "1-3 yrs": 0, "3-5 yrs": 0, "5-8 yrs": 0, "8+ yrs": 0}

    for candidate in candidates:
        exp = candidate.get("total_experience", 0)
        if exp <= 1:
            buckets["0-1 yrs"] += 1
        elif exp <= 3:
            buckets["1-3 yrs"] += 1
        elif exp <= 5:
            buckets["3-5 yrs"] += 1
        elif exp <= 8:
            buckets["5-8 yrs"] += 1
        else:
            buckets["8+ yrs"] += 1

    return buckets


def get_top_skills(candidates: List[Dict[str, Any]], n: int = 10) -> List[tuple]:
    """Return top N most common skills across candidates."""
    distribution = compute_skill_distribution(candidates)
    return list(distribution.items())[:n]


def get_candidate_score_breakdown(candidate: Dict[str, Any]) -> Dict[str, float]:
    """Return score component breakdown for radar chart."""
    return {
        "Skill Match": candidate.get("skill_match", 0),
        "Experience": candidate.get("experience_score", 0),
        "Education": candidate.get("education_score", 0),
        "Projects": candidate.get("projects_score", 0),
        "Certifications": candidate.get("certifications_score", 0),
        "Resume Quality": candidate.get("resume_quality_score", 0),
    }


def compute_dashboard_metrics(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute all key metrics for the main dashboard."""
    summary = get_ranking_summary(candidates)
    ranked = rank_candidates(candidates)

    return {
        "total_candidates": summary["total"],
        "average_ats_score": summary["avg_score"],
        "highest_score": summary["max_score"],
        "lowest_score": summary["min_score"],
        "highly_recommended": summary["highly_recommended"],
        "recommended": summary["recommended"],
        "needs_improvement": summary["needs_improvement"],
        "rejected": summary["rejected"],
        "top_candidates": ranked[:5],
        "score_distribution": compute_score_distribution(candidates),
        "skill_distribution": compute_skill_distribution(candidates),
        "recommendation_distribution": compute_recommendation_distribution(candidates),
        "experience_distribution": compute_experience_distribution(candidates),
    }


def compute_match_analytics(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute average match metrics across all candidates."""
    if not candidates:
        return {
            "avg_skill_match": 0,
            "avg_keyword_match": 0,
            "avg_semantic_score": 0,
        }

    n = len(candidates)
    return {
        "avg_skill_match": round(
            sum(c.get("skill_match", 0) for c in candidates) / n, 2
        ),
        "avg_keyword_match": round(
            sum(c.get("keyword_match", 0) for c in candidates) / n, 2
        ),
        "avg_semantic_score": round(
            sum(c.get("semantic_score", 0) for c in candidates) / n, 2
        ),
    }
