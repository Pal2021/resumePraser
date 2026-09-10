from resume_service import ResumeTailoringService


class ResumeApplication:
    def __init__(self, tailoring: ResumeTailoringService):
        self._tailoring = tailoring

    def generate_stream(self, jd_text: str, resume_text: str):
        """Yields (output_tex, status_message) tuples."""
        yield "", "⏳ Reading your inputs…"

        jd = (jd_text or "").strip()
        resume = (resume_text or "").strip()

        if not jd:
            raise ValueError("Please paste a Job Description.")
        if not resume:
            raise ValueError("Please paste your Overleaf / LaTeX resume.")

        yield "", "🚀 Sending inputs to GPT-5…"

        streamed: list[str] = []
        for token in self._tailoring.tailor_stream(jd, resume):
            streamed.append(token)
            yield "".join(streamed), "✍️ GPT-5 is tailoring your resume…"

        result = self._tailoring.clean("".join(streamed))
        self._tailoring.validate_structure(resume, result)

        yield result, "✅ Done! Your tailored Overleaf LaTeX resume is ready."
