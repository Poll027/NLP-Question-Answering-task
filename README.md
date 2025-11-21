# LLM_QA_Project_YOlubadejo_Folajuwon_23CG034128

Small Question-and-Answering (Q&A) system connecting to an LLM via OpenRouter.


Contents:

- `LLM_QA_CLI.py` — Command-line interface
- `app.py` — Streamlit web GUI (primary interface)
- `requirements.txt` — Python dependencies
- `LLM_QA_hosted_webGUI_link.txt` — placeholder for hosted link and details

Quick start (local):

1. Create and activate a Python virtual environment (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file or set environment variable `OPENROUTER_API_KEY` with your OpenRouter API key.

3. Run the CLI:

```powershell
python LLM_QA_CLI.py --question "What is natural language processing?"
```

4. Run the Streamlit app locally:

```powershell
streamlit run app.py
```

Notes:

- This repository is Streamlit-first; the Streamlit app (`app.py`) is the intended web GUI.
- The code defaults to mock mode when `OPENROUTER_API_KEY` is not set; set the env var to make real OpenRouter requests.
- Model names and endpoint behavior may need to be adjusted to match your OpenRouter plan — update the `model` argument if required.

Deployment:

- Deploy to Streamlit Cloud by pushing the repository to GitHub and linking the app.
- After deployment, fill `LLM_QA_hosted_webGUI_link.txt` with Name, Matric number, Live URL, and GitHub repo link.
