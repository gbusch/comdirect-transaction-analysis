import uuid
import requests
from dotenv import load_dotenv
import os

from auth import get_token, timestamp

load_dotenv()


ACCOUNT_ID = os.getenv("ACCOUNT_ID")


ACCESS_TOKEN = get_token()
SESSION_ID = uuid.uuid4()


def get_transactions(min_date, paging_first, paging_count=50):
    # 4.1.3 Account Transactions
    r = requests.get(
        f"https://api.comdirect.de/api/banking/v2/accounts/{ACCOUNT_ID}/transactions",
        params={
            "min-bookingDate": min_date,
            # "max-bookingDate": "2019-12-31",
            "bookingStatus": "BOOKED",
            "paging-count": paging_count,
            "paging-first": paging_first,
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{SESSION_ID}","requestId":"{timestamp()}"}}}}',
        },
    )
    assert r.ok
    return r.json()
