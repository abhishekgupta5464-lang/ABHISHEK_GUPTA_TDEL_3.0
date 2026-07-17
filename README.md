# Smart Resume Screening and Candidate Ranking Tool

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered **Applicant Tracking System (ATS)** that automatically analyzes resumes, compares them against job descriptions, calculates ATS scores, ranks candidates, and generates interview recommendations — built for the **IBM AI Internship**.

![Dashboard Screenshot](assets/screenshots/dashboard.png)

> **Note:** Place your application screenshots in `assets/screenshots/` after running the app.

---

## Project Overview

Recruiters spend hours manually screening resumes. This tool automates that process using Natural Language Processing (NLP), Machine Learning, and Semantic Similarity to deliver instant, data-driven hiring insights.

### Key Capabilities

- Parse resumes (PDF, DOCX, TXT) and extract structured candidate data
- Analyze job descriptions for required skills, keywords, and experience
- Calculate weighted ATS scores (0–100) using multiple AI matching techniques
- Rank candidates automatically with hiring recommendations
- Generate resume improvement feedback and tailored interview questions
- Visualize analytics with interactive Plotly charts
- Export results as CSV or PDF reports

---

## Features

| Feature | Description |
|---------|-------------|
| **Resume Parser** | Extracts name, email, skills, education, experience, projects, certifications |
| **JD Parser** | Extracts required/preferred skills, experience, education, keywords |
| **AI Matching** | TF-IDF, Cosine Similarity, Sentence Transformers, Keyword Matching |
| **ATS Scoring** | Weighted 100-point score with progress bars and gauge charts |
| **Candidate Ranking** | Auto-rank with Highly Recommended / Recommended / Needs Improvement / Rejected |
| **Resume Feedback** | Missing skills, weak sections, grammar tips, project suggestions |
| **Interview Generator** | Questions by skill, project, experience — Beginner / Intermediate / Advanced |
| **Analytics** | Bar, pie, radar, histogram charts with score and skill distributions |
| **Database** | SQLite with full CRUD, search, and filter operations |
| **Downloads** | Export candidate rankings as CSV or individual PDF reports |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard (app.py)              │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  Resume  │   JD     │   ATS    │ Ranker   │   Analytics     │
│  Parser  │  Parser  │  Scorer  │          │   & Charts      │
├──────────┴──────────┴──────────┴──────────┴─────────────────┤
│              AI Matching Engine (skill_matcher.py)           │
│     TF-IDF │ Cosine Similarity │ Sentence Transformers      │
├─────────────────────────────────────────────────────────────┤
│                   SQLite Database (database.db)              │
└─────────────────────────────────────────────────────────────┘
```

### ATS Score Weights

| Component | Weight |
|-----------|--------|
| Skill Match | 40% |
| Experience | 20% |
| Education | 15% |
| Projects | 10% |
| Certifications | 10% |
| Resume Quality | 5% |

---

## Folder Structure

```
Smart_Resume_Screener/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── database.db                     # SQLite database (auto-created)
├── assets/
│   ├── sample_resumes/             # Sample resume files for testing
│   └── sample_job_descriptions/    # Sample JD files for testing
└── modules/
    ├── resume_parser.py            # Resume & JD parsing
    ├── skill_matcher.py            # AI matching engine
    ├── ats_score.py                # ATS score calculator
    ├── candidate_ranker.py         # Candidate ranking logic
    ├── database.py                 # SQLite CRUD operations
    ├── analytics.py                # Analytics computations
    ├── charts.py                   # Plotly chart generators
    ├── recommendation.py           # Hiring recommendations
    ├── interview_generator.py      # Interview question generator
    ├── resume_feedback.py          # Resume improvement suggestions
    └── utils.py                    # Shared utility functions
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- 4 GB RAM minimum (for Sentence Transformers model)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Smart_Resume_Screener.git
cd Smart_Resume_Screener
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Language Model (Optional)

```bash
python -m spacy download en_core_web_sm
```

> The app works without spaCy — it uses regex and vocabulary-based extraction as the primary method.

---

## Usage

### Start the Application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

### Quick Start Workflow

1. **Upload Job Description** — Go to "Upload Job Description", paste or upload a JD
2. **Upload Resumes** — Go to "Upload Resume", select the JD, upload PDF/DOCX/TXT files
3. **View Rankings** — Check "Candidate Ranking" for sorted results with ATS scores
4. **Analytics** — Explore charts in the "Analytics" page
5. **Feedback** — Get improvement suggestions in "Resume Feedback"
6. **Interview Prep** — Generate questions in "Interview Questions"

### Sample Data

Sample files are included in:
- `assets/sample_resumes/` — 3 sample candidate resumes
- `assets/sample_job_descriptions/` — 2 sample job descriptions

---

## Screenshots

| Dashboard | Candidate Ranking |
|-----------|-------------------|
| ![Dashboard](assets/screenshots/dashboard.png) | ![Ranking](assets/screenshots/ranking.png) |

| Analytics | Resume Feedback |
|-----------|----------------|
| ![Analytics](assets/screenshots/analytics.png) | ![Feedback](assets/screenshots/feedback.png) |

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.11+ |
| Framework | Streamlit |
| Database | SQLite |
| ML/NLP | scikit-learn, Sentence Transformers, spaCy |
| Data | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| File Parsing | PyPDF2, pdfplumber, python-docx |

---

## Future Scope

- [ ] Integration with LinkedIn and Naukri APIs for direct resume import
- [ ] Multi-language resume support (Hindi, Spanish, French)
- [ ] LLM-powered resume summarization using IBM Watsonx
- [ ] Email notifications for shortlisted candidates
- [ ] Role-based access control for recruiter teams
- [ ] Batch processing via REST API endpoints
- [ ] Customizable ATS score weight configuration
- [ ] Docker containerization for cloud deployment

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Author

Built for the **IBM AI Internship** program.

---

<p align="center">
  <b>Smart Resume Screener</b> — Hire Smarter, Not Harder 🚀
</p>
