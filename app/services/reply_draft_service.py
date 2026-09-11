import logging
import time

from app.ai.reply_generator import generate_reply
from app.database.database import SessionLocal
from app.database.models import Email, ReplyDraft, Attachment
from app.rag.retriever import retrieve_relevant_knowledge


logger = logging.getLogger(__name__)

# Gemini Free Tier safety
REQUEST_SPACING_SECONDS = 15

# Retry settings
MAX_RETRIES = 4
BASE_BACKOFF_SECONDS = 20
BACKOFF_MULTIPLIER = 2
MAX_BACKOFF_SECONDS = 180


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check whether the Gemini request failed because of rate limiting."""

    if getattr(exc, "code", None) == 429:
        return True

    message = str(exc).lower()

    return (
        "429" in message
        or "resource_exhausted" in message
    )


def generate_reply_with_retry(
    email: Email,
    attachment_text: str,
    knowledge_context: str = "",
):
    """Generate an AI reply with RAG context, spacing, and retry protection."""

    attempt = 0
    backoff = BASE_BACKOFF_SECONDS

    while True:

        try:
            # Keep requests spaced out for Gemini Free Tier.
            time.sleep(REQUEST_SPACING_SECONDS)

            return generate_reply(
                sender=email.sender,
                subject=email.subject,
                body=email.body,
                category=email.category,
                priority=email.priority,
                intent=email.intent or "",
                summary=email.summary or "",
                attachment_text=attachment_text,
                knowledge_context=knowledge_context,
            )

        except Exception as exc:

            if (
                _is_rate_limit_error(exc)
                and attempt < MAX_RETRIES
            ):
                wait = min(
                    backoff,
                    MAX_BACKOFF_SECONDS,
                )

                logger.warning(
                    "Gemini rate limited for "
                    "email id=%s. Retry %d/%d "
                    "in %ds.",
                    email.id,
                    attempt + 1,
                    MAX_RETRIES,
                    wait,
                )

                print(
                    f"[RATE LIMIT] email id={email.id} | "
                    f"Retry {attempt + 1}/{MAX_RETRIES} "
                    f"in {wait}s"
                )

                time.sleep(wait)

                backoff *= BACKOFF_MULTIPLIER
                attempt += 1

                continue

            raise


def generate_reply_drafts(limit=10):

    db = SessionLocal()

    processed_count = 0
    created_count = 0
    skipped_count = 0
    failed_count = 0

    try:

        emails = (
            db.query(Email)
            .filter(
                Email.requires_reply.is_(True),
                Email.category.is_not(None),
            )
            .order_by(Email.id.desc())
            .limit(limit)
            .all()
        )

        print()
        print("=" * 70)
        print("AI REPLY DRAFT PROCESSING")
        print("=" * 70)

        print(
            f"Emails found for drafting: "
            f"{len(emails)}"
        )

        print("=" * 70)

        for email in emails:

            processed_count += 1

            existing_draft = (
                db.query(ReplyDraft)
                .filter(
                    ReplyDraft.email_id == email.id,
                    ReplyDraft.status.in_(
                        ["pending", "approved", "sent"]
                    ),
                )
                .first()
            )

            if existing_draft:

                skipped_count += 1

                print(
                    f"[SKIP] id={email.id} | "
                    f"Draft already exists | "
                    f"{email.subject}"
                )

                continue

            print()
            print(
                f"Processing email id={email.id}"
            )

            print(
                f"Subject: {email.subject}"
            )

            try:

                # -------------------------------------------------
                # Load attachments
                # -------------------------------------------------

                attachments = (
                    db.query(Attachment)
                    .filter(
                        Attachment.email_id == email.id
                    )
                    .all()
                )

                # -------------------------------------------------
                # Collect extracted attachment text
                # -------------------------------------------------

                attachment_text_parts = []

                for attachment in attachments:

                    if attachment.extracted_text:

                        attachment_text_parts.append(
                            f"Attachment: "
                            f"{attachment.filename}\n"
                            f"{attachment.extracted_text}"
                        )

                attachment_text = "\n\n".join(
                    attachment_text_parts
                )

                print(
                    f"Attachments found: "
                    f"{len(attachments)}"
                )

                print(
                    f"Attachment text: "
                    f"{len(attachment_text)} characters"
                )

                # -------------------------------------------------
                # Retrieve relevant knowledge from RAG
                # -------------------------------------------------

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

                knowledge_context = "\n\n".join(
                    f"Knowledge: {result['title']}\n"
                    f"{result['content']}"
                    for result in knowledge_results
                )

                print(
                    f"Relevant knowledge items: "
                    f"{len(knowledge_results)}"
                )

                # -------------------------------------------------
                # Generate reply using Gemini + RAG
                # -------------------------------------------------

                draft_text = generate_reply_with_retry(
                    email=email,
                    attachment_text=attachment_text,
                    knowledge_context=knowledge_context,
                )

                # -------------------------------------------------
                # Save reply draft
                # -------------------------------------------------

                draft = ReplyDraft(
                    email_id=email.id,
                    draft_text=draft_text,
                    status="pending",
                )

                db.add(draft)
                db.commit()

                created_count += 1

                print(
                    f"[OK] Draft created for "
                    f"email id={email.id}"
                )

            except Exception as exc:

                db.rollback()

                failed_count += 1

                logger.exception(
                    "Failed to generate reply "
                    "for email id=%s",
                    email.id,
                )

                print(
                    f"[FAILED] email id={email.id} | "
                    f"{exc}"
                )

        total_drafts = (
            db.query(ReplyDraft).count()
        )

        print()
        print("-" * 70)

        print(
            f"Processed this run    : "
            f"{processed_count}"
        )

        print(
            f"Drafts created        : "
            f"{created_count}"
        )

        print(
            f"Skipped               : "
            f"{skipped_count}"
        )

        print(
            f"Failed                : "
            f"{failed_count}"
        )

        print(
            f"Total drafts in DB    : "
            f"{total_drafts}"
        )

        print("-" * 70)

        return (
            processed_count,
            created_count,
            skipped_count,
            failed_count,
        )

    finally:

        db.close()