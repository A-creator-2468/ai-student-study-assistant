import os
import re
from collections import Counter

import streamlit as st

st.set_page_config(
    page_title="AI-Powered Student Study Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI-Powered Student Study Assistant")
st.caption("Summarize notes • Generate practice questions • Plan study time • Ask for explanations")

st.info(
    "This MVP works without an API key using lightweight text-processing features. "
    "For generated explanations and more flexible summaries, optionally add a Groq API key."
)

def local_summary(text: str, sentence_count: int = 5) -> str:
    """Create an extractive summary by selecting sentences with frequent keywords."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return "Please enter some notes first."
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if len(sentences) <= sentence_count:
        return "\n".join(f"• {s.strip()}" for s in sentences if s.strip())

    words = re.findall(r"\b[a-zA-Z]{3,}\b", cleaned.lower())
    stop_words = {
        "the", "and", "for", "are", "was", "were", "this", "that", "with",
        "from", "into", "have", "has", "had", "their", "there", "which",
        "when", "where", "what", "will", "can", "could", "would", "should",
        "about", "also", "than", "then", "them", "they", "these", "those",
        "its", "not", "but", "you", "your", "our", "out", "use", "used",
    }
    freq = Counter(w for w in words if w not in stop_words)
    scored = []
    for index, sentence in enumerate(sentences):
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
        score = sum(freq[t] for t in tokens if t not in stop_words) / max(len(tokens), 1)
        scored.append((score, index, sentence.strip()))
    chosen = sorted(sorted(scored, reverse=True)[:sentence_count], key=lambda item: item[1])
    return "\n".join(f"• {sentence}" for _, _, sentence in chosen)

def local_questions(topic: str, count: int) -> list[str]:
    topic = topic.strip()
    if not topic:
        return []
    templates = [
        f"What is {topic}?",
        f"Explain the main features of {topic}.",
        f"What are the advantages and limitations of {topic}?",
        f"Give a real-world example of {topic}.",
        f"How does {topic} work?",
        f"Compare {topic} with a related concept.",
        f"Where is {topic} used and why?",
        f"Write short notes on the important concepts in {topic}.",
        f"What problems can occur when using {topic}?",
        f"Summarize the key points of {topic}.",
    ]
    return templates[:count]

def call_groq(prompt: str) -> str | None:
    """Optional AI integration. Returns None if no key or request fails."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    except Exception:
        api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly study assistant for college students. "
                        "Use clear, accurate, beginner-friendly language. "
                        "If the input is insufficient, say so rather than inventing facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as exc:
        st.warning(f"Optional AI service was unavailable, so you can use the built-in mode. Details: {exc}")
        return None

tab1, tab2, tab3, tab4 = st.tabs(
    ["📝 Notes Summarizer", "❓ Question Generator", "🗓️ Study Planner", "💬 Doubt Assistant"]
)

with tab1:
    st.subheader("Turn long notes into key points")
    notes = st.text_area("Paste your study notes", height=220, placeholder="Paste a paragraph or your class notes here...")
    summary_length = st.slider("Number of key sentences", min_value=3, max_value=8, value=5)
    if st.button("Summarize notes", key="summarize"):
        if not notes.strip():
            st.error("Please paste some notes first.")
        else:
            result = call_groq(
                f"Summarize the following study notes into {summary_length} concise bullet points. "
                f"Preserve important definitions and facts. Notes:\n\n{notes}"
            )
            if result:
                st.success("AI-generated summary")
                st.write(result)
            else:
                st.success("Built-in extractive summary")
                st.markdown(local_summary(notes, summary_length))

with tab2:
    st.subheader("Create practice questions")
    topic = st.text_input("Subject or topic", placeholder="e.g., Database normalization")
    question_count = st.slider("Number of questions", min_value=3, max_value=10, value=5)
    if st.button("Generate questions", key="questions"):
        if not topic.strip():
            st.error("Please enter a topic.")
        else:
            result = call_groq(
                f"Create {question_count} practice questions for a college student about '{topic}'. "
                "Mix short-answer and conceptual questions. Number each question and do not provide answers."
            )
            if result:
                st.success("AI-generated practice questions")
                st.write(result)
            else:
                st.success("Practice questions")
                for i, question in enumerate(local_questions(topic, question_count), start=1):
                    st.write(f"{i}. {question}")

with tab3:
    st.subheader("Build a simple daily study plan")
    subjects_text = st.text_input("Subjects (comma-separated)", placeholder="e.g., Python, DBMS, Mathematics")
    available_hours = st.number_input("Available study time (hours)", min_value=1, max_value=12, value=3)
    break_minutes = st.selectbox("Break between study sessions", [5, 10, 15], index=1)
    if st.button("Create study plan", key="planner"):
        subjects = [s.strip() for s in subjects_text.split(",") if s.strip()]
        if not subjects:
            st.error("Enter at least one subject.")
        else:
            total_minutes = int(available_hours * 60)
            session_count = len(subjects)
            session_minutes = max(15, total_minutes // session_count - break_minutes)
            st.success("Your suggested study plan")
            elapsed = 0
            for idx, subject in enumerate(subjects):
                start = elapsed
                end = min(start + session_minutes, total_minutes)
                st.write(f"**{idx + 1}. {subject}** — {start // 60:02d}:{start % 60:02d} to {end // 60:02d}:{end % 60:02d} ({end-start} min)")
                elapsed = end + (break_minutes if idx < len(subjects) - 1 else 0)
            st.caption("Tip: Put your hardest subject first and use the final 5 minutes for revision.")

with tab4:
    st.subheader("Ask a study question")
    doubt = st.text_area("What topic do you need help understanding?", height=150, placeholder="e.g., Explain primary keys and foreign keys with an example.")
    if st.button("Explain topic", key="doubt"):
        if not doubt.strip():
            st.error("Please enter a question.")
        else:
            result = call_groq(
                f"Explain this to a beginner college student. Use simple language, a small example, "
                f"and a short recap. Question: {doubt}"
            )
            if result:
                st.write(result)
            else:
                st.warning(
                    "The built-in version needs an AI API key for open-ended explanations. "
                    "Add GROQ_API_KEY to Streamlit secrets to enable this feature. "
                    "Meanwhile, try the Notes Summarizer, Question Generator, or Study Planner."
                )

st.divider()
st.caption("Academic prototype • Verify AI-generated information with textbooks or your instructor.")
