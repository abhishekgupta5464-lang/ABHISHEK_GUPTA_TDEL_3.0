"""
Utility functions for Smart Resume Screener.
Provides shared helpers for text processing, file handling, and formatting.
"""

import os
import re
import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    "machine learning", "deep learning", "nlp", "computer vision", "data science",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd", "terraform",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot",
    "html", "css", "rest api", "graphql", "microservices", "agile", "scrum",
    "git", "github", "gitlab", "linux", "bash", "shell scripting",
    "tableau", "power bi", "excel", "spark", "hadoop", "kafka", "airflow",
    "communication", "leadership", "problem solving", "teamwork", "project management",
    "streamlit", "selenium", "pytest", "junit", "unit testing", "api development",
    "cloud computing", "devops", "etl", "data analysis", "statistics", "a/b testing",
    "blockchain", "cybersecurity", "networking", "sap", "salesforce", "oracle",
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "b.tech", "b.e.", "m.tech", "m.e.",
    "b.sc", "m.sc", "mba", "bca", "mca", "diploma", "associate", "high school",
    "computer science", "information technology", "engineering", "mathematics",
    "statistics", "business administration", "electrical", "mechanical", "civil",
]

EXPERIENCE_KEYWORDS = [
    "experience", "work history", "employment", "professional experience",
    "work experience", "career history", "internship", "intern",
]

PROJECT_KEYWORDS = [
    "projects", "project experience", "personal projects", "academic projects",
    "key projects", "portfolio",
]

CERT_KEYWORDS = [
    "certifications", "certificates", "licenses", "credentials", "certified",
]

LANGUAGE_KEYWORDS = [
    "languages", "language proficiency", "spoken languages",
]


def get_project_root() -> str:
    """Return the absolute path to the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_database_path() -> str:
    """Return the absolute path to the SQLite database file."""
    return os.path.join(get_project_root(), "database.db")


def clean_text(text: str) -> str:
    """Normalize whitespace and remove excessive special characters from text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"[^\w\s@.\-+(),/:;#&]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_email(text: str) -> Optional[str]:
    """Extract the first valid email address from text using regex."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0).lower() if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text supporting multiple formats."""
    patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        r"\b\d{10}\b",
        r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn profile URL from resume text."""
    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_github(text: str) -> Optional[str]:
    """Extract GitHub profile URL from resume text."""
    pattern = r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_name(text: str) -> str:
    """Extract candidate name from the first few lines of resume text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Unknown Candidate"

    skip_patterns = [
        r"resume", r"curriculum vitae", r"cv", r"@",
        r"\d{3}", r"http", r"linkedin", r"github",
    ]
    for line in lines[:5]:
        lower = line.lower()
        if any(re.search(p, lower) for p in skip_patterns):
            continue
        if 2 <= len(line.split()) <= 5 and len(line) < 60:
            name = re.sub(
                r"\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            if name:
                return name.title()

    words = lines[0].split()
    if 1 <= len(words) <= 4:
        return lines[0].title()
    return "Unknown Candidate"


def extract_section(text: str, section_keywords: List[str]) -> str:
    """Extract text belonging to a resume section based on keyword headers."""
    lines = text.split("\n")
    section_lines = []
    in_section = False

    all_section_headers = (
        EXPERIENCE_KEYWORDS + PROJECT_KEYWORDS + CERT_KEYWORDS
        + LANGUAGE_KEYWORDS + ["education", "skills", "summary", "objective",
                               "achievements", "awards", "references"]
    )

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            if in_section:
                section_lines.append("")
            continue

        is_target = any(kw in line_lower for kw in section_keywords)
        is_other_section = (
            not is_target
            and any(kw in line_lower for kw in all_section_headers)
            and len(line_lower) < 50
        )

        if is_target and len(line_lower) < 50:
            in_section = True
            continue

        if is_other_section:
            in_section = False
            continue

        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using vocabulary matching and section parsing."""
    text_lower = text.lower()
    found_skills = set()

    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.add(skill.title())

    skills_section = extract_section(text_lower, ["skills", "technical skills", "core competencies"])
    if skills_section:
        for part in re.split(r"[,|•\n\t;]", skills_section):
            skill = part.strip()
            if 2 < len(skill) < 40 and not skill.isdigit():
                found_skills.add(skill.title())

    return sorted(list(found_skills))


def extract_education(text: str) -> List[str]:
    """Extract education entries from resume text."""
    education_section = extract_section(text.lower(), ["education", "academic", "qualification"])
    entries = []

    if education_section:
        for line in education_section.split("\n"):
            line = line.strip()
            if line and any(kw in line.lower() for kw in EDUCATION_KEYWORDS):
                entries.append(line)

    if not entries:
        for line in text.split("\n"):
            line = line.strip()
            lower = line.lower()
            if any(kw in lower for kw in EDUCATION_KEYWORDS) and len(line) < 120:
                entries.append(line)

    return entries[:5]


def extract_experience_entries(text: str) -> List[str]:
    """Extract work experience entries from resume text."""
    exp_section = extract_section(text.lower(), EXPERIENCE_KEYWORDS)
    entries = []

    if exp_section:
        current = []
        for line in exp_section.split("\n"):
            line = line.strip()
            if not line:
                if current:
                    entries.append(" ".join(current))
                    current = []
            else:
                current.append(line)
        if current:
            entries.append(" ".join(current))

    return entries[:10]


def extract_projects(text: str) -> List[str]:
    """Extract project descriptions from resume text."""
    proj_section = extract_section(text.lower(), PROJECT_KEYWORDS)
    entries = []

    if proj_section:
        for line in proj_section.split("\n"):
            line = line.strip()
            if line and len(line) > 10:
                entries.append(line)

    return entries[:8]


def extract_certifications(text: str) -> List[str]:
    """Extract certification entries from resume text."""
    cert_section = extract_section(text.lower(), CERT_KEYWORDS)
    entries = []

    if cert_section:
        for line in cert_section.split("\n"):
            line = line.strip()
            if line and len(line) > 5:
                entries.append(line)

    cert_patterns = [
        r"certified\s+\w+",
        r"\b(AWS|Azure|GCP|Google|Microsoft|Oracle|Cisco|CompTIA|PMP|Scrum)\s+\w+",
    ]
    for pattern in cert_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entries.append(match.group(0))

    return list(set(entries))[:8]


def extract_languages(text: str) -> List[str]:
    """Extract spoken languages from resume text."""
    lang_section = extract_section(text.lower(), LANGUAGE_KEYWORDS)
    languages = []

    common_langs = [
        "english", "hindi", "spanish", "french", "german", "chinese",
        "japanese", "korean", "arabic", "portuguese", "russian", "tamil",
        "telugu", "bengali", "marathi", "urdu", "italian", "dutch",
    ]

    search_text = (lang_section + " " + text).lower()
    for lang in common_langs:
        if re.search(r"\b" + lang + r"\b", search_text):
            languages.append(lang.title())

    return languages


def calculate_total_experience_years(text: str) -> float:
    """Estimate total years of experience from date ranges in resume text."""
    patterns = [
        r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)",
        r"experience[:\s]+(\d+)\+?\s*years?",
    ]

    years_found = []
    text_lower = text.lower()

    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                val = float(match.group(1))
                if val <= 50:
                    years_found.append(val)
            except (ValueError, IndexError):
                continue

    range_pattern = r"(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|present|current)"
    for match in re.finditer(range_pattern, text_lower):
        start = int(match.group(1))
        end_str = match.group(2)
        end = 2026 if end_str in ("present", "current") else int(end_str)
        if end >= start:
            years_found.append(end - start)

    return round(max(years_found) if years_found else 0.0, 1)


def parse_experience_requirement(jd_text: str) -> float:
    """Parse required years of experience from job description text."""
    patterns = [
        r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*(?:of\s*)?(?:experience|exp)",
        r"minimum\s*(\d+)\s*years?",
        r"at least\s*(\d+)\s*years?",
        r"(\d+)\s*[-–]\s*\d+\s*years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, jd_text.lower())
        if match:
            return float(match.group(1))
    return 0.0


def extract_jd_skills(jd_text: str) -> Tuple[List[str], List[str]]:
    """Extract required and preferred skills from job description."""
    text_lower = jd_text.lower()
    required = []
    preferred = []

    req_section = ""
    pref_section = ""

    lines = jd_text.split("\n")
    current = None
    for line in lines:
        lower = line.lower().strip()
        if any(k in lower for k in ["required skills", "must have", "requirements", "required:"]):
            current = "required"
            continue
        if any(k in lower for k in ["preferred skills", "nice to have", "preferred:", "bonus"]):
            current = "preferred"
            continue
        if current == "required":
            req_section += " " + line
        elif current == "preferred":
            pref_section += " " + line

    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            if req_section and re.search(pattern, req_section.lower()):
                required.append(skill.title())
            elif pref_section and re.search(pattern, pref_section.lower()):
                preferred.append(skill.title())
            else:
                required.append(skill.title())

    return sorted(set(required)), sorted(set(preferred))


def extract_jd_keywords(jd_text: str) -> List[str]:
    """Extract important keywords from job description for ATS matching."""
    text_lower = jd_text.lower()
    keywords = set()

    for skill in COMMON_SKILLS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            keywords.add(skill)

    for match in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", jd_text):
        keywords.add(match.group(0).lower())

    for line in jd_text.split("\n"):
        line = line.strip().lstrip("•-*→ ")
        if 3 < len(line) < 80:
            keywords.add(line.lower())

    return sorted(list(keywords))[:30]


def extract_jd_education(jd_text: str) -> List[str]:
    """Extract education requirements from job description."""
    entries = []
    for line in jd_text.split("\n"):
        lower = line.lower()
        if any(kw in lower for kw in EDUCATION_KEYWORDS) and len(line) < 120:
            entries.append(line.strip())
    return entries[:5]


def score_color(score: float) -> str:
    """Return hex color code based on ATS score value."""
    if score >= 80:
        return "#00C853"
    if score >= 60:
        return "#FFD600"
    if score >= 40:
        return "#FF9100"
    return "#FF1744"


def recommendation_color(recommendation: str) -> str:
    """Return hex color for recommendation label."""
    colors = {
        "Highly Recommended": "#00C853",
        "Recommended": "#69F0AE",
        "Needs Improvement": "#FFD600",
        "Rejected": "#FF1744",
    }
    return colors.get(recommendation, "#78909C")


def format_list_for_display(items: List[str], max_items: int = 10) -> str:
    """Format a list of strings for display in the UI."""
    if not items:
        return "None"
    display = items[:max_items]
    result = ", ".join(display)
    if len(items) > max_items:
        result += f" (+{len(items) - max_items} more)"
    return result


def list_to_json(items: List[Any]) -> str:
    """Serialize a list to JSON string for database storage."""
    return json.dumps(items)


def json_to_list(json_str: str) -> List[Any]:
    """Deserialize JSON string back to a list."""
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []


def generate_file_hash(content: bytes) -> str:
    """Generate MD5 hash of file content for duplicate detection."""
    return hashlib.md5(content).hexdigest()


def validate_file_extension(filename: str, allowed: List[str]) -> bool:
    """Check if uploaded file has an allowed extension."""
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
