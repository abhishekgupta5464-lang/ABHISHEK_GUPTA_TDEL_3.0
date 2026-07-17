"""
Smart Resume Screening and Candidate Ranking Tool
Main Streamlit application entry point.
IBM AI Internship Project
"""

import io
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.analytics import compute_dashboard_metrics, compute_match_analytics
from modules.ats_score import calculate_ats_score
from modules.candidate_ranker import candidates_to_dataframe, get_top_candidates, rank_candidates
from modules.charts import (
    create_experience_histogram,
    create_gauge_chart,
    create_match_comparison_chart,
    create_radar_chart,
    create_recommendation_pie_chart,
    create_score_distribution_chart,
    create_skill_bar_chart,
    create_top_candidates_chart,
)
from modules.database import (
    delete_candidate,
    delete_job_description,
    get_all_candidates,
    get_all_job_descriptions,
    get_candidate,
    get_candidate_count,
    get_average_ats_score,
    initialize_database,
    insert_candidate,
    insert_job_description,
    search_candidates,
)
from modules.interview_generator import generate_interview_questions
from modules.recommendation import get_recommendation, get_recommendation_details
from modules.resume_feedback import generate_resume_feedback
from modules.resume_parser import parse_job_description_file, parse_job_description_text, parse_resume
from modules.utils import dataframe_to_csv_bytes, format_list_for_display, recommendation_color, score_color

# ---------------------------------------------------------------------------
# Page configuration and global styles
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0E1117; }
    .metric-card {
        background: linear-gradient(135deg, #1A1D24 0%, #252830 100%);
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-card h3 { color: #8892A4; font-size: 0.85rem; margin: 0; font-weight: 500; }
    .metric-card h1 { color: #FAFAFA; font-size: 2rem; margin: 0.3rem 0 0 0; font-weight: 700; }
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .section-header {
        color: #FAFAFA;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00C853;
    }
    div[data-testid="stSidebar"] { background-color: #1A1D24; }
    .stButton > button {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: #000;
        font-weight: 600;
        border: none;
        border-radius: 8px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        "selected_job_id": None,
        "last_upload_message": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_metric_card(label: str, value, suffix: str = ""):
    """Render a styled metric card in the dashboard."""
    st.markdown(
        f'<div class="metric-card"><h3>{label}</h3><h1>{value}{suffix}</h1></div>',
        unsafe_allow_html=True,
    )


def process_and_save_resume(file_bytes: bytes, filename: str, job_id: int):
    """Parse resume, calculate ATS score, and save to database."""
    resume_data = parse_resume(file_bytes, filename)
    jobs = get_all_job_descriptions()
    jd_data = next((j for j in jobs if j["id"] == job_id), None)

    if not jd_data:
        raise ValueError("Please upload a Job Description before screening resumes.")

    scores = calculate_ats_score(resume_data, jd_data)
    resume_data.update(scores)
    resume_data["recommendation"] = get_recommendation(scores["ats_score"])
    resume_data["job_id"] = job_id

    candidate_id = insert_candidate(resume_data)
    return candidate_id, resume_data, scores


def generate_pdf_report(candidate: dict) -> bytes:
    """Generate a simple text-based PDF report for a candidate."""
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt

    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")

        lines = [
            "SMART RESUME SCREENER - CANDIDATE REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            f"Candidate: {candidate.get('name', 'Unknown')}",
            f"Email: {candidate.get('email', 'N/A')}",
            f"Phone: {candidate.get('phone', 'N/A')}",
            f"Experience: {candidate.get('total_experience', 0)} years",
            "",
            f"ATS Score: {candidate.get('ats_score', 0)}/100",
            f"Skill Match: {candidate.get('skill_match', 0)}%",
            f"Keyword Match: {candidate.get('keyword_match', 0)}%",
            f"Semantic Score: {candidate.get('semantic_score', 0)}%",
            f"Recommendation: {candidate.get('recommendation', 'N/A')}",
            "",
            f"Skills: {', '.join(candidate.get('skills', []))}",
            f"Education: {'; '.join(candidate.get('education', []))}",
        ]

        ax.text(0.05, 0.95, "\n".join(lines), transform=ax.transAxes,
                fontsize=10, verticalalignment="top", fontfamily="monospace")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------------------------
# Page: Dashboard
# ---------------------------------------------------------------------------

def page_dashboard():
    """Render the main dashboard with key metrics and charts."""
    st.markdown('<p class="section-header">📊 Dashboard Overview</p>', unsafe_allow_html=True)

    candidates = get_all_candidates()
    metrics = compute_dashboard_metrics(candidates)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Candidates", metrics["total_candidates"])
    with col2:
        render_metric_card("Average ATS Score", metrics["average_ats_score"], "%")
    with col3:
        render_metric_card("Highly Recommended", metrics["highly_recommended"])
    with col4:
        render_metric_card("Highest Score", metrics["highest_score"], "%")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        if candidates:
            st.plotly_chart(
                create_score_distribution_chart(metrics["score_distribution"]),
                use_container_width=True,
            )
        else:
            st.info("Upload resumes to see score distribution.")

    with col_b:
        if candidates:
            st.plotly_chart(
                create_recommendation_pie_chart(metrics["recommendation_distribution"]),
                use_container_width=True,
            )
        else:
            st.info("Upload resumes to see recommendation breakdown.")

    if metrics["top_candidates"]:
        st.markdown('<p class="section-header">🏆 Top Candidates</p>', unsafe_allow_html=True)
        st.plotly_chart(
            create_top_candidates_chart(metrics["top_candidates"]),
            use_container_width=True,
        )

        top_df = candidates_to_dataframe(metrics["top_candidates"])
        st.dataframe(top_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Page: Upload Resume
# ---------------------------------------------------------------------------

def page_upload_resume():
    """Render resume upload and screening page."""
    st.markdown('<p class="section-header">📄 Upload Resume</p>', unsafe_allow_html=True)

    jobs = get_all_job_descriptions()
    if not jobs:
        st.warning("⚠️ No job descriptions found. Please upload a Job Description first.")
        return

    job_options = {f"{j['title']} ({j['company'] or 'N/A'})": j["id"] for j in jobs}
    selected_job_label = st.selectbox("Select Job Description", list(job_options.keys()))
    job_id = job_options[selected_job_label]
    st.session_state.selected_job_id = job_id

    uploaded_files = st.file_uploader(
        "Upload Resume(s)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT",
    )

    if uploaded_files and st.button("🔍 Screen & Save Candidates", type="primary"):
        progress = st.progress(0)
        results = []

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    file_bytes = uploaded_file.read()
                    cid, resume_data, scores = process_and_save_resume(
                        file_bytes, uploaded_file.name, job_id
                    )
                    results.append({
                        "name": resume_data["name"],
                        "score": scores["ats_score"],
                        "rec": get_recommendation(scores["ats_score"]),
                        "status": "✅ Success",
                    })
            except ValueError as exc:
                results.append({
                    "name": uploaded_file.name,
                    "score": 0,
                    "rec": "Error",
                    "status": f"❌ {exc}",
                })
            except Exception as exc:
                results.append({
                    "name": uploaded_file.name,
                    "score": 0,
                    "rec": "Error",
                    "status": f"❌ Unexpected error: {exc}",
                })

            progress.progress((i + 1) / len(uploaded_files))

        st.success(f"Processed {len(uploaded_files)} resume(s)!")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Sample Resumes** (place files in `assets/sample_resumes/`)")
    sample_dir = os.path.join(os.path.dirname(__file__), "assets", "sample_resumes")
    if os.path.exists(sample_dir):
        samples = [f for f in os.listdir(sample_dir) if f.endswith((".txt", ".pdf", ".docx"))]
        if samples:
            st.write(", ".join(samples))
        else:
            st.caption("No sample files yet.")


# ---------------------------------------------------------------------------
# Page: Upload Job Description
# ---------------------------------------------------------------------------

def page_upload_jd():
    """Render job description upload page."""
    st.markdown('<p class="section-header">💼 Upload Job Description</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Paste Text", "📁 Upload File"])

    with tab1:
        title = st.text_input("Job Title", placeholder="e.g. Senior Python Developer")
        company = st.text_input("Company", placeholder="e.g. IBM")
        jd_text = st.text_area(
            "Job Description",
            height=300,
            placeholder="Paste the full job description here...",
        )

        if st.button("💾 Save Job Description", key="save_jd_text"):
            if not jd_text.strip():
                st.error("Job description cannot be empty.")
            else:
                try:
                    parsed = parse_job_description_text(jd_text, title, company)
                    job_id = insert_job_description(parsed)
                    st.success(f"✅ Job description saved! (ID: {job_id})")
                    st.json({
                        "Required Skills": parsed["required_skills"],
                        "Preferred Skills": parsed["preferred_skills"],
                        "Experience Required": f"{parsed['experience_required']} years",
                        "Keywords": parsed["keywords"][:10],
                    })
                except ValueError as exc:
                    st.error(str(exc))

    with tab2:
        jd_title = st.text_input("Job Title", key="jd_file_title", placeholder="e.g. Data Scientist")
        jd_company = st.text_input("Company", key="jd_file_company", placeholder="e.g. IBM")
        jd_file = st.file_uploader("Upload JD File", type=["pdf", "docx", "txt"], key="jd_file")

        if jd_file and st.button("💾 Save from File", key="save_jd_file"):
            try:
                with st.spinner("Parsing job description..."):
                    parsed = parse_job_description_file(
                        jd_file.read(), jd_file.name, jd_title, jd_company
                    )
                    job_id = insert_job_description(parsed)
                    st.success(f"✅ Job description saved! (ID: {job_id})")
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Error parsing file: {exc}")

    st.markdown("---")
    st.markdown("**Saved Job Descriptions**")
    jobs = get_all_job_descriptions()
    if jobs:
        for job in jobs:
            with st.expander(f"📌 {job['title']} — {job['company'] or 'N/A'}"):
                st.write(f"**Required Skills:** {format_list_for_display(job['required_skills'])}")
                st.write(f"**Experience:** {job['experience_required']} years")
                if st.button("🗑️ Delete", key=f"del_job_{job['id']}"):
                    delete_job_description(job["id"])
                    st.rerun()
    else:
        st.info("No job descriptions saved yet.")


# ---------------------------------------------------------------------------
# Page: Candidate Ranking
# ---------------------------------------------------------------------------

def page_ranking():
    """Render candidate ranking page with search and filters."""
    st.markdown('<p class="section-header">🏅 Candidate Ranking</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_name = st.text_input("🔍 Search by Name", "")
    with col2:
        search_skill = st.text_input("🛠️ Filter by Skill", "")
    with col3:
        min_exp = st.number_input("Min Experience (yrs)", 0.0, 30.0, 0.0, 0.5)
    with col4:
        min_score = st.slider("Min ATS Score", 0, 100, 0)

    candidates = search_candidates(
        name=search_name,
        skill=search_skill,
        min_experience=min_exp,
        min_ats_score=min_score,
    )

    if not candidates:
        st.info("No candidates match your filters. Upload resumes to get started.")
        return

    ranked_df = candidates_to_dataframe(candidates)

    def color_recommendation(val):
        """Apply color styling to recommendation column."""
        color = recommendation_color(val)
        return f"background-color: {color}22; color: {color}; font-weight: 600"

    styled = ranked_df.style.map(color_recommendation, subset=["Recommendation"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        csv_bytes = dataframe_to_csv_bytes(ranked_df)
        st.download_button(
            "📥 Download CSV",
            csv_bytes,
            file_name=f"candidates_ranking_{datetime.now():%Y%m%d}.csv",
            mime="text/csv",
        )
    with col_b:
        selected_name = st.selectbox("Generate PDF Report for", ranked_df["Name"].tolist())
        selected = next((c for c in candidates if c["name"] == selected_name), None)
        if selected and st.button("📄 Download PDF Report"):
            pdf_bytes = generate_pdf_report(selected)
            st.download_button(
                "📥 Download PDF",
                pdf_bytes,
                file_name=f"report_{selected_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )

    st.markdown("**Manage Candidates**")
    del_id = st.number_input("Candidate ID to delete", min_value=1, step=1)
    if st.button("🗑️ Delete Candidate"):
        if delete_candidate(int(del_id)):
            st.success("Candidate deleted.")
            st.rerun()
        else:
            st.error("Candidate not found.")


# ---------------------------------------------------------------------------
# Page: Analytics
# ---------------------------------------------------------------------------

def page_analytics():
    """Render analytics dashboard with interactive charts."""
    st.markdown('<p class="section-header">📈 Analytics</p>', unsafe_allow_html=True)

    candidates = get_all_candidates()
    if not candidates:
        st.info("No data available. Upload resumes and job descriptions first.")
        return

    metrics = compute_dashboard_metrics(candidates)
    match_stats = compute_match_analytics(candidates)

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Avg Skill Match", match_stats["avg_skill_match"], "%")
    with col2:
        render_metric_card("Avg Keyword Match", match_stats["avg_keyword_match"], "%")
    with col3:
        render_metric_card("Avg Semantic Score", match_stats["avg_semantic_score"], "%")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Scores", "🛠️ Skills", "👥 Experience", "🔀 Comparison"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                create_score_distribution_chart(metrics["score_distribution"]),
                use_container_width=True,
            )
        with c2:
            st.plotly_chart(
                create_recommendation_pie_chart(metrics["recommendation_distribution"]),
                use_container_width=True,
            )

    with tab2:
        st.plotly_chart(
            create_skill_bar_chart(metrics["skill_distribution"]),
            use_container_width=True,
        )

    with tab3:
        st.plotly_chart(
            create_experience_histogram(metrics["experience_distribution"]),
            use_container_width=True,
        )

    with tab4:
        ranked = rank_candidates(candidates)
        st.plotly_chart(
            create_match_comparison_chart(ranked),
            use_container_width=True,
        )

        st.markdown("**Individual Candidate Radar**")
        names = [c["name"] for c in ranked]
        selected = st.selectbox("Select Candidate", names)
        candidate = next(c for c in ranked if c["name"] == selected)
        from modules.analytics import get_candidate_score_breakdown
        breakdown = get_candidate_score_breakdown(candidate)
        st.plotly_chart(create_radar_chart(breakdown, f"{selected} — Score Breakdown"), use_container_width=True)


# ---------------------------------------------------------------------------
# Page: Resume Feedback
# ---------------------------------------------------------------------------

def page_feedback():
    """Render resume feedback and improvement suggestions."""
    st.markdown('<p class="section-header">💡 Resume Feedback</p>', unsafe_allow_html=True)

    candidates = get_all_candidates()
    if not candidates:
        st.info("No candidates available. Upload resumes first.")
        return

    selected_name = st.selectbox("Select Candidate", [c["name"] for c in candidates])
    candidate = next(c for c in candidates if c["name"] == selected_name)

    jobs = get_all_job_descriptions()
    jd = next((j for j in jobs if j["id"] == candidate.get("job_id")), jobs[0] if jobs else None)

    if not jd:
        st.warning("No job description linked.")
        return

    if st.button("🔍 Analyze Resume", type="primary"):
        with st.spinner("Analyzing resume..."):
            feedback = generate_resume_feedback(candidate, jd)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    create_gauge_chart(candidate.get("ats_score", 0), "ATS Score"),
                    use_container_width=True,
                )
            with col2:
                length = feedback["length_analysis"]
                st.metric("Word Count", length["word_count"])
                st.metric("Length Status", length["status"])
                st.info(length["feedback"])

            if feedback["missing_skills"]:
                st.error("**Missing Skills:** " + ", ".join(feedback["missing_skills"]))
            if feedback["missing_keywords"]:
                st.warning("**Missing Keywords:** " + ", ".join(feedback["missing_keywords"][:8]))

            if feedback["weak_sections"]:
                st.markdown("**Weak Sections**")
                for item in feedback["weak_sections"]:
                    st.markdown(f"- ⚠️ {item}")

            if feedback["grammar_issues"]:
                st.markdown("**Grammar & Style**")
                for item in feedback["grammar_issues"]:
                    st.markdown(f"- ✏️ {item}")

            if feedback["project_suggestions"]:
                st.markdown("**Project Suggestions**")
                for item in feedback["project_suggestions"]:
                    st.markdown(f"- 💡 {item}")

            st.markdown("**General Tips**")
            for tip in feedback["overall_tips"]:
                st.markdown(f"- ✅ {tip}")


# ---------------------------------------------------------------------------
# Page: Interview Questions
# ---------------------------------------------------------------------------

def page_interview():
    """Render interview question generator page."""
    st.markdown('<p class="section-header">🎤 Interview Questions</p>', unsafe_allow_html=True)

    candidates = get_all_candidates()
    if not candidates:
        st.info("No candidates available.")
        return

    col1, col2 = st.columns(2)
    with col1:
        selected_name = st.selectbox("Select Candidate", [c["name"] for c in candidates])
    with col2:
        difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

    candidate = next(c for c in candidates if c["name"] == selected_name)

    if st.button("🎯 Generate Questions", type="primary"):
        with st.spinner("Generating tailored interview questions..."):
            questions = generate_interview_questions(candidate, difficulty.lower())

            for category, q_list in questions.items():
                st.markdown(f"### {category}")
                for i, q in enumerate(q_list, 1):
                    st.markdown(f"**Q{i}.** {q}")
                st.markdown("---")


# ---------------------------------------------------------------------------
# Page: About
# ---------------------------------------------------------------------------

def page_about():
    """Render about page with project information."""
    st.markdown('<p class="section-header">ℹ️ About Smart Resume Screener</p>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 Project Overview
    **Smart Resume Screening and Candidate Ranking Tool** is an AI-powered ATS-inspired
    application built for the **IBM AI Internship**. It automates resume analysis,
    job-resume matching, candidate ranking, and interview preparation.

    ### ✨ Key Features
    - **Resume Parsing** — Extract name, skills, experience, education, and more
    - **Job Description Analysis** — Parse required/preferred skills and keywords
    - **AI Matching Engine** — TF-IDF, Cosine Similarity, Sentence Transformers
    - **ATS Scoring** — Weighted 100-point score with visual indicators
    - **Candidate Ranking** — Automatic ranking with recommendations
    - **Resume Feedback** — Actionable improvement suggestions
    - **Interview Generator** — Tailored questions by difficulty level
    - **Analytics Dashboard** — Interactive charts and metrics

    ### 🏗️ Architecture
    ```
    Streamlit UI → Resume/JD Parser → AI Matching Engine → ATS Scorer
         ↓              ↓                    ↓                  ↓
    SQLite DB    Skill Matcher    Sentence Transformers   Ranker
    ```

    ### 🛠️ Tech Stack
    Python 3.11+ | Streamlit | SQLite | scikit-learn | spaCy |
    Sentence Transformers | Plotly | Pandas | PyPDF2 | pdfplumber

    ### 📊 ATS Score Weights
    | Component | Weight |
    |-----------|--------|
    | Skill Match | 40% |
    | Experience | 20% |
    | Education | 15% |
    | Projects | 10% |
    | Certifications | 10% |
    | Resume Quality | 5% |

    ---
    Built with ❤️ for IBM AI Internship | MIT License
    """)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main():
    """Main application entry point with sidebar navigation."""
    initialize_database()
    init_session_state()

    st.sidebar.markdown("## 📋 Smart Resume Screener")
    st.sidebar.markdown("*IBM AI Internship Project*")
    st.sidebar.markdown("---")

    pages = {
        "📊 Dashboard": page_dashboard,
        "📄 Upload Resume": page_upload_resume,
        "💼 Upload Job Description": page_upload_jd,
        "🏅 Candidate Ranking": page_ranking,
        "📈 Analytics": page_analytics,
        "💡 Resume Feedback": page_feedback,
        "🎤 Interview Questions": page_interview,
        "ℹ️ About": page_about,
    }

    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    st.sidebar.markdown("---")

    count = get_candidate_count()
    avg = get_average_ats_score()
    st.sidebar.metric("Candidates", count)
    st.sidebar.metric("Avg ATS Score", f"{avg}%")

    pages[selection]()


if __name__ == "__main__":
    main()
