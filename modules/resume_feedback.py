"""
Resume feedback module for Smart Resume Screener.
Analyzes resumes and provides actionable improvement suggestions.
"""

import re
from typing import Any, Dict, List

from modules.utils import clean_text


def analyze_grammar_issues(text: str) -> List[str]:
    """Detect common grammar and formatting issues in resume text."""
    issues = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped[0].islower() and len(stripped) > 20:
            issues.append(f"Line {i + 1}: Starts with lowercase — capitalize section content.")

        if re.search(r"\s{2,}", stripped):
            issues.append(f"Line {i + 1}: Contains extra spaces.")

        weak_verbs = ["did", "made", "got", "was", "were", "had"]
        for verb in weak_verbs:
            if re.search(rf"\b{verb}\b", stripped.lower()) and len(stripped) > 30:
                issues.append(
                    f"Line {i + 1}: Consider replacing weak verb '{verb}' with action verbs."
                )
                break

    if not re.search(r"\b(developed|built|designed|implemented|led|managed|created)\b", text.lower()):
        issues.append("Resume lacks strong action verbs. Use: developed, built, implemented, led.")

    return issues[:8]


def analyze_resume_length(text: str) -> Dict[str, Any]:
    """Analyze resume length and provide length-based feedback."""
    word_count = len(text.split())
    char_count = len(text)
    line_count = len([l for l in text.split("\n") if l.strip()])

    if word_count < 150:
        status = "Too Short"
        feedback = "Resume is too brief. Add more detail about experience, projects, and skills."
        score = 40
    elif word_count < 300:
        status = "Short"
        feedback = "Resume is on the shorter side. Consider adding project details and achievements."
        score = 65
    elif word_count <= 800:
        status = "Optimal"
        feedback = "Resume length is ideal for ATS systems (300-800 words)."
        score = 100
    elif word_count <= 1200:
        status = "Long"
        feedback = "Resume is slightly long. Trim redundant content for better readability."
        score = 75
    else:
        status = "Too Long"
        feedback = "Resume exceeds recommended length. Recruiters prefer concise 1-2 page resumes."
        score = 50

    return {
        "word_count": word_count,
        "char_count": char_count,
        "line_count": line_count,
        "status": status,
        "feedback": feedback,
        "score": score,
    }


def identify_weak_sections(resume_data: Dict[str, Any]) -> List[str]:
    """Identify resume sections that need improvement."""
    weak = []

    if not resume_data.get("skills") or len(resume_data["skills"]) < 3:
        weak.append("Skills section is missing or too sparse. Add 8-15 relevant technical skills.")

    if not resume_data.get("experience"):
        weak.append("No work experience detected. Add internships or freelance work if applicable.")

    if not resume_data.get("projects"):
        weak.append("Projects section is empty. Add 2-3 projects demonstrating your skills.")

    if not resume_data.get("education"):
        weak.append("Education section not found. Include degree, institution, and graduation year.")

    if not resume_data.get("email"):
        weak.append("Email address missing. Always include professional contact information.")

    if not resume_data.get("certifications"):
        weak.append("No certifications listed. Industry certs boost ATS scores significantly.")

    if not resume_data.get("linkedin") and not resume_data.get("github"):
        weak.append("Missing LinkedIn/GitHub links. Online profiles increase credibility.")

    exp_entries = resume_data.get("experience", [])
    if exp_entries:
        for entry in exp_entries:
            if not re.search(r"\d{4}", entry):
                weak.append("Experience entries missing dates. Add start/end dates for each role.")
                break

    return weak


def suggest_projects(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> List[str]:
    """Suggest project ideas based on missing skills from job description."""
    suggestions = []
    missing = set(s.lower() for s in jd_data.get("required_skills", []))
    resume_skills = set(s.lower() for s in resume_data.get("skills", []))
    gap_skills = missing - resume_skills

    project_templates = {
        "python": "Build a Python automation tool or REST API using Flask/FastAPI.",
        "machine learning": "Create an ML model for prediction using scikit-learn on a public dataset.",
        "react": "Develop a responsive React dashboard with API integration.",
        "docker": "Containerize a web application using Docker and docker-compose.",
        "aws": "Deploy a full-stack app on AWS using EC2, S3, and Lambda.",
        "sql": "Design a normalized database schema and write complex SQL queries.",
        "data science": "Perform end-to-end data analysis with visualization on Kaggle dataset.",
        "tensorflow": "Build a deep learning model for image classification using TensorFlow.",
        "kubernetes": "Set up a microservices architecture orchestrated with Kubernetes.",
        "streamlit": "Create an interactive data app using Streamlit for business insights.",
    }

    for skill in list(gap_skills)[:5]:
        for key, template in project_templates.items():
            if key in skill:
                suggestions.append(f"To demonstrate '{skill.title()}': {template}")
                break
        else:
            suggestions.append(
                f"Build a portfolio project showcasing '{skill.title()}' skills."
            )

    if not suggestions:
        suggestions.append(
            "Add quantified achievements to existing projects (e.g., 'Improved accuracy by 15%')."
        )

    return suggestions[:6]


def generate_resume_feedback(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    match_results: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive resume feedback with all improvement suggestions.
    Combines missing skills, weak sections, grammar, length, and project tips.
    """
    match_results = match_results or {}
    resume_text = resume_data.get("resume_text", "")

    missing_skills = match_results.get(
        "missing_skills",
        [s for s in jd_data.get("required_skills", [])
         if s.lower() not in [r.lower() for r in resume_data.get("skills", [])]],
    )

    missing_keywords = match_results.get(
        "missing_keywords",
        [k for k in jd_data.get("keywords", [])
         if k.lower() not in resume_text.lower()],
    )

    return {
        "missing_skills": missing_skills[:10],
        "missing_keywords": missing_keywords[:10],
        "weak_sections": identify_weak_sections(resume_data),
        "grammar_issues": analyze_grammar_issues(resume_text),
        "length_analysis": analyze_resume_length(resume_text),
        "project_suggestions": suggest_projects(resume_data, jd_data),
        "overall_tips": _generate_overall_tips(resume_data, jd_data),
    }


def _generate_overall_tips(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
) -> List[str]:
    """Generate general resume improvement tips."""
    tips = [
        "Tailor your resume keywords to match the job description exactly.",
        "Use bullet points with quantified results (e.g., 'Reduced latency by 40%').",
        "Place most relevant skills and experience at the top of each section.",
        "Use standard section headings: Experience, Education, Skills, Projects.",
        "Save and upload as PDF to preserve formatting across ATS systems.",
    ]

    if not resume_data.get("certifications"):
        tips.append("Obtain relevant certifications (AWS, Google, Microsoft) to stand out.")

    if jd_data.get("experience_required", 0) > resume_data.get("total_experience", 0):
        tips.append(
            f"Job requires {jd_data['experience_required']} years experience. "
            "Highlight internships and academic projects to bridge the gap."
        )

    return tips
