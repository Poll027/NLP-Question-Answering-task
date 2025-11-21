"""Streamlit web GUI for the LLM Q&A project using OpenRouter.

Features:
- Enter a question
- View processed question
- See raw LLM response (truncated)
- Display generated answer

Set OPENROUTER_API_KEY in your environment to enable real queries; otherwise the app runs in mock mode.
"""
import re
import json
import streamlit as st
import requests

# IMPORTANT: This app uses ONLY the API key supplied by the user at runtime.
# We do NOT read environment variables, .env, or Streamlit secrets anymore.


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\n\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_prompt(processed_question: str) -> str:
    return (
        "You are a helpful assistant. Answer the user's question concisely and clearly.\n"
        f"Question: {processed_question}\nAnswer:"
    )


def query_openrouter(prompt: str, model: str = "gpt-4o-mini", api_key: str = None) -> dict:
    # Require api_key to be provided explicitly by the user.
    if not api_key:
        raise ValueError("No OpenRouter API key provided. The app requires the user to supply their API key.")

    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}
    resp = requests.post(url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices") or []
    answer = None
    if choices:
        answer = choices[0].get("message", {}).get("content") or choices[0].get("text")
    return {"mock": False, "raw": data, "answer": answer}


def main():
    st.set_page_config(page_title="LLM Q&A (OpenRouter)", layout="centered")
    st.title("LLM Q&A — OpenRouter (Streamlit)")

    st.markdown("Enter a question and click 'Ask' to query the LLM.")

    # Require the user to input their OpenRouter API key (masked). This key is used only in-memory.
    st.subheader("Your OpenRouter API key")
    provided_key = st.text_input("Paste your OpenRouter API key (required)", value="", type="password")
    if not provided_key or provided_key.strip() == "":
        st.warning("Please paste your OpenRouter API key above before asking a question. This key will not be saved.")

    question = st.text_area("Your question", height=120)
    col1, col2 = st.columns([1, 1])
    with col1:
        model = st.selectbox("Model (env override)", options=["gpt-4o-mini", "gpt-4o", "openrouter-gpt"], index=0)
    with col2:
        ask = st.button("Ask")

    if ask and question.strip():
        processed = preprocess(question)
        st.subheader("Processed question")
        st.write(processed)

        prompt = build_prompt(processed)
        # ensure user provided a key
        api_key_to_use = provided_key.strip()
        if not api_key_to_use:
            st.error("No API key provided. Please paste your OpenRouter API key in the field above.")
            return

        with st.spinner("Querying LLM..."):
            try:
                result = query_openrouter(prompt, model=model, api_key=api_key_to_use)
            except Exception as e:
                st.error(f"Error querying OpenRouter: {e}")
                return

        st.subheader("Raw response (truncated)")
        st.code(json.dumps(result.get("raw"), indent=2)[:2000])

        st.subheader("Answer")
        if result.get("mock"):
            st.info(result.get("answer"))
        else:
            st.success(result.get("answer") or "(no answer parsed)")


if __name__ == "__main__":
    main()
