import base64
from pathlib import Path

from app.gmail.client import get_gmail_service


ATTACHMENT_DIR = Path("app/attachments")


def download_attachment(
    message_id: str,
    attachment_id: str,
    filename: str,
) -> str:
    service = get_gmail_service()

    ATTACHMENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(
            userId="me",
            messageId=message_id,
            id=attachment_id,
        )
        .execute()
    )

    data = attachment.get("data")

    if not data:
        raise ValueError(
            f"No attachment data returned for '{filename}'."
        )

    file_data = base64.urlsafe_b64decode(
        data + "==="
    )

    safe_filename = Path(filename).name
    file_path = ATTACHMENT_DIR / safe_filename

    file_path.write_bytes(file_data)

    return str(file_path)