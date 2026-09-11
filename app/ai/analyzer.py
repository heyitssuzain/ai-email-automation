import json
import re

from app.ai.gemini_client import client
from app.ai.schemas import EmailAnalysis


MODEL_NAME = "gemini-3.6-flash"


def clean_json_response(text: str) -> str:
    """
    Clean Gemini's response before JSON parsing.

    Handles:
    - ```json ... ```
    - ``` ... ```
    - Extra text before/after JSON
    """

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    # If Gemini added text around the JSON,
    # extract the JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()


def analyze_email(
    sender: str,
    subject: str,
    body: str,
    attachment_text: str = "",
) -> EmailAnalysis:
    """
    Analyze an email using Gemini AI.
    """

    prompt = f"""
You are an AI email classification assistant.

Analyze the email below.

RETURN ONLY A JSON OBJECT.
DO NOT use Markdown.
DO NOT use ```json.
DO NOT add explanations before or after the JSON.

The JSON must contain exactly these fields:

- category
- priority
- intent
- summary
- requires_reply

Allowed categories:

- Customer Support
- Sales
- Complaint
- Job Inquiry
- Invoice
- General
- Spam

Allowed priorities:

- LOW
- MEDIUM
- HIGH
- URGENT

Rules:

1. category must be exactly one of the allowed categories.
2. priority must be exactly one of the allowed priorities.
3. intent must briefly explain what the sender wants.
4. summary must summarize the email clearly.
5. requires_reply must be true if the sender expects or needs a response.
6. Do not add extra JSON fields.
7. Return valid JSON only.

EMAIL:

From:
{sender}

Subject:
{subject}

Body:
{body}

ATTACHMENT CONTENT:

{attachment_text if attachment_text else "No readable attachment content is available."}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    response_text = response.text or ""

    cleaned_text = clean_json_response(
        response_text
    )

    try:
        data = json.loads(cleaned_text)

    except json.JSONDecodeError as exc:
        print()
        print("=" * 70)
        print("GEMINI RAW RESPONSE")
        print("=" * 70)
        print(response_text)
        print("=" * 70)

        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    return EmailAnalysis.model_validate(data)