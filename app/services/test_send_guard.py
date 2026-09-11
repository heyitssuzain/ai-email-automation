from app.services.send_reply_service import send_approved_reply


def main():
    try:
        send_approved_reply(2)
    except Exception as exc:
        print("=" * 70)
        print("SEND GUARD TEST")
        print("=" * 70)
        print("Expected: SEND BLOCKED")
        print("Result  :", exc)
        print("=" * 70)


if __name__ == "__main__":
    main()