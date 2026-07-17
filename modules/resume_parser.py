"""
Resume parser module for Smart Resume Screener.
Extracts structured information from PDF, DOCX, and TXT resume files.
"""

import io
import re
from typing import Any, Dict, Optional

import pdfplumber
from docx import Document
from PyPDF2 import PdfReader

from modules.utils import (
    calculate_total_experience_years,
    clean_text,
    extract_certifications,
    extract_education,
    extract_email,
    extract_experience_entries,
    extract_github,
    extract_languages,
    extract_linkedin,
    extract_name,
    extract_phone,
    extract_projects,
    extract_skills_from_text,
    validate_file_extension,
)


ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file using pdfplumber with PyPDF2 fallback."""
    text_parts = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        pass

    if not text_parts:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        except Exception as exc:
            raise ValueError(f"Unable to read PDF file: {exc}") from exc

    if not text_parts:
        raise ValueError("PDF appears to be empty or contains only images.")

    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from a DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        if not paragraphs:
            raise ValueError("DOCX file appears to be empty.")
        return "\n".join(paragraphs)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Unable to read DOCX file: {exc}") from exc


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text content from a plain text file."""
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            text = file_bytes.decode(encoding)
            if text.strip():
                return text
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode text file with supported encodings.")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Route file extraction to the appropriate parser based on extension."""
    if not validate_file_extension(filename, ALLOWED_EXTENSIONS):
        raise ValueError(
            f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    if ext in ("docx", "doc"):
        return extract_text_from_docx(file_bytes)
    if ext == "txt":
        return extract_text_from_txt(file_bytes)

    raise ValueError(f"Unsupported file extension: .{ext}")


def parse_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse a resume file and extract all structured candidate information.
    Returns a dictionary with name, contact info, skills, and sections.
    """
    if not file_bytes:
        raise ValueError("No resume file provided. Please upload a valid resume.")

    raw_text = extract_text_from_file(file_bytes, filename)
    text = clean_text(raw_text)

    if len(text) < 50:
        raise ValueError(
            "Resume content is too short. The file may be corrupted or empty."
        )

    parsed = {
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "skills": extract_skills_from_text(raw_text),
        "education": extract_education(raw_text),
        "experience": extract_experience_entries(raw_text),
        "projects": extract_projects(raw_text),
        "certifications": extract_certifications(raw_text),
        "languages": extract_languages(raw_text),
        "linkedin": extract_linkedin(raw_text),
        "github": extract_github(raw_text),
        "total_experience": calculate_total_experience_years(raw_text),
        "resume_text": raw_text,
        "file_name": filename,
    }

    return parsed


def parse_job_description_text(jd_text: str, title: str = "", company: str = "") -> Dict[str, Any]:
    """
    Parse job description text and extract structured requirements.
    Used when JD is entered as text rather than uploaded as a file.
    """
    from modules.utils import (
        extract_jd_education,
        extract_jd_keywords,
        extract_jd_skills,
        parse_experience_requirement,
    )

    if not jd_text or len(jd_text.strip()) < 20:
        raise ValueError("Job description is empty or too short.")

    text = jd_text.strip()
    required_skills, preferred_skills = extract_jd_skills(text)

    if not title:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        title = lines[0][:80] if lines else "Untitled Position"

    return {
        "title": title,
        "company": company,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_required": parse_experience_requirement(text),
        "education": extract_jd_education(text),
        "keywords": extract_jd_keywords(text),
        "jd_text": text,
    }


def parse_job_description_file(
    file_bytes: bytes,
    filename: str,
    title: str = "",
    company: str = "",
) -> Dict[str, Any]:
    """Parse a job description from an uploaded file."""
    text = extract_text_from_file(file_bytes, filename)
    result = parse_job_description_text(text, title, company)
    result["file_name"] = filename
    return result
