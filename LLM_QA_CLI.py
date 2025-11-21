#!/usr/bin/env python3
"""LLM_QA_CLI.py

Simple command-line Q&A client that preprocesses a question and queries OpenRouter (or a mock) for an answer.

Usage:
  python LLM_QA_CLI.py --question "What is NLP?"

Set environment variable OPENROUTER_API_KEY to use real OpenRouter API requests.
"""
import os
import re
import argparse
import json
from typing import Dict, Any

import requests


def preprocess(text: str) -> str:
    """Lowercase, remove punctuation, and tokenize (simple whitespace tokens).

    Returns a cleaned string suitable to display or include in a prompt.
    """
    text = text.lower()
    # remove punctuation
    text = re.sub(r"[^\n\w\s]", "", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_prompt(processed_question: str) -> str:
    return (
        "You are a helpful assistant. Answer the user's question concisely and clearly.\n"
        f"Question: {processed_question}\nAnswer:"
    )


def query_openrouter(prompt: str, model: str = "gpt-4o-mini", api_key: str = None) -> Dict[str, Any]:
    """Send a completion request to the OpenRouter-compatible endpoint.

    This function requires the caller to supply an API key explicitly. The
    function will not read keys from environment variables or secrets files.
    """
    if not api_key:
        raise ValueError("OpenRouter API key must be provided via --api-key or prompted input.")

    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800,
    }

    resp = requests.post(url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Try to extract a sensible answer based on common OpenAI-style responses
    answer = None
    if isinstance(data, dict):
        # OpenRouter often returns OpenAI-compatible response shape
        choices = data.get("choices") or []
        if choices:
            content = choices[0].get("message", {}).get("content") or choices[0].get("text")
            answer = content

    return {"mock": False, "raw": data, "answer": answer}


def main():
    parser = argparse.ArgumentParser(description="LLM Q&A CLI using OpenRouter")
    parser.add_argument("--question", "-q", help="Question to ask", required=False)
    parser.add_argument("--api-key", "-k", help="OpenRouter API key", required=False)
    args = parser.parse_args()

    if args.question:
        question = args.question
    else:
        question = input("Enter your question: ")

    api_key = args.api_key
    if not api_key:
        # Prompt securely for API key if not provided as an argument
        try:
            import getpass
            api_key = getpass.getpass("OpenRouter API key: ")
        except Exception:
            api_key = input("OpenRouter API key: ")

    if not api_key:
        print("No API key provided. Exiting.")
        return

    processed = preprocess(question)
    prompt = build_prompt(processed)

    print("\nProcessed question:", processed)
    print("\nSending to LLM...\n")

    try:
        result = query_openrouter(prompt, api_key=api_key)
    except Exception as e:
        print("Error querying OpenRouter:", e)
        return

    if result.get("mock"):
        print("[MOCK MODE] Raw response:", json.dumps(result.get("raw"), indent=2))
        print("\nAnswer:\n", result.get("answer"))
    else:
        print("Raw response (truncated):")
        print(json.dumps(result.get("raw"), indent=2)[:2000])
        print("\nAnswer:\n", result.get("answer") or "(no answer parsed)")


if __name__ == "__main__":
    main()
