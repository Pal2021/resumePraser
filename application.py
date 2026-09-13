from typing import Iterator

from resume_service import ResumeTailoringService


class ResumeApplication:
    def __init__(self, tailoring: ResumeTailoringService) -> None:
        self._tailoring = tailoring

    def generate_stream(
        self,
        jd_text: str,
        resume_text: str,
        extra_skills: str = "",
    ) -> Iterator[tuple[str, str]]:
        yield "", "⏳ Reading your inputs…"

        jd = (jd_text or "").strip()
        resume = (resume_text or "").strip()
        extra = (extra_skills or "").strip()

        if not jd:
            raise ValueError("Please paste a Job Description.")
        if not resume:
            raise ValueError("Please paste your Overleaf / LaTeX resume.")

        yield "", "🚀 Analyzing job description and tailoring your resume…"

        yield from self._tailoring.tailor_stream(jd, resume, extra)