"""
ATS Score calculator for Smart Resume Screener.
Computes weighted overall ATS score out of 100.
"""

from typing import Any, Dict, List

from modules.skill_matcher import compute_full_match


WEIGHTS = {
    "skill_match": 0.40,
    "experience": 0.20,
    "education": 0.15,
    "projects": 0.10,
    "certifications": 0.10,
    "resume_quality": 0.05,
}


def score_experience(candidate_exp: float, required_exp: float) -> float:
    """Score experience fit on a 0-100 scale against job requirement."""
    if required_exp <= 0:
        return 80.0 if candidate_exp > 0 else 50.0

    ratio = candidate_exp / required_exp
    if ratio >= 1.0:
        return min(100.0, 70.0 + (ratio - 1.0) * 15)
    if ratio >= 0.7:
        return 50.0 + ratio * 35
    return max(10.0, ratio * 70)


def score_education(
    candidate_education: List[str],
    jd_education: List[str],
) -> float:
    """Score education alignment between candidate and job requirements."""
    if not jd_education:
        return 75.0 if candidate_education else 40.0

    if not candidate_education:
        return 20.0

    candidate_text = " ".join(candidate_education).lower()
    jd_text = " ".join(jd_education).lower()

    degree_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "mba", "b.sc", "m.sc"]
    matches = sum(
        1 for kw in degree_keywords
        if kw in jd_text and kw in candidate_text
    )

    field_keywords = [
        "computer", "software", "engineering", "science", "technology",
        "information", "data", "business", "mathematics",
    ]
    field_matches = sum(
        1 for kw in field_keywords
        if kw in jd_text and kw in candidate_text
    )

    base = 40.0
    base += matches * 20
    base += field_matches * 10
    return min(100.0, base)


def score_projects(candidate_projects: List[str], jd_keywords: List[str]) -> float:
    """Score project relevance based on keyword overlap with job description."""
    if not candidate_projects:
        return 30.0

    if not jd_keywords:
        return 60.0 + min(30, len(candidate_projects) * 5)

    project_text = " ".join(candidate_projects).lower()
    matches = sum(1 for kw in jd_keywords if kw.lower() in project_text)
    relevance = (matches / len(jd_keywords)) * 70
    quantity_bonus = min(30, len(candidate_projects) * 5)
    return min(100.0, relevance + quantity_bonus)


def score_certifications(
    candidate_certs: List[str],
    jd_keywords: List[str],
) -> float:
    """Score certifications relevance to the job description."""
    if not candidate_certs:
        return 35.0

    cert_text = " ".join(candidate_certs).lower()
    if jd_keywords:
        matches = sum(1 for kw in jd_keywords if kw.lower() in cert_text)
        return min(100.0, 50 + (matches / len(jd_keywords)) * 50)

    return min(100.0, 50 + len(candidate_certs) * 10)


def score_resume_quality(resume_data: Dict[str, Any]) -> float:
    """Evaluate overall resume completeness and quality."""
    score = 0.0
    checks = [
        (resume_data.get("email"), 15),
        (resume_data.get("phone"), 10),
        (resume_data.get("skills"), 20),
        (resume_data.get("education"), 15),
        (resume_data.get("experience"), 20),
        (resume_data.get("projects"), 10),
        (resume_data.get("linkedin") or resume_data.get("github"), 10),
    ]

    for value, points in checks:
        if value:
            if isinstance(value, list) and len(value) > 0:
                score += points
            elif isinstance(value, str) and value.strip():
                score += points

    resume_text = resume_data.get("resume_text", "")
    word_count = len(resume_text.split())
    if 300 <= word_count <= 800:
        score = min(100, score)
    elif word_count < 150:
        score *= 0.7
    elif word_count > 1200:
        score *= 0.85

    return round(min(100.0, score), 2)


def calculate_ats_score(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate complete ATS score with component breakdown.
    Weights: Skills 40%, Experience 20%, Education 15%,
    Projects 10%, Certifications 10%, Resume Quality 5%.
    """
    match_results = compute_full_match(resume_data, jd_data)

    exp_score = score_experience(
        resume_data.get("total_experience", 0),
        jd_data.get("experience_required", 0),
    )
    edu_score = score_education(
        resume_data.get("education", []),
        jd_data.get("education", []),
    )
    proj_score = score_projects(
        resume_data.get("projects", []),
        jd_data.get("keywords", []),
    )
    cert_score = score_certifications(
        resume_data.get("certifications", []),
        jd_data.get("keywords", []),
    )
    quality_score = score_resume_quality(resume_data)

    skill_component = match_results["skill_match"] * WEIGHTS["skill_match"]
    exp_component = exp_score * WEIGHTS["experience"]
    edu_component = edu_score * WEIGHTS["education"]
    proj_component = proj_score * WEIGHTS["projects"]
    cert_component = cert_score * WEIGHTS["certifications"]
    quality_component = quality_score * WEIGHTS["resume_quality"]

    overall = (
        skill_component + exp_component + edu_component
        + proj_component + cert_component + quality_component
    )

    return {
        "ats_score": round(min(100.0, overall), 2),
        "skill_match": match_results["skill_match"],
        "keyword_match": match_results["keyword_match"],
        "semantic_score": match_results["semantic_score"],
        "experience_score": round(exp_score, 2),
        "education_score": round(edu_score, 2),
        "projects_score": round(proj_score, 2),
        "certifications_score": round(cert_score, 2),
        "resume_quality_score": round(quality_score, 2),
        "matched_skills": match_results["matched_skills"],
        "missing_skills": match_results["missing_skills"],
        "matched_keywords": match_results["matched_keywords"],
        "missing_keywords": match_results["missing_keywords"],
    }
