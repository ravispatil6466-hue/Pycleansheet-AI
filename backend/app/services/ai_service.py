"""
AI chatbot service. Supports OpenAI or Gemini based on settings.AI_PROVIDER.
Builds a system prompt describing the active dataset so the assistant can
answer analytical questions, suggest charts, and explain cleaning steps.
"""
from app.config import settings
import pandas as pd


def _dataset_context(df: pd.DataFrame | None) -> str:
    if df is None:
        return "No dataset is currently loaded."
    cols = ", ".join([f"{c} ({df[c].dtype})" for c in df.columns[:40]])
    return (
        f"Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns.\n"
        f"Columns: {cols}\n"
        f"Sample rows (first 3): {df.head(3).to_dict(orient='records')}"
    )


SYSTEM_PROMPT_TEMPLATE = """You are the AI assistant inside Pycleansheet AI, a Power BI-like data
analytics platform. You help users understand their dataset, suggest data
cleaning steps, recommend chart types, and explain statistics in plain
language. Be concise and practical. When recommending a chart, name the
exact chart type (bar, line, scatter, heatmap, etc.) and which columns to use.

Context about the current dataset:
{context}
"""


def chat_completion(message: str, df: pd.DataFrame | None, history: list | None = None) -> str:
    context = _dataset_context(df)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
    history = history or []

    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return _gemini_chat(system_prompt, message, history)
    if settings.OPENAI_API_KEY:
        return _openai_chat(system_prompt, message, history)

    return _fallback_answer(message, df)


def _openai_chat(system_prompt: str, message: str, history: list) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.4)
    return resp.choices[0].message.content


def _gemini_chat(system_prompt: str, message: str, history: list) -> str:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
    chat = model.start_chat(history=[
        {"role": "user" if h.get("role") == "user" else "model", "parts": [h.get("content", "")]}
        for h in history[-10:]
    ])
    resp = chat.send_message(message)
    return resp.text


def _fallback_answer(message: str, df: pd.DataFrame | None) -> str:
    """Deterministic offline fallback so the app works without an API key configured."""
    msg = message.lower()
    if df is None:
        return ("No AI provider API key is configured yet (set OPENAI_API_KEY or GEMINI_API_KEY "
                "in backend/.env), and no dataset is loaded either. Upload a dataset and add an "
                "API key to unlock full AI chat.")
    if "missing" in msg or "null" in msg:
        missing = df.isna().sum()
        top = missing[missing > 0].sort_values(ascending=False).head(5)
        if len(top) == 0:
            return "Good news — this dataset has no missing values."
        lines = "\n".join([f"- {c}: {int(v)} missing" for c, v in top.items()])
        return f"Here are the columns with the most missing values:\n{lines}"
    if "correlat" in msg:
        return "Try the Correlation Matrix chart type from the visualization pane to explore relationships between numeric columns."
    if "summary" in msg or "describe" in msg or "overview" in msg:
        return (f"This dataset has {df.shape[0]} rows and {df.shape[1]} columns. "
                f"Numeric columns: {list(df.select_dtypes('number').columns)[:10]}. "
                f"Categorical columns: {list(df.select_dtypes(exclude='number').columns)[:10]}.")
    return ("I can help with cleaning, EDA, and chart suggestions. "
            "(Note: no AI provider API key is configured, so I'm answering with a basic rule-based "
            "assistant. Add OPENAI_API_KEY or GEMINI_API_KEY in backend/.env for full AI responses.)")
