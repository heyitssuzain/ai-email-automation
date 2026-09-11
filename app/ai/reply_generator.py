from app.ai.gemini_client import client


MODEL_NAME = "gemini-3.6-flash"

def generate_reply(
    sender: str,
    subject: str,
    body: str,
    category: str,
    priority: str,
    intent: str,
    summary: str,
    attachment_text: str = "",
    knowledge_context: str = "",
) -> str:

    prompt = f"""
You are an AI email assistant.

Write a professional reply to the email below.

IMPORTANT RULES:

1. Return ONLY the reply text.
2. Do not add explanations.
3. Do not mention that you are an AI.
4. Do not invent facts, promises, prices, dates,
   policies, or information.
5. If information is missing, politely ask the sender
   for it.
6. Keep the reply concise and professional.
7. Match the tone of the original email.
8. Do not include a subject line.
9. Do not automatically promise actions that have
   not been confirmed.
10. Use attachment information only when relevant.
11. Never claim that an attachment was reviewed,
    approved, accepted, or verified unless the
    provided attachment content supports that claim.

KNOWLEDGE BASE:

The following information was retrieved from the
company knowledge base.

Use it when it is relevant to the customer's question.

Do NOT invent information that is not present in the
knowledge base.

{knowledge_context if knowledge_context else "No relevant knowledge base information was found."}


EMAIL INFORMATION:

From:
{sender}

Subject:
{subject}

Category:
{category}

Priority:
{priority}

Intent:
{intent}

Summary:
{summary}

Original Email:
{body}


ATTACHMENT CONTENT:

{
    attachment_text
    if attachment_text
    else "No readable attachment content is available."
}


Now write the reply.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    reply = (response.text or "").strip()

    if not reply:
        raise ValueError("Gemini returned an empty reply.")

    return reply