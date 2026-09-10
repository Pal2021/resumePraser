import gradio as gr
from dotenv import load_dotenv

from application import ResumeApplication
from config import Settings
from llm_client import AzureOpenAIClient
from resume_service import ResumeTailoringService

load_dotenv()
settings = Settings.from_environment()

application = ResumeApplication(
    tailoring=ResumeTailoringService(AzureOpenAIClient.from_settings(settings)),
)


def generate(jd_text: str, resume_text: str):
    last_output = ""
    try:
        for output, status in application.generate_stream(jd_text, resume_text):
            if output:
                last_output = output
            yield output or last_output, status
    except Exception as exc:
        yield last_output, f"❌ **Error:** {exc}"


APP_CSS = """
/* Font setup */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

.hero {
    margin-bottom: 24px !important;
}
.hero h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 6px !important;
}
.hero p {
    font-size: 1.05rem !important;
    color: #94a3b8 !important;
    margin: 0 !important;
}

/* Generate Button */
.gen-btn {
    min-height: 52px !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.4) !important;
    cursor: pointer !important;
    transition: transform 0.15s ease, box-shadow 0.2s ease !important;
}
.gen-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.55) !important;
}

/* Output Card Base - High-contrast dark styling by default */
.output-card {
    border-radius: 16px !important;
    padding: 24px !important;
    margin-top: 16px !important;
    background: #111827 !important;
    border: 1px solid #374151 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
}

/* Output Section Title */
.output-title, .output-title * {
    color: #f9fafb !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    margin-bottom: 12px !important;
}

/* Status Banner / Pill */
.status-pill {
    padding: 12px 18px !important;
    border-radius: 10px !important;
    margin-bottom: 16px !important;
    background: rgba(99, 102, 241, 0.2) !important;
    border: 1px solid rgba(129, 140, 248, 0.4) !important;
    border-left: 5px solid #818cf8 !important;
}

.status-pill, .status-pill * {
    color: #e0e7ff !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    line-height: 1.5 !important;
}

/* Light Theme Overrides (if browser is explicitly light) */
.gradio-container:not(.dark) .output-card,
body:not(.dark) .output-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06) !important;
}

.gradio-container:not(.dark) .output-title *,
body:not(.dark) .output-title * {
    color: #0f172a !important;
}

.gradio-container:not(.dark) .status-pill,
body:not(.dark) .status-pill {
    background: #eef2ff !important;
    border: 1px solid #c7d2fe !important;
    border-left: 5px solid #4f46e5 !important;
}

.gradio-container:not(.dark) .status-pill *,
body:not(.dark) .status-pill * {
    color: #312e81 !important;
}

/* Monospace font for LaTeX code */
.output-card textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace !important;
    font-size: 0.92rem !important;
    line-height: 1.55 !important;
}
"""

with gr.Blocks(title="Customized Resume Builder") as demo:
    with gr.Column():

        gr.Markdown(
            "# 🎯 Customized Resume Builder\n"
            "Paste your target Job Description and Overleaf LaTeX resume. Get back tailor-made `.tex` code ready for Overleaf.",
            elem_classes=["hero"],
        )

        with gr.Row(equal_height=True):
            jd_text = gr.Textbox(
                lines=18,
                label="Paste Job Description",
                placeholder="Paste the target Job Description here…",
            )
            resume_text = gr.Textbox(
                lines=18,
                label="Paste Overleaf / LaTeX Resume Code",
                placeholder="Paste your Overleaf LaTeX resume code here…",
            )

        generate_btn = gr.Button(
            "🚀 Generate Tailored Resume",
            variant="primary",
            elem_classes=["gen-btn"],
        )

        with gr.Column(elem_classes=["output-card"]):
            gr.Markdown(
                "### 📑 Tailored Resume — Overleaf LaTeX (.tex) Code",
                elem_classes=["output-title"],
            )
            status = gr.Markdown(
                "Ready. Paste a JD and your LaTeX resume, then click **Generate Tailored Resume**.",
                elem_classes=["status-pill"],
            )
            result_text = gr.Textbox(
                lines=26,
                label="Tailored Resume — Overleaf LaTeX (.tex) Code",
                show_label=False,
                buttons=["copy"],
                placeholder="Your tailored Overleaf LaTeX resume code will appear here…",
            )

        gr.ClearButton(
            value="🗑️ Clear All",
            components=[jd_text, resume_text, result_text, status],
        )

        generate_btn.click(
            generate,
            inputs=[jd_text, resume_text],
            outputs=[result_text, status],
        )


if __name__ == "__main__":
    demo.launch(
        server_name=settings.server_name,
        server_port=settings.port,
        share=settings.share,
        theme=gr.themes.Soft(),
        css=APP_CSS,
    )
