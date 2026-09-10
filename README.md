# Customized Resume Builder

A streamlined, modern Gradio application that takes a Job Description and your Overleaf LaTeX resume code, uses `gpt-5` to tailor your resume specifically to the job, and outputs compile-ready Overleaf LaTeX (`.tex`) code with one-click copy.

## Key Features

- **Pure Text-in, Text-out**: Only two inputs:
  1. **Paste Job Description**
  2. **Paste Overleaf / LaTeX Resume Code**
- **Direct Overleaf LaTeX Output**: Tailored `.tex` code ready to paste straight into Overleaf.
- **Strict ATS Section Preservation**: Preserves the source structure, ordering, and formatting macros without adding arbitrary sections or inventing facts.
- **Live Streaming**: Real-time token streaming and status feedback as the model tailors your resume.

## Project Structure

- `app.py` — Clean Gradio interface and high-contrast theme styling.
- `application.py` — Orchestrates stream generation, validation, and cleanup.
- `resume_service.py` — Overleaf LaTeX tailoring rules, system prompts, and ATS constraints.
- `llm_client.py` — Azure OpenAI client adapter with streaming and API key support.
- `config.py` — Centralized environment configuration.

## Run Locally

1. **Create and activate a virtual environment**:

   Windows PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   Copy `.env.example` to `.env` and set your Azure OpenAI details:
   ```ini
   AZURE_OPENAI_ENDPOINT=https://<your-resource>.services.ai.azure.com/openai/v1
   AZURE_OPENAI_MODEL=gpt-5
   AZURE_TOKEN_SCOPE=https://ai.azure.com/.default
   PORT=7860
   ```

4. **Authenticate Azure locally**:
   ```bash
   az login
   ```
   *(Or optionally set `AZURE_OPENAI_API_KEY=your_key` in `.env` to bypass Azure CLI login)*

5. **Start the application**:
   ```bash
   python app.py
   ```
   Open `http://localhost:7860` in your browser.

---

## 🚀 How to Deploy Completely FREE

### Option 1: Hugging Face Spaces (Recommended — 100% Free Forever)

Hugging Face (the creator of Gradio) provides free hosting with 2 vCPUs and 16 GB RAM.

1. **Create a Free Space**:
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space).
   - Enter a name (e.g. `latex-resume-builder`).
   - Select **Gradio** as the Space SDK.
   - Choose the **Free** hardware tier (CPU basic • 2 vCPU • 16 GB RAM).
   - Set Space to **Public** or **Private**.

2. **Upload Your Files**:
   - Push your repository using Git or drag-and-drop the files directly in the browser:
     - `app.py`
     - `application.py`
     - `resume_service.py`
     - `llm_client.py`
     - `config.py`
     - `requirements.txt`

3. **Add Environment Variables & Secrets**:
   - Go to **Settings** → **Variables and secrets**.
   - Under **Secrets** (or Variables), add:
     - `AZURE_OPENAI_ENDPOINT` = `https://<your-resource>.services.ai.azure.com/openai/v1`
     - `AZURE_OPENAI_MODEL` = `gpt-5`
     - `AZURE_OPENAI_API_KEY` = `<your-azure-key>`
   - Hugging Face automatically detects `app.py`, installs `requirements.txt`, and boots your app on a permanent HTTPS URL!

---

### Option 2: Instant 72-Hour Public Link (Zero Deployment Needed)

If you just need to share the app with friends, clients, or test from your mobile phone:

1. In `.env`, set:
   ```ini
   GRADIO_SHARE=true
   ```
2. Run:
   ```bash
   python app.py
   ```
3. Gradio will output a live public URL: `https://xxxx.gradio.live`. It requires no server setup and runs directly through a secure tunnel.

---

### Option 3: Koyeb / Render Free Tier

1. Push your repository to GitHub.
2. Sign up on [koyeb.com](https://www.koyeb.com) or [render.com](https://render.com).
3. Connect your GitHub repository.
4. Set the build command to: `pip install -r requirements.txt` and start command to: `python app.py`.
5. Add your environment variables in their dashboard.
