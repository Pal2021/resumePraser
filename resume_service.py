import re
from typing import Iterator

from llm_client import LLM


class ResumeTailoringService:
    ALLOWED_SECTIONS = (
        "Skills",
        "Experience",
        "Projects",
        "Achievements & Certifications",
        "Education",
    )

    SYSTEM_PROMPT = """\
You are an expert ATS resume editor specializing in Overleaf LaTeX resumes.
Tailor the user's resume to match the Job Description while strictly obeying
EVERY constraint below.

ABSOLUTE RULES — ZERO EXCEPTIONS:

1. STRICT STRUCTURE PRESERVATION:
   - The output MUST contain ONLY the sections present in the source resume,
     in the EXACT same order.
   - Allowed sections: Skills | Experience | Projects | Achievements & Certifications | Education
   - NEVER add "Summary", "Profile", "Objective", "About Me", "References",
     or ANY other new section.

2. SECTION-SPECIFIC MODIFICATION RULES:
   - SKILLS: You MAY add or reorder skills to align with the JD, but only
     skills evidenced by the source resume.
   - EXPERIENCE: Make ONLY minimal, subtle keyword-alignment edits.
     Do NOT rewrite entire bullet points. Do NOT change employers, titles,
     dates, or metrics.
   - PROJECTS: Add JD-relevant keywords ONLY when supported by existing
     project details. Never fabricate.
   - ACHIEVEMENTS & CERTIFICATIONS: Keep EXACTLY as provided — zero changes.
   - EDUCATION: Keep EXACTLY as provided — zero changes.

3. FACTUAL INTEGRITY:
   - NEVER invent experience, skills, certifications, dates, employers,
     or metrics.

4. OUTPUT FORMAT:
   - Output MUST be valid, compile-ready Overleaf LaTeX (.tex).
   - Preserve packages, formatting macros, and document structure from source.
   - Return ONLY the raw LaTeX code — no markdown fences, no commentary.
"""

    def __init__(self, llm: LLM):
        self._llm = llm

    def tailor_stream(self, job_description: str, resume: str) -> Iterator[str]:
        if not job_description.strip():
            raise ValueError("Please provide a job description.")
        if not resume.strip():
            raise ValueError("Please provide a resume.")

        prompt = f"""The source is an Overleaf LaTeX (.tex) resume.

JOB DESCRIPTION:
{job_description.strip()}

SOURCE RESUME:
{resume.strip()}

Generate the tailored resume now in clean Overleaf LaTeX (.tex) format.
Return ONLY the LaTeX code ready for Overleaf."""
        yield from self._llm.stream(self.SYSTEM_PROMPT, prompt)

    @staticmethod
    def clean(text: str) -> str:
        cleaned = re.sub(r"^```(?:latex|tex|text)?\s*", "", text.strip(), flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.I)
        return cleaned.strip()

    @classmethod
    def _sections(cls, text: str) -> list[str]:
        aliases = {
            "skills": "skills",
            "technical skills": "skills",
            "experience": "experience",
            "work experience": "experience",
            "professional experience": "experience",
            "projects": "projects",
            "achievements & certifications": "achievements & certifications",
            "achievements and certifications": "achievements & certifications",
            "certifications": "achievements & certifications",
            "education": "education",
        }
        headings: list[str] = []
        for line in text.splitlines():
            latex_match = re.search(r"\\(?:sub)?section\*?\{([^}]+)\}", line)
            normalized = latex_match.group(1) if latex_match else line
            normalized = normalized.replace(r"\&", "&")
            normalized = re.sub(r"^[^A-Za-z&]+|[^A-Za-z&]+$", "", normalized).strip().lower()
            if normalized in aliases:
                canonical = aliases[normalized]
                if not headings or headings[-1] != canonical:
                    headings.append(canonical)
        return headings

    @classmethod
    def validate_structure(cls, source: str, output: str) -> None:
        prohibited = ["summary", "professional summary", "profile", "objective", "about me"]
        output_lower = output.lower()
        for forbidden in prohibited:
            if f"\\section{{{forbidden}}}" in output_lower or f"\\section*{{{forbidden}}}" in output_lower:
                raise ValueError(
                    f"Strict rule violated: '{forbidden.capitalize()}' section was added."
                )
