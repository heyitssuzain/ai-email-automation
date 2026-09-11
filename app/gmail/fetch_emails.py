import base64
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from app.gmail.client import get_gmail_service
from app.services.email_storage import save_emails_to_database


def get_header(headers, name):
    """
    Get a specific email header.
    """

    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")

    return ""


def decode_body(data):
    """
    Decode Gmail's URL-safe base64 email body.
    """

    if not data:
        return ""

    try:
        decoded = base64.urlsafe_b64decode(data + "===")
        return decoded.decode(
            "utf-8",
            errors="replace",
        )
    except Exception:
        return ""


def html_to_text(html):
    """
    Convert HTML email into readable plain text.
    """

    if not html:
        return ""

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    return soup.get_text(
        separator="\n",
        strip=True,
    )


def extract_body(payload):
    """
    Extract the best available email body.

    Preference:
    1. text/plain
    2. text/html
    3. nested MIME parts
    """

    mime_type = payload.get(
        "mimeType",
        "",
    )

    body_data = payload.get(
        "body",
        {}).get("data")

    if mime_type == "text/plain" and body_data:
        return decode_body(body_data).strip()

    if mime_type == "text/html" and body_data:
        return html_to_text(
            decode_body(body_data)
        )

    parts = payload.get(
        "parts",
        [],
    )

    plain_text = ""
    html_text = ""

    for part in parts:
        part_mime = part.get(
            "mimeType",
            "",
        )

        part_data = part.get(
            "body",
            {}).get("data")

        if part_mime == "text/plain" and part_data:
            plain_text = decode_body(part_data)

        elif part_mime == "text/html" and part_data:
            html_text = decode_body(part_data)

        elif part.get("parts"):
            nested_body = extract_body(part)

            if nested_body:
                plain_text = nested_body

    if plain_text.strip():
        return plain_text.strip()

    if html_text.strip():
        return html_to_text(html_text)

    return ""


def extract_attachments(payload):
    """
    Find attachments recursively inside an email.
    """

    attachments = []

    def walk_parts(parts):
        for part in parts:
            filename = part.get(
                "filename",
                "",
            )

            body = part.get(
                "body",
                {},
            )

            attachment_id = body.get(
                "attachmentId"
            )

            mime_type = part.get(
                "mimeType",
                "",
            )

            if filename and attachment_id:
                attachments.append(
                    {
                        "filename": filename,
                        "mime_type": mime_type,
                        "attachment_id": attachment_id,
                    }
                )

            nested_parts = part.get(
                "parts",
                []
            )

            if nested_parts:
                walk_parts(nested_parts)

    walk_parts(
        payload.get(
            "parts",
            [],
        )
    )

    return attachments


def fetch_latest_emails(max_results=10):
    """
    Fetch latest inbox emails from Gmail.
    """

    service = get_gmail_service()

    emails = []
    page_token = None

    while len(emails) < max_results:

        remaining = max_results - len(emails)

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=min(
                    remaining,
                    100,
                ),
                pageToken=page_token,
            )
            .execute()
        )

        messages = response.get(
            "messages",
            []
        )

        if not messages:
            break

        for message in messages:

            message_id = message["id"]

            full_message = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",
                )
                .execute()
            )

            payload = full_message.get(
                "payload",
                {}
            )

            headers = payload.get(
                "headers",
                []
            )

            sender = get_header(
                headers,
                "From",
            )

            recipient = get_header(
                headers,
                "To",
            )

            subject = get_header(
                headers,
                "Subject",
            )

            date = get_header(
                headers,
                "Date",
            )

            body = extract_body(
                payload
            )

            attachments = extract_attachments(
                payload
            )

            email_data = {
                "message_id": message_id,
                "thread_id": full_message.get(
                    "threadId"
                ),
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "date": date,
                "body": body,
                "attachments": attachments,
                "snippet": full_message.get(
                    "snippet",
                    "",
                ),
            }

            emails.append(email_data)

            if len(emails) >= max_results:
                break

        page_token = response.get(
            "nextPageToken"
        )

        if not page_token:
            break

    saved_count, skipped_count = (
        save_emails_to_database(emails)
    )

    print()
    print("=" * 70)
    print("GMAIL FETCH RESULT")
    print("=" * 70)
    print(
        f"Emails fetched    : {len(emails)}"
    )
    print(
        f"New emails saved  : {saved_count}"
    )
    print(
        f"Duplicates skipped: {skipped_count}"
    )
    print("=" * 70)

    print()

    for index, email in enumerate(
        emails,
        start=1,
    ):
        print("-" * 70)
        print(
            f"EMAIL #{index}"
        )
        print("-" * 70)

        print(
            "From:",
            email["sender"],
        )

        print(
            "To:",
            email["recipient"],
        )

        print(
            "Subject:",
            email["subject"],
        )

        print(
            "Date:",
            email["date"],
        )

        print(
            "Attachments:",
            len(email["attachments"]),
        )

        body_preview = email["body"][:300]

        print(
            "Body:",
            body_preview,
        )

    return emails


if __name__ == "__main__":
    fetch_latest_emails()