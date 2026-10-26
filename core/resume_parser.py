"""
Resume Parser & Custom Interview Question Generator.
Parses PDF and plain text resumes, extracts key skills, technologies, and experience,
and generates tailored interview questions matching job descriptions.
"""

import re
import io
from typing import Dict, List, Any, Optional
from pathlib import Path

# Common skill taxonomies
KNOWN_SKILLS = {
    "Languages": ["Python", "Java", "C++", "Go", "Golang", "TypeScript", "JavaScript", "Rust", "SQL", "R", "Bash"],
    "NLP & AI": ["Transformers", "PyTorch", "TensorFlow", "spaCy", "NLTK", "Hugging Face", "LLMs", "RAG", "BERT", "GPT", "Tokenization", "LoRA", "QLoRA", "Whisper", "LangChain"],
    "Web & Backend": ["FastAPI", "Flask", "Django", "Node.js", "Express", "React", "REST", "gRPC", "GraphQL", "WebSockets"],
    "Databases & Cloud": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Kafka", "Celery", "Terraform", "CI/CD"]
}


class ResumeParser:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extracts text from uploaded PDF file using pypdf."""
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_file)
            text_parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            return "\n".join(text_parts)
        except Exception as e:
            return f"Error reading PDF: {e}"

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parses resume text into structured skills, experience bullet points, and domains."""
        if not text or not text.strip():
            return {"skills": {}, "experience_points": [], "detected_domains": []}

        text_lower = text.lower()
        extracted_skills = {}

        for category, skill_list in KNOWN_SKILLS.items():
            matched = []
            for skill in skill_list:
                pat = rf'\b{re.escape(skill.lower())}\b'
                if re.search(pat, text_lower):
                    matched.append(skill)
            if matched:
                extracted_skills[category] = matched

        # Extract experience bullet points (lines starting with - or * or •)
        bullet_points = []
        for line in text.split("\n"):
            line_str = line.strip()
            if re.match(r'^[-*•]\s+', line_str):
                cleaned = re.sub(r'^[-*•]\s+', '', line_str)
                if len(cleaned) > 20:
                    bullet_points.append(cleaned)

        # Detect candidate's top domains
        domains = []
        if extracted_skills.get("NLP & AI"):
            domains.append("Computational Linguistics & NLP")
        if extracted_skills.get("Web & Backend") or extracted_skills.get("Databases & Cloud"):
            domains.append("Software Engineering")
        if "AWS" in str(extracted_skills) or "Kubernetes" in str(extracted_skills) or "Kafka" in str(extracted_skills):
            domains.append("System Design")
        if not domains:
            domains.append("Software Engineering")

        return {
            "skills": extracted_skills,
            "experience_points": bullet_points[:8],
            "detected_domains": list(set(domains))
        }

    def generate_tailored_questions(
        self,
        resume_data: Dict[str, Any],
        job_description: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes personalized interview questions based on parsed resume skills and job requirements.
        """
        questions = []
        q_idx = 1

        all_skills = [s for sublist in resume_data.get("skills", {}).values() for s in sublist]

        # 1. Experience deep-dive question based on bullet points
        exp_points = resume_data.get("experience_points", [])
        if exp_points:
            best_bullet = exp_points[0]
            questions.append({
                "id": f"tailored_{q_idx:02d}",
                "category": "Experience Deep Dive",
                "difficulty": "Mid",
                "question": f"In your resume, you highlighted: '{best_bullet[:140]}...'. Can you walk me through the key technical hurdles you overcame during this implementation and how you validated the outcome?",
                "keywords": ["challenge", "architecture", "validation", "metrics", "trade-offs"],
                "expected_concepts": ["Clear problem context", "Specific technical decisions made", "Measurable impact and lessons learned"]
            })
            q_idx += 1

        # 2. Technology specialization question
        if "NLP & AI" in resume_data.get("skills", {}):
            top_tech = resume_data["skills"]["NLP & AI"][:2]
            tech_str = " and ".join(top_tech)
            questions.append({
                "id": f"tailored_{q_idx:02d}",
                "category": "Computational Linguistics & NLP",
                "difficulty": "Senior",
                "question": f"You have hands-on experience with {tech_str}. How do you approach latency vs. accuracy trade-offs when serving models using these frameworks in production?",
                "keywords": ["quantization", "batching", "caching", "throughput", "vram", "latency"],
                "expected_concepts": ["Knowledge of model optimization", "Inference serving bottlenecks", "Production monitoring"]
            })
            q_idx += 1
        elif "Web & Backend" in resume_data.get("skills", {}):
            top_tech = resume_data["skills"]["Web & Backend"][:2]
            tech_str = " and ".join(top_tech)
            questions.append({
                "id": f"tailored_{q_idx:02d}",
                "category": "Software Engineering",
                "difficulty": "Mid",
                "question": f"Looking at your proficiency with {tech_str}, how do you ensure zero-downtime deployments and handle backward-compatible API versioning?",
                "keywords": ["blue-green", "canary", "versioning", "migration", "backward compatibility"],
                "expected_concepts": ["Deployment patterns", "Schema migration safety", "API contract preservation"]
            })
            q_idx += 1

        # 3. Behavioral question tailored to leadership and collaboration
        questions.append({
            "id": f"tailored_{q_idx:02d}",
            "category": "Behavioral & HR",
            "difficulty": "Mid",
            "question": "Tell me about a time when a critical dependency or third-party service failed unexpectedly right before a project release. How did you adapt your plan and communicate with stakeholders?",
            "keywords": ["situation", "task", "action", "result", "communication", "mitigation", "resilience"],
            "expected_concepts": ["STAR framing", "Calm triage and contingency planning", "Proactive stakeholder management"]
        })
        q_idx += 1

        # 4. Job Description alignment question if JD is supplied
        if job_description and len(job_description.strip()) > 30:
            questions.append({
                "id": f"tailored_{q_idx:02d}",
                "category": "Target Role Alignment",
                "difficulty": "Senior",
                "question": "Based on our job requirements and your background, what do you see as your biggest competitive strength for this role, and where do you anticipate your steepest learning curve?",
                "keywords": ["alignment", "self-awareness", "growth mindset", "impact", "strengths"],
                "expected_concepts": ["Honest self-awareness", "Mapping personal skills to company goals", "Concrete plan to bridge skill gaps"]
            })

        return questions
