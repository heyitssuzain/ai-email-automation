from app.gmail.fetch_emails import fetch_latest_emails
from app.services.ai_email_service import analyze_unprocessed_emails
from app.services.reply_draft_service import generate_reply_drafts


def run_email_pipeline():
    print("=" * 70)
    print("AI EMAIL AUTOMATION PIPELINE")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Fetch new emails
    # ---------------------------------------------------------

    print("\n[1/3] Fetching new emails...")

    fetch_result = fetch_latest_emails()

    # ---------------------------------------------------------
    # 2. Analyze emails
    # ---------------------------------------------------------

    print("\n[2/3] Analyzing emails...")

    analysis_result = analyze_unprocessed_emails(
        limit=10
    )

    # ---------------------------------------------------------
    # 3. Generate reply drafts
    # ---------------------------------------------------------

    print("\n[3/3] Generating reply drafts...")

    draft_result = generate_reply_drafts(
        limit=10
    )

    # ---------------------------------------------------------
    # Pipeline summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print(
    f"Emails fetched       : "
    f"{len(fetch_result) if fetch_result is not None else 0}"
    )

    print(
        f"Emails analyzed      : "
        f"{analysis_result['succeeded']}"
    )

    print(
        f"Analysis failed      : "
        f"{analysis_result['failed']}"
    )

    print(
        f"Drafts created       : "
        f"{draft_result[1]}"
    )

    print(
        f"Drafts skipped       : "
        f"{draft_result[2]}"
    )

    print(
        f"Drafts failed        : "
        f"{draft_result[3]}"
    )

    print("=" * 70)

    return {
        "analysis": analysis_result,
        "drafts": {
            "processed": draft_result[0],
            "created": draft_result[1],
            "skipped": draft_result[2],
            "failed": draft_result[3],
        },
    }


if __name__ == "__main__":
    run_email_pipeline()