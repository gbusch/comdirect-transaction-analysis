import datetime
import json
import uuid
import requests
from dotenv import load_dotenv
import os


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_token():
    # 2.1 OAuth2 Resource Owner Password Credentials Flow
    r = requests.post(
        "https://api.comdirect.de/oauth/token",
        data={
            "client_id": f"{CLIENT_ID}",
            "client_secret": f"{CLIENT_SECRET}",
            "username": f"{USER_NAME}",
            "password": f"{PASSWORD}",
            "grant_type": "password",
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    assert r.ok
    access_token = r.json()["access_token"]

    # 2.2 Abruf Session-Status
    session_id = uuid.uuid4()
    tan_header = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-http-request-info": f'{{"clientRequestId": {{"sessionId": "{session_id}", "requestId": "{timestamp()}"}}}}',
        "Content-Type": "application/json",
    }
    r = requests.get(
        f"https://api.comdirect.de/api/session/clients/user/v1/sessions",
        headers=tan_header,
    )

    session_id = r.json()[0]["identifier"]

    # 2.3 Anlage Validierung einer Session-TAN
    r = requests.post(
        f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{session_id}/validate",
        data=f'{{"identifier":"{session_id}","sessionTanActive":true,"activated2FA":true}}',
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{session_id}","requestId":"{timestamp()}"}}}}',
            "Content-Type": "application/json",
        },
    )
    assert r.ok
    challenge_id = json.loads(r.headers["x-once-authentication-info"])["id"]
    m_tan = input("Please press ENTER after confirming push-tan ")

    # 2.4 Aktivierung einer Session-TAN
    r = requests.patch(
        f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{session_id}",
        data=f'{{"identifier":"{session_id}","sessionTanActive":true,"activated2FA":true}}',
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{session_id}","requestId":"{timestamp()}"}}}}',
            "Content-Type": "application/json",
            "x-once-authentication-info": f'{{"id":"{challenge_id}"}}',
        },
    )
    assert r.ok

    # 2.5 CD Secondary Flow
    r = requests.post(
        "https://api.comdirect.de/oauth/token",
        data={
            "client_id": f"{CLIENT_ID}",
            "client_secret": f"{CLIENT_SECRET}",
            "grant_type": "cd_secondary",
            "token": f"{access_token}",
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    access_token = r.json()["access_token"]
    print(f"access token: {access_token}")

    return access_token


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")
