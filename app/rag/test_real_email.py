from app.database.database import SessionLocal
from app.database.models import Email
from app.rag.retriever import retrieve_relevant_knowledge
from app.services.reply_draft_service import generate_reply_with_retry


EMAIL_ID = 20


def run_real_email_rag_test():
    db = SessionLocal()

    try:
        email = (
            db.query(Email)
            .filter(Email.id == EMAIL_ID)
            .first()
        )

        if not email:
            raise ValueError(f"Email ID {EMAIL_ID} not found.")

        print("=" * 70)
        print("REAL EMAIL RAG TEST")
        print("=" * 70)
        print(f"Email ID : {email.id}")
        print(f"Subject  : {email.subject}")

        knowledge_query = f"""
Subject: {email.subject}

Email:
{email.body}

Intent:
{email.intent or ""}

Summary:
{email.summary or ""}
"""

        knowledge_results = retrieve_relevant_knowledge(
            knowledge_query,
            top_k=3,
        )

        print()
        print("RELEVANT KNOWLEDGE")
        print("=" * 70)

        for result in knowledge_results:
            print(
                f"- {result['title']} "
                f"(score={result['score']:.4f})"
            )

        knowledge_context = "\n\n".join(
            f"Knowledge: {result['title']}\n"
            f"{result['content']}"
            for result in knowledge_results
        )

        draft = generate_reply_with_retry(
            email=email,
            attachment_text="",
            knowledge_context=knowledge_context,
        )

        print()
        print("=" * 70)
        print("GENERATED RAG DRAFT")
        print("=" * 70)
        print(draft)
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_real_email_rag_test()