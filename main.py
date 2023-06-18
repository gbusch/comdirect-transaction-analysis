import json
import uuid
from transactions import get_transactions


MIN_DATE = "2019-07-01"
PAGING = 50
INDEX = 0

transactions = get_transactions(MIN_DATE, INDEX, 1)

TOTAL = transactions["paging"]["matches"]
for index in range(INDEX, TOTAL, PAGING):
    transactions = get_transactions(MIN_DATE, index, PAGING)
    with open(f"./account_data/{uuid.uuid4()}.json", "w") as f:
        json.dump(transactions["values"], f)

print(f"processed {TOTAL} transactions")
