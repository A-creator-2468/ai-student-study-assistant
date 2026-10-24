# AI-Powered Student Study Assistant

A beginner-friendly Streamlit mini-project for students. It includes:
- Notes summarizer (built-in extractive mode; optional AI mode)
- Practice-question generator (built-in templates; optional AI mode)
- Study planner
- Doubt assistant (optional AI mode)

## Run locally

1. Install Python 3.10 or later.
2. Download or clone this repository.
3. Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

4. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Enable optional AI features

This project uses Groq's API when a `GROQ_API_KEY` is provided. Check the provider's current terms, availability, and usage limits before use.

For local development, set an environment variable named `GROQ_API_KEY`. Do not commit the key to GitHub.

For Streamlit Community Cloud, open the app's **Settings → Secrets** and add:

```toml
GROQ_API_KEY = "paste-your-own-key-here"
```

The app still supports its built-in summary, question templates, and planner without the key.

## Deploy on Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Create a new app and select the repository, branch, and `app.py`.
4. Deploy and wait for the build to finish.
5. Test each tab. Add the API key through app secrets only if you choose to enable AI features.

## Limitations

- Built-in summaries are extractive and may not fully capture meaning.
- Built-in questions are templates rather than model-generated questions.
- AI responses can be inaccurate; verify important information.
- Do not paste confidential or personal information into the app.
