import socket

from googleapiclient.discovery import Resource
from googleapiclient.discovery import build
import httplib2
from google_auth_httplib2 import AuthorizedHttp

from app.gmail.auth import get_gmail_credentials


# Force this project to use IPv4 for Google API connections.
_original_getaddrinfo = socket.getaddrinfo


def _ipv4_only_getaddrinfo(*args, **kwargs):
    results = _original_getaddrinfo(*args, **kwargs)

    return [
        result
        for result in results
        if result[0] == socket.AF_INET
    ]


socket.getaddrinfo = _ipv4_only_getaddrinfo


def get_gmail_service() -> Resource:
    credentials = get_gmail_credentials()

    http = httplib2.Http(timeout=30)

    authorized_http = AuthorizedHttp(
        credentials,
        http=http,
    )

    service = build(
        "gmail",
        "v1",
        http=authorized_http,
        cache_discovery=False,
    )

    return service