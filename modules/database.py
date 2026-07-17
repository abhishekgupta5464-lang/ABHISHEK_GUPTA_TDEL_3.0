"""
SQLite database module for Smart Resume Screener.
Handles CRUD operations for candidates and job descriptions.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from modules.utils import get_database_path, json_to_list, list_to_json


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection with row factory."""
    conn = sqlite3.connect(get_database_path())
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """Create database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            projects TEXT,
            certifications TEXT,
            languages TEXT,
            linkedin TEXT,
            github TEXT,
            total_experience REAL DEFAULT 0,
            ats_score REAL DEFAULT 0,
            skill_match REAL DEFAULT 0,
            keyword_match REAL DEFAULT 0,
            semantic_score REAL DEFAULT 0,
            experience_score REAL DEFAULT 0,
            education_score REAL DEFAULT 0,
            projects_score REAL DEFAULT 0,
            certifications_score REAL DEFAULT 0,
            resume_quality_score REAL DEFAULT 0,
            recommendation TEXT DEFAULT 'Needs Improvement',
            resume_text TEXT,
            file_name TEXT,
            job_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            experience_required REAL DEFAULT 0,
            education TEXT,
            keywords TEXT,
            jd_text TEXT,
            file_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_candidate(data: Dict[str, Any]) -> int:
    """Insert a new candidate record and return the generated ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO candidates (
            name, email, phone, skills, education, experience, projects,
            certifications, languages, linkedin, github, total_experience,
            ats_score, skill_match, keyword_match, semantic_score,
            experience_score, education_score, projects_score,
            certifications_score, resume_quality_score, recommendation,
            resume_text, file_name, job_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", "Unknown"),
        data.get("email"),
        data.get("phone"),
        list_to_json(data.get("skills", [])),
        list_to_json(data.get("education", [])),
        list_to_json(data.get("experience", [])),
        list_to_json(data.get("projects", [])),
        list_to_json(data.get("certifications", [])),
        list_to_json(data.get("languages", [])),
        data.get("linkedin"),
        data.get("github"),
        data.get("total_experience", 0),
        data.get("ats_score", 0),
        data.get("skill_match", 0),
        data.get("keyword_match", 0),
        data.get("semantic_score", 0),
        data.get("experience_score", 0),
        data.get("education_score", 0),
        data.get("projects_score", 0),
        data.get("certifications_score", 0),
        data.get("resume_quality_score", 0),
        data.get("recommendation", "Needs Improvement"),
        data.get("resume_text", ""),
        data.get("file_name", ""),
        data.get("job_id"),
    ))

    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id


def update_candidate(candidate_id: int, data: Dict[str, Any]) -> bool:
    """Update an existing candidate record by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    list_fields = ["skills", "education", "experience", "projects",
                   "certifications", "languages"]
    update_data = dict(data)
    for field in list_fields:
        if field in update_data and isinstance(update_data[field], list):
            update_data[field] = list_to_json(update_data[field])

    update_data["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in update_data.keys())
    values = list(update_data.values()) + [candidate_id]

    cursor.execute(f"UPDATE candidates SET {set_clause} WHERE id = ?", values)

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def delete_candidate(candidate_id: int) -> bool:
    """Delete a candidate record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_candidate(candidate_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single candidate by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_all_candidates(job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieve all candidates, optionally filtered by job ID."""
    conn = get_connection()
    cursor = conn.cursor()

    if job_id:
        cursor.execute(
            "SELECT * FROM candidates WHERE job_id = ? ORDER BY ats_score DESC",
            (job_id,),
        )
    else:
        cursor.execute("SELECT * FROM candidates ORDER BY ats_score DESC")

    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


def search_candidates(
    name: str = "",
    skill: str = "",
    min_experience: float = 0,
    education: str = "",
    min_ats_score: float = 0,
) -> List[Dict[str, Any]]:
    """Search candidates using multiple filter criteria."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM candidates WHERE 1=1"
    params: List[Any] = []

    if name:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{name.lower()}%")

    if skill:
        query += " AND LOWER(skills) LIKE ?"
        params.append(f"%{skill.lower()}%")

    if min_experience > 0:
        query += " AND total_experience >= ?"
        params.append(min_experience)

    if education:
        query += " AND LOWER(education) LIKE ?"
        params.append(f"%{education.lower()}%")

    if min_ats_score > 0:
        query += " AND ats_score >= ?"
        params.append(min_ats_score)

    query += " ORDER BY ats_score DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


def insert_job_description(data: Dict[str, Any]) -> int:
    """Insert a new job description record and return the generated ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO job_descriptions (
            title, company, required_skills, preferred_skills,
            experience_required, education, keywords, jd_text, file_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("title", "Untitled Position"),
        data.get("company", ""),
        list_to_json(data.get("required_skills", [])),
        list_to_json(data.get("preferred_skills", [])),
        data.get("experience_required", 0),
        list_to_json(data.get("education", [])),
        list_to_json(data.get("keywords", [])),
        data.get("jd_text", ""),
        data.get("file_name", ""),
    ))

    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id


def get_job_description(job_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a job description by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_job_dict(row) if row else None


def get_all_job_descriptions() -> List[Dict[str, Any]]:
    """Retrieve all job descriptions ordered by creation date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_job_dict(row) for row in rows]


def delete_job_description(job_id: int) -> bool:
    """Delete a job description by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_descriptions WHERE id = ?", (job_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_candidate_count() -> int:
    """Return total number of candidates in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM candidates")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_average_ats_score() -> float:
    """Return average ATS score across all candidates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(ats_score) FROM candidates")
    result = cursor.fetchone()[0]
    conn.close()
    return round(result or 0, 2)


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a candidate database row to a dictionary with parsed lists."""
    d = dict(row)
    for field in ["skills", "education", "experience", "projects",
                  "certifications", "languages"]:
        d[field] = json_to_list(d.get(field, "[]"))
    return d


def _row_to_job_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a job description database row to a dictionary."""
    d = dict(row)
    for field in ["required_skills", "preferred_skills", "education", "keywords"]:
        d[field] = json_to_list(d.get(field, "[]"))
    return d
