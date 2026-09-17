import re
from typing import Iterator

from llm_client import LLM


# --- Always-on AI skills offered to the model -----------------------------

DEFAULT_AI_SKILLS = (
    "Artificial Intelligence, Generative AI, Machine Learning, LLMs, "
    "Prompt Engineering, Azure OpenAI, Spring AI, LangChain, RAG, "
    "Vector Databases, "
    
    # --- Core Data Science & ML Gaps ---
    "NumPy, Pandas, Scikit-learn, PyTorch, TensorFlow, NLP, Deep Learning, "
    "Transformers, Probability & Statistics, Model Evaluation, Hallucination Reduction, Embeddings, "
    # --- Backend/API Gaps ---
    "FastAPI, Flask, "
    # --- Agentic & Advanced AI Gaps ---
    "LangGraph, AutoGen, CrewAI, Multi-step Agent Workflows, Reasoning Loops, Agent Memory, "
    # --- Database Gaps ---
    "ChromaDB, FAISS, NoSQL, "
    # --- Cloud/Deployment Gaps ---
    "AWS, GCP, Azure, "
    # --- Business Automation & Domain Gaps ---
    "Automation Workflows, Recommendation Systems, Optimization Engines, "
    "Computer Vision Systems, ROI Optimization"
)


# --- Skills that get trimmed if the output is too long --------------------
# Order matters: earlier items are removed first.
# An item is only removed if it does NOT appear in the JD.

TRIM_PRIORITY_SKILLS = [
    # Tier 1 — user's explicit examples
    "Postman",
    "Swagger",
    "Maven",
    "Gradle",
    # Tier 2 — QA/test tooling (dev roles usually don't need these listed)
    "Test Plan Development",
    "Test Case Design",
    "Functional Testing",
    "Regression Testing",
    "Integration Testing",
    "API Testing",
    "Defect Tracking",
    "Bug Tracking",
    # Tier 3 — soft/buzzword items
    "Agile and Scrum",
    "Source Code Control (Git)",
    # Tier 4 — extra DBs / infra
    "Neo4j",
    "MongoDB",
    "Apache Kafka",
    "Kafka",
    "MySQL",
    # Tier 5 — frameworks that only matter if JD names them
    "Hibernate",
    "JPA",
    "JWT",
    "Jenkins",
    "GitHub Actions",
    # Tier 6 — last resort
    "C++",
    "JavaScript",
]


# --- LaTeX section parsing ------------------------------------------------

SECTION_MACROS = (
    "section", "subsection", "subsubsection",
    "cvsection", "cvsubsection", "rSection",
    "resumeSection", "heading", "Heading",
)

SECTION_PATTERN = re.compile(
    r"\\(" + "|".join(SECTION_MACROS) + r")\*?\s*\{([^{}]*)\}",
    re.MULTILINE,
)

ALIASES = {
    "skills": "skills", "technical skills": "skills", "technologies": "skills",
    "experience": "experience", "work experience": "experience",
    "professional experience": "experience", "relevant experience": "experience",
    "projects": "projects", "personal projects": "projects",
    "achievements & certifications": "achievements & certifications",
    "achievements and certifications": "achievements & certifications",
    "achievements": "achievements & certifications",
    "certifications": "achievements & certifications",
    "education": "education",
}

PROTECTED_SECTIONS = {"achievements & certifications", "education"}

FORBIDDEN_SECTION_WORDS = {
    "summary", "professional summary", "profile", "objective",
    "career objective", "about me", "about",
}

MATHMODE_PATTERNS = (
    (re.compile(r"\\\((\d+(?:\.\d+)?)\s*\\?%\s*\\\)"), r"\1\\%"),
    (re.compile(r"\\\((\d+(?:\.\d+)?)\s*\+\s*\\\)"), r"\1+"),
    (re.compile(r"\\\(\\mathrm\{([^}]+)\}\\\)"), r"\1"),
    (re.compile(r"\\\(\\text\{([^}]+)\}\\\)"), r"\1"),
    (re.compile(r"\\\(([A-Za-z0-9\+\-\s\.,:;!?/%]+)\\\)"), r"\1"),
)


# --- Known multi-word tech phrases used when matching JD -------------------

JD_PHRASES = [
    "spring boot", "springboot", "spring security", "spring ai", "spring",
    "restful api", "restful apis", "rest api", "rest apis",
    "microservices", "microservice",
    "system design", "object oriented", "oop",
    "data structures", "algorithms", "dsa",
    "machine learning", "generative ai", "artificial intelligence",
    "large language model", "large language models", "llm", "llms",
    "rag", "retrieval augmented generation", "vector database", "vector databases",
    "prompt engineering", "langchain", "azure openai", "openai", "gpt",
    "ci/cd", "cicd", "continuous integration", "continuous deployment",
    "github actions", "jenkins",
    "test case", "test plan", "unit test", "integration test",
    "api testing", "regression testing", "functional testing",
    "defect", "bug tracking", "junit", "mockito",
    "postman", "swagger", "maven", "gradle",
    "docker", "kubernetes", "kafka", "apache kafka",
    "mysql", "postgresql", "mongodb", "neo4j",
    "hibernate", "jpa", "jwt", "sql", "nosql",
    "agile", "scrum", "git", "github",
    "python", "java", "javascript", "c++", "c#",
]


# --- Helpers --------------------------------------------------------------

def _normalize_section_name(name: str) -> str:
    cleaned = name.replace(r"\&", "&").replace("&amp;", "&")
    cleaned = re.sub(r"\\[a-zA-Z]+\*?", "", cleaned)
    cleaned = re.sub(r"[^A-Za-z& ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return ALIASES.get(cleaned, cleaned)


def extract_sections(tex: str) -> list[str]:
    sections: list[str] = []
    for m in SECTION_PATTERN.finditer(tex):
        name = _normalize_section_name(m.group(2))
        if name:
            sections.append(name)
    return sections


def extract_section_bodies(tex: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(tex))
    bodies: dict[str, str] = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tex)
        name = _normalize_section_name(m.group(2))
        if not name:
            continue
        body = tex[start:end].strip()
        bodies[name] = bodies.get(name, "") + ("\n" if name in bodies else "") + body
    return bodies


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _brace_balance(tex: str) -> bool:
    depth, i, n = 0, 0, len(tex)
    while i < n:
        c = tex[i]
        if c == "\\" and i + 1 < n:
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def _extract_latex_block(text: str) -> str:
    text = (text or "").strip()
    fence = re.search(
        r"```(?:latex|tex|text)?\s*\n(.*?)```", text,
        flags=re.DOTALL | re.I,
    )
    if fence:
        text = fence.group(1).strip()
    else:
        text = re.sub(r"^```(?:latex|tex|text)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```\s*$", "", text, flags=re.I).strip()

    start = text.find("\\documentclass")
    if start != -1:
        text = text[start:]
    end = text.rfind("\\end{document}")
    if end != -1:
        text = text[: end + len("\\end{document}")]
    return text.strip()


def _fix_mathmode(text: str) -> str:
    for pattern, repl in MATHMODE_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def _estimate_length(tex: str) -> int:
    start = tex.find("\\begin{document}")
    end = tex.find("\\end{document}")
    if start == -1:
        return len(tex)
    if end == -1:
        end = len(tex)
    body = tex[start:end]
    body = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", body)
    body = re.sub(r"\s+", " ", body)
    return len(body.strip())


def _extract_jd_terms(jd: str) -> set[str]:
    jd_lower = jd.lower()
    terms: set[str] = set()
    for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.]{1,}", jd_lower):
        terms.add(w)
    for p in JD_PHRASES:
        if p in jd_lower:
            terms.add(p)
    return terms


def _term_matches_jd(term: str, jd_terms: set[str], jd_lower: str) -> bool:
    t = term.strip().lower()
    t = t.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_")
    t = re.sub(r"\\[a-zA-Z]+", "", t).strip(" .,;:")
    if not t:
        return False
    if t in jd_lower:
        return True
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.]{1,}", t) if len(w) >= 2]
    if not words:
        return False
    return any(w in jd_terms for w in words)


def _skills_section_span(tex: str):
    matches = list(SECTION_PATTERN.finditer(tex))
    for i, m in enumerate(matches):
        name = _normalize_section_name(m.group(2))
        if name == "skills":
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(tex)
            return (start, end)
    return None


def _remove_skill_from_skills_section(tex: str, skill: str, jd: str) -> str:
    """Remove a single skill from the Skills section. No-op if skill is in JD."""
    jd_terms = _extract_jd_terms(jd)
    if _term_matches_jd(skill, jd_terms, jd.lower()):
        return tex  # JD mentions it — keep it

    span = _skills_section_span(tex)
    if not span:
        return tex

    body = tex[span[0]:span[1]]
    s = re.escape(skill)

    # Remove "…, skill" / ", skill " occurrences.
    new_body = re.sub(rf",\s*{s}\b", "", body, flags=re.I)
    # Remove "skill, …" (first item in the list).
    new_body = re.sub(rf"\b{s}\s*,\s*", "", new_body, flags=re.I)
    # Remove standalone "skill" before \\ or end (safety net).
    new_body = re.sub(rf"\b{s}(?=\s*(?:\\\\|$))", "", new_body, flags=re.I)
    # Clean up: collapse double spaces, empty items, commas followed by \\
    new_body = re.sub(r"[ \t]{2,}", " ", new_body)
    new_body = re.sub(r",\s*,", ",", new_body)
    new_body = re.sub(r",\s*(?=\\\\)", " ", new_body)

    return tex[:span[0]] + new_body + tex[span[1]:]


def _trim_skills_to_fit(tex: str, jd: str, target_len: int) -> str:
    """Iteratively remove non-JD skills until the output fits."""
    if _estimate_length(tex) <= target_len:
        return tex
    for skill in TRIM_PRIORITY_SKILLS:
        if _estimate_length(tex) <= target_len:
            break
        tex = _remove_skill_from_skills_section(tex, skill, jd)
    return tex


# --- Service --------------------------------------------------------------

class ResumeTailoringService:

    SYSTEM_PROMPT = r"""\
You are an expert ATS resume optimizer for Overleaf LaTeX resumes.

You receive a JOB DESCRIPTION, a SOURCE RESUME in LaTeX, and an APPROVED
SKILLS list. Produce the highest-ATS-scoring version of this resume that is
truthful to the source AND fits on ONE PAGE.

HARD INTEGRITY RULES:
- Every claim must be supported by the SOURCE RESUME or APPROVED SKILLS list.
- NEVER invent metrics, employers, dates, titles, projects, or certifications.
- NEVER add an experience bullet, project, or certification that isn't in source.
- Only skills from source OR APPROVED SKILLS list may appear.

WHAT TO DO:

1. PRESERVE STRUCTURE:
   - Same sections, same order, same preamble, same custom macros.
   - Same \documentclass ... \begin{document} ... \end{document} envelope.

2. ONE-PAGE RULE:
   - The final compiled PDF must fit on ONE page.
   - Output must NOT exceed the source length by more than 10%.
   - Keep each Skills category to ONE line.
   - If you add the AI \& Generative AI line, you MUST keep the rest of the
     Skills section within its original line count. Drop low-priority items
     (Postman, Swagger, Maven, Gradle, redundant test tools, extra DBs)
     unless the job description mentions them.

3. SKILLS SECTION — AGGRESSIVE ATS OPTIMIZATION:
   - Reorder so most JD-relevant items come FIRST in each line.
   - Add items from APPROVED SKILLS relevant to the JD.
   - You MUST create a new category inside Skills, labeled exactly:
     \textbf{AI \& Generative AI:}
     Place it right after "Frameworks \& Tools".
   - The AI \& Generative AI line MUST be ONE line.
   - Use JD's exact phrasing (write "Generative AI" not "GenAI").
   - Do not remove any existing skill unless it is a strict duplicate OR
     it is low-priority and not mentioned in the JD.

4. EXPERIENCE — reframe to match the JD (facts unchanged):
   - You MAY rewrite each bullet in full, but every claim must be supported
     by the source bullet.
   - Preserve employer, title, dates, every numeric metric EXACTLY.
   - Reframe toward JD vocabulary: problem definition, solution design,
     deployment readiness, functional design, requirement analysis,
     root cause analysis, shortlisting solution alternatives.
   - Each bullet must remain ONE clean sentence. Do NOT staple JD phrases
     onto the end of existing sentences.

5. PROJECTS — same as Experience: reframe bullets, keep names, stacks,
   links, and all numeric facts unchanged.

6. ACHIEVEMENTS & CERTIFICATIONS: byte-for-byte identical to source.
7. EDUCATION: byte-for-byte identical to source.

8. LATEX HYGIENE:
   - NEVER wrap plain text in math mode. Write C++, 85\%, 1000+, 15+
     directly — NOT \(\mathrm{C++}\) or \(85\%\).
   - Escape special chars: % -> \%, & -> \&, _ -> \_, # -> \#, $ -> \$.

9. OUTPUT: raw LaTeX only. No markdown fences, no commentary.
"""

    RETRY_PROMPT = """\
Your previous output violated the rules. Fix ONLY the problems below and
return the corrected LaTeX resume.

PROBLEMS:
{problems}

Return ONLY the raw LaTeX code.
"""

    MAX_ATTEMPTS = 3
    LENGTH_TOLERANCE = 1.02   # output must stay within 2% of source length

    def __init__(self, llm: LLM) -> None:
        self._llm = llm

    def tailor_stream(
        self,
        job_description: str,
        resume: str,
        extra_skills: str = "",
    ) -> Iterator[tuple[str, str]]:
        source_sections = extract_sections(resume)
        source_bodies = extract_section_bodies(resume)
        source_len = _estimate_length(resume)
        target_len = int(source_len * self.LENGTH_TOLERANCE)
        user_prompt = self._build_user_prompt(job_description, resume, extra_skills)

        problems: list[str] = []
        cleaned = ""

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            if attempt == 1:
                yield "", "✍️ Optimizing for ATS (attempt 1)…"
                prompt = user_prompt
            else:
                yield "", f"🔁 Refining (attempt {attempt})…"
                prompt = (
                    user_prompt
                    + "\n\n"
                    + self.RETRY_PROMPT.format(
                        problems="\n".join(f"- {p}" for p in problems)
                    )
                )

            raw = self._llm.complete(self.SYSTEM_PROMPT, prompt)
            cleaned = _extract_latex_block(raw)
            cleaned = _fix_mathmode(cleaned)

            # Deterministic trim: remove low-priority non-JD skills if too long.
            if _estimate_length(cleaned) > target_len:
                before = _estimate_length(cleaned)
                cleaned = _trim_skills_to_fit(cleaned, job_description, target_len)
                after = _estimate_length(cleaned)
                if after < before:
                    # Try once more with a slightly tighter target.
                    cleaned = _trim_skills_to_fit(
                        cleaned, job_description, target_len - 50
                    )

            problems = self._validate(
                cleaned, source_sections, source_bodies, source_len
            )

            if not problems:
                yield cleaned, "✅ Done! ATS-optimized, one-page resume ready."
                return

        raise ValueError(
            f"Model could not produce valid LaTeX after {self.MAX_ATTEMPTS} "
            "attempts. Last problems:\n" + "\n".join(f"- {p}" for p in problems)
        )

    @staticmethod
    def _build_user_prompt(jd: str, resume: str, extra_skills: str) -> str:
        parts = [DEFAULT_AI_SKILLS]
        if extra_skills.strip():
            parts.append(extra_skills.strip())
        approved = " | ".join(parts)

        return (
            "JOB DESCRIPTION:\n"
            f"{jd.strip()}\n\n"
            "APPROVED SKILLS "
            "(the ONLY skills you may add to the Skills section beyond the "
            "source; keep the AI category to one line):\n"
            f"{approved}\n\n"
            "SOURCE RESUME (LaTeX):\n"
            f"{resume.strip()}\n\n"
            "Return the ATS-optimized, ONE-PAGE resume as raw LaTeX only."
        )

    @classmethod
    def _validate(
        cls,
        output: str,
        source_sections: list[str],
        source_bodies: dict[str, str],
        source_len: int,
    ) -> list[str]:
        problems: list[str] = []
        if not output.strip():
            return ["Output is empty."]

        for marker in ("\\documentclass", "\\begin{document}", "\\end{document}"):
            if marker not in output:
                problems.append(f"Output is missing {marker}.")

        if not _brace_balance(output):
            problems.append("Braces { } are unbalanced.")

        out_sections = extract_sections(output)

        for sec in out_sections:
            if sec in FORBIDDEN_SECTION_WORDS and sec not in source_sections:
                problems.append(f"Forbidden new section added: '{sec}'.")

        if out_sections != source_sections:
            problems.append(
                f"Section structure changed. Expected {source_sections}, "
                f"got {out_sections}."
            )

        out_bodies = extract_section_bodies(output)
        for protected in PROTECTED_SECTIONS:
            if protected not in source_bodies:
                continue
            src = _normalize_whitespace(source_bodies[protected])
            out = _normalize_whitespace(out_bodies.get(protected, ""))
            if src != out:
                problems.append(
                    f"Protected section '{protected}' was modified."
                )

        out_lower = output.lower()
        has_ai_category = (
            "ai \\& generative ai" in out_lower
            or "ai & generative ai" in out_lower
            or "artificial intelligence" in out_lower
        )
        if not has_ai_category:
            problems.append(
                "Skills section is missing AI/Generative AI keywords. "
                "Add a \\textbf{AI \\& Generative AI:} line inside the Skills "
                "section with the approved AI skills."
            )

        out_len = _estimate_length(output)
        if source_len and out_len > source_len * cls.LENGTH_TOLERANCE:
            over = int((out_len / source_len - 1) * 100)
            problems.append(
                f"Output is ~{over}% longer than the source. The source is a "
                "one-page resume, so the output MUST stay within ~2% of the "
                "source length. Drop low-priority skills (Postman, Swagger, "
                "Maven, Gradle, redundant test tools, extra DBs) unless the "
                "JD mentions them. Keep each Skills category to ONE line."
            )

        for pattern, _ in MATHMODE_PATTERNS:
            if pattern.search(output):
                problems.append(
                    "Output contains plain text wrapped in math mode "
                    "(e.g. \\(85\\%\\) or \\(\\mathrm{C++}\\)). "
                    "Write it directly: 85\\%, C++, 1000+, 15+."
                )
                break

        return problems