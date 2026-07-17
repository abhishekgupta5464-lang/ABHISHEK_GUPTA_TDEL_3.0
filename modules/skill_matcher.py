"""
Skill matching engine for Smart Resume Screener.
Uses TF-IDF, cosine similarity, and sentence transformers for matching.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.utils import clean_text


@lru_cache(maxsize=1)
def _load_sentence_model():
    """Load and cache the sentence transformer model for semantic matching."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """Compute TF-IDF cosine similarity between two text documents."""
    if not text1.strip() or not text2.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 2)
    except Exception:
        return 0.0


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity using sentence transformers."""
    model = _load_sentence_model()
    if model is None:
        return compute_tfidf_similarity(text1, text2)

    try:
        embeddings = model.encode([text1, text2], convert_to_numpy=True)
        similarity = cosine_similarity(
            embeddings[0].reshape(1, -1),
            embeddings[1].reshape(1, -1),
        )[0][0]
        return round(float(similarity) * 100, 2)
    except Exception:
        return compute_tfidf_similarity(text1, text2)


def compute_skill_match(
    resume_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Calculate skill match percentage between resume and job requirements.
    Required skills weighted at 80%, preferred at 20%.
    """
    preferred_skills = preferred_skills or []
    resume_lower = {s.lower() for s in resume_skills}

    matched_required = []
    missing_required = []
    for skill in required_skills:
        if skill.lower() in resume_lower or _fuzzy_skill_match(skill, resume_skills):
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred = []
    for skill in preferred_skills:
        if skill.lower() in resume_lower or _fuzzy_skill_match(skill, resume_skills):
            matched_preferred.append(skill)

    req_score = (
        (len(matched_required) / len(required_skills)) * 100
        if required_skills else 50.0
    )
    pref_score = (
        (len(matched_preferred) / len(preferred_skills)) * 100
        if preferred_skills else 50.0
    )

    if required_skills and preferred_skills:
        overall = req_score * 0.8 + pref_score * 0.2
    elif required_skills:
        overall = req_score
    elif preferred_skills:
        overall = pref_score
    else:
        overall = 50.0

    return {
        "skill_match_pct": round(overall, 2),
        "matched_skills": matched_required + matched_preferred,
        "missing_skills": missing_required,
        "required_match_pct": round(req_score, 2),
        "preferred_match_pct": round(pref_score, 2),
    }


def _fuzzy_skill_match(target: str, skills: List[str]) -> bool:
    """Check if target skill partially matches any resume skill."""
    target_lower = target.lower()
    target_parts = target_lower.replace(".", " ").split()

    for skill in skills:
        skill_lower = skill.lower()
        if target_lower in skill_lower or skill_lower in target_lower:
            return True
        if any(part in skill_lower for part in target_parts if len(part) > 2):
            return True
    return False


def compute_keyword_match(resume_text: str, keywords: List[str]) -> Dict[str, Any]:
    """Calculate keyword match percentage between resume and JD keywords."""
    if not keywords:
        return {"keyword_match_pct": 50.0, "matched_keywords": [], "missing_keywords": []}

    resume_lower = resume_text.lower()
    matched = []
    missing = []

    for kw in keywords:
        if kw.lower() in resume_lower:
            matched.append(kw)
        else:
            missing.append(kw)

    pct = (len(matched) / len(keywords)) * 100
    return {
        "keyword_match_pct": round(pct, 2),
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def compute_full_match(
    resume_data: Dict,
    jd_data: Dict,
) -> Dict[str, Any]:
    """
    Run complete AI matching pipeline combining all matching methods.
    Returns skill match, keyword match, semantic score, and TF-IDF score.
    """
    resume_text = resume_data.get("resume_text", "")
    jd_text = jd_data.get("jd_text", "")

    required = jd_data.get("required_skills", [])
    preferred = jd_data.get("preferred_skills", [])
    keywords = jd_data.get("keywords", [])

    skill_result = compute_skill_match(
        resume_data.get("skills", []),
        required,
        preferred,
    )

    keyword_result = compute_keyword_match(resume_text, keywords)
    tfidf_score = compute_tfidf_similarity(resume_text, jd_text)
    semantic_score = compute_semantic_similarity(resume_text, jd_text)

    return {
        "skill_match": skill_result["skill_match_pct"],
        "keyword_match": keyword_result["keyword_match_pct"],
        "semantic_score": semantic_score,
        "tfidf_score": tfidf_score,
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "matched_keywords": keyword_result["matched_keywords"],
        "missing_keywords": keyword_result["missing_keywords"],
    }
