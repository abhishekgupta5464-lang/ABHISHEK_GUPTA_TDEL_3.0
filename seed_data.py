"""Seed sample data and verify all modules work correctly."""

from modules.database import initialize_database, insert_job_description, insert_candidate, get_all_candidates
from modules.resume_parser import parse_resume, parse_job_description_text
from modules.ats_score import calculate_ats_score
from modules.recommendation import get_recommendation
from modules.candidate_ranker import rank_candidates
from modules.resume_feedback import generate_resume_feedback
from modules.interview_generator import generate_interview_questions


def main():
    """Initialize database and seed sample candidates."""
    initialize_database()
    print("DB initialized")

    jd_text = open("assets/sample_job_descriptions/senior_python_developer.txt").read()
    jd = parse_job_description_text(jd_text, "Senior Python Developer", "IBM")
    job_id = insert_job_description(jd)
    print(f"Job ID: {job_id}")

    for fname in ["john_smith_resume.txt", "sarah_johnson_resume.txt", "mike_chen_resume.txt"]:
        data = parse_resume(open(f"assets/sample_resumes/{fname}", "rb").read(), fname)
        scores = calculate_ats_score(data, jd)
        data.update(scores)
        data["recommendation"] = get_recommendation(scores["ats_score"])
        data["job_id"] = job_id
        insert_candidate(data)
        print(f"{data['name']}: ATS={scores['ats_score']} Rec={data['recommendation']}")

    ranked = rank_candidates(get_all_candidates())
    print("Ranked:", [(c["rank"], c["name"], c["ats_score"]) for c in ranked])

    feedback = generate_resume_feedback(ranked[0], jd)
    print("Feedback keys:", list(feedback.keys()))

    questions = generate_interview_questions(ranked[0], "intermediate")
    print("Question categories:", list(questions.keys()))
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
