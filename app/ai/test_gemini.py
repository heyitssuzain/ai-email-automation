from app.ai.gemini_client import client


def main():
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Reply with exactly: Gemini connection successful!",
    )

    print()
    print("=" * 60)
    print("GEMINI TEST")
    print("=" * 60)
    print(response.text)
    print("=" * 60)


if __name__ == "__main__":
    main()