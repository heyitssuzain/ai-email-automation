from app.gmail.client import get_gmail_service


def main():
    service = get_gmail_service()

    profile = (
        service.users()
        .getProfile(userId="me")
        .execute()
    )

    email = profile.get("emailAddress")

    print()
    print("================================")
    print("Gmail authentication successful!")
    print("Connected account:", email)
    print("================================")
    print()


if __name__ == "__main__":
    main()