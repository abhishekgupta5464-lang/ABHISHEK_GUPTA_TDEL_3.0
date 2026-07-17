"""
Interview question generator for Smart Resume Screener.
Generates tailored questions based on skills, projects, and experience.
"""

import random
from typing import Any, Dict, List


SKILL_QUESTIONS = {
    "python": {
        "beginner": [
            "What are Python lists vs tuples? When would you use each?",
            "Explain the difference between append() and extend() in Python.",
            "How do you handle exceptions in Python?",
        ],
        "intermediate": [
            "Explain Python decorators and provide a use case.",
            "What are generators and when would you prefer them over lists?",
            "How does Python's GIL affect multithreading?",
        ],
        "advanced": [
            "Design a Python context manager for database connection pooling.",
            "Explain metaclasses in Python and when you would use them.",
            "How would you optimize memory usage in a large-scale Python application?",
        ],
    },
    "machine learning": {
        "beginner": [
            "What is the difference between supervised and unsupervised learning?",
            "Explain overfitting and how to prevent it.",
            "What is cross-validation and why is it important?",
        ],
        "intermediate": [
            "Compare Random Forest and Gradient Boosting algorithms.",
            "How do you handle imbalanced datasets in classification?",
            "Explain the bias-variance tradeoff with examples.",
        ],
        "advanced": [
            "Design an ML pipeline for real-time fraud detection.",
            "How would you deploy and monitor an ML model in production?",
            "Explain attention mechanisms and their role in transformers.",
        ],
    },
    "sql": {
        "beginner": [
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "Explain primary keys and foreign keys.",
            "Write a query to find duplicate records in a table.",
        ],
        "intermediate": [
            "Explain window functions with a practical example.",
            "How would you optimize a slow-running SQL query?",
            "What are indexes and when should you avoid using them?",
        ],
        "advanced": [
            "Design a database schema for an e-commerce platform.",
            "Explain query execution plans and how to read them.",
            "How would you handle database sharding at scale?",
        ],
    },
    "react": {
        "beginner": [
            "What is the difference between state and props in React?",
            "Explain the React component lifecycle.",
            "What are React hooks and name a few commonly used ones.",
        ],
        "intermediate": [
            "Explain React Context API and when to use it vs Redux.",
            "How does React's virtual DOM improve performance?",
            "What are custom hooks and how do you create one?",
        ],
        "advanced": [
            "How would you optimize rendering performance in a large React app?",
            "Explain React Server Components and their benefits.",
            "Design a scalable state management architecture for a React application.",
        ],
    },
    "aws": {
        "beginner": [
            "What is the difference between EC2 and Lambda?",
            "Explain S3 storage classes and their use cases.",
            "What is an IAM role and why is it important?",
        ],
        "intermediate": [
            "Design a highly available architecture using AWS services.",
            "How would you set up CI/CD pipeline using AWS CodePipeline?",
            "Explain VPC, subnets, and security groups.",
        ],
        "advanced": [
            "Design a multi-region disaster recovery strategy on AWS.",
            "How would you optimize AWS costs for a growing startup?",
            "Explain AWS Well-Architected Framework pillars.",
        ],
    },
    "docker": {
        "beginner": [
            "What is a Docker container vs a virtual machine?",
            "Explain Dockerfile and its common instructions.",
            "What is docker-compose and when would you use it?",
        ],
        "intermediate": [
            "How do you optimize Docker image size?",
            "Explain Docker networking modes.",
            "How would you manage secrets in Docker containers?",
        ],
        "advanced": [
            "Design a container orchestration strategy for microservices.",
            "How do you implement zero-downtime deployments with Docker?",
            "Explain container security best practices.",
        ],
    },
}

GENERAL_QUESTIONS = {
    "beginner": [
        "Tell me about yourself and your background.",
        "Why are you interested in this role?",
        "Describe a project you are most proud of.",
        "How do you approach learning new technologies?",
        "What are your strengths and areas for improvement?",
    ],
    "intermediate": [
        "Describe a challenging technical problem you solved.",
        "How do you prioritize tasks when working on multiple projects?",
        "Tell me about a time you had to learn a technology quickly.",
        "How do you handle disagreements with team members?",
        "Describe your experience with agile development methodologies.",
    ],
    "advanced": [
        "Design a system to handle 1 million concurrent users.",
        "How would you lead a team through a major technical migration?",
        "Describe a time you made a technical decision that had business impact.",
        "How do you balance technical debt with feature delivery?",
        "Explain how you would architect a real-time analytics platform.",
    ],
}

EXPERIENCE_QUESTIONS = {
    "beginner": [
        "Walk me through your most recent project or internship.",
        "What tools and technologies did you use in your academic projects?",
    ],
    "intermediate": [
        "Describe your role and contributions in your previous position.",
        "What was the most complex feature you built and how did you approach it?",
    ],
    "advanced": [
        "Tell me about a system you architected from scratch.",
        "How have you mentored junior developers in your previous roles?",
    ],
}


def _match_skill_category(skill: str) -> str:
    """Map a skill name to a question category key."""
    skill_lower = skill.lower()
    for category in SKILL_QUESTIONS:
        if category in skill_lower or skill_lower in category:
            return category
    return ""


def generate_skill_questions(
    skills: List[str],
    difficulty: str = "intermediate",
    count: int = 5,
) -> List[str]:
    """Generate interview questions based on candidate skills and difficulty."""
    questions = []
    difficulty = difficulty.lower()

    for skill in skills:
        category = _match_skill_category(skill)
        if category and category in SKILL_QUESTIONS:
            pool = SKILL_QUESTIONS[category].get(difficulty, [])
            if pool:
                questions.extend(random.sample(pool, min(2, len(pool))))

    if len(questions) < count:
        general = GENERAL_QUESTIONS.get(difficulty, [])
        questions.extend(random.sample(general, min(count - len(questions), len(general))))

    random.shuffle(questions)
    return questions[:count]


def generate_project_questions(
    projects: List[str],
    difficulty: str = "intermediate",
    count: int = 3,
) -> List[str]:
    """Generate interview questions based on candidate projects."""
    if not projects:
        return []

    questions = []
    templates = {
        "beginner": [
            "Walk me through the architecture of '{project}'.",
            "What was your specific contribution to '{project}'?",
            "What challenges did you face while building '{project}'?",
        ],
        "intermediate": [
            "What design decisions did you make in '{project}' and why?",
            "How would you scale '{project}' to handle more users?",
            "What would you do differently if you rebuilt '{project}' today?",
        ],
        "advanced": [
            "Analyze the trade-offs in your '{project}' architecture.",
            "How did you ensure reliability and performance in '{project}'?",
            "What metrics would you track for '{project}' in production?",
        ],
    }

    diff_templates = templates.get(difficulty.lower(), templates["intermediate"])
    for project in projects[:3]:
        short_proj = project[:60] + "..." if len(project) > 60 else project
        template = random.choice(diff_templates)
        questions.append(template.format(project=short_proj))

    return questions[:count]


def generate_experience_questions(
    experience: List[str],
    total_years: float,
    difficulty: str = "intermediate",
) -> List[str]:
    """Generate questions based on work experience level."""
    if total_years >= 5:
        diff = "advanced"
    elif total_years >= 2:
        diff = "intermediate"
    else:
        diff = "beginner"

    if difficulty.lower() in ("beginner", "intermediate", "advanced"):
        diff = difficulty.lower()

    pool = EXPERIENCE_QUESTIONS.get(diff, [])
    questions = list(pool)

    if experience:
        questions.append(
            f"Based on your experience, describe a situation where you "
            f"demonstrated leadership or initiative."
        )

    return questions[:4]


def generate_interview_questions(
    resume_data: Dict[str, Any],
    difficulty: str = "intermediate",
    total_count: int = 15,
) -> Dict[str, List[str]]:
    """
    Generate a complete set of interview questions organized by category.
    Categories: General, Skills, Projects, Experience, Behavioral.
    """
    skills = resume_data.get("skills", [])
    projects = resume_data.get("projects", [])
    experience = resume_data.get("experience", [])
    total_years = resume_data.get("total_experience", 0)

    skill_qs = generate_skill_questions(skills, difficulty, count=6)
    project_qs = generate_project_questions(projects, difficulty, count=4)
    exp_qs = generate_experience_questions(experience, total_years, difficulty)

    behavioral = [
        "Describe a time you failed and what you learned from it.",
        "How do you handle tight deadlines and pressure?",
        "Tell me about a time you collaborated with a cross-functional team.",
        "Give an example of when you went above and beyond expectations.",
        "How do you stay updated with industry trends and new technologies?",
    ]

    general = GENERAL_QUESTIONS.get(difficulty.lower(), GENERAL_QUESTIONS["intermediate"])
    general_selected = random.sample(general, min(3, len(general)))

    all_questions = {
        "General Questions": general_selected,
        "Technical Skills": skill_qs,
        "Project Deep-Dive": project_qs,
        "Experience Based": exp_qs,
        "Behavioral": random.sample(behavioral, min(3, len(behavioral))),
    }

    return all_questions
