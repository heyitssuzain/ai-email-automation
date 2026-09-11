from email.message import EmailMessage

from app.gmail.client import get_gmail_service


def send_email(
    recipient: str,
    subject: str,
    body: str,
    thread_id: str | None = None,
):
    service = get_gmail_service()

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    raw_message = __import__("base64").urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    message_body = {
        "raw": raw_message,
    }

    if thread_id:
        message_body["threadId"] = thread_id

    sent_message = (
        service.users()
        .messages()
        .send(
            userId="me",
            body=message_body,
        )
        .execute()
    )

    return sent_message