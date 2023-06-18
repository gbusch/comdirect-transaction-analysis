# Retrieve your bank transactions from ComDirect via API

## Secrets
The five secrets listed in `.env.example` are needed. Copy them to `.env`. The env-file should never be checked into version control!
Username and password are the ones you use to login to ComDirect in the browser.
To get client-id and client-secret, you need to register for API use in the online-banking portal.
Account-id can be found out by running
```
GET /banking/clients/user/v1/accounts/balances
```
using the same headers as in `get_transactions()` and the token you retrieve with `get_token()`.

## Download transaction list
The transaction list can be downloaded by running `main.py`.

## Analysing spendings
Transactions are downloaded as json-files into the folder account_data. A convenient way to analyse the data is by using DuckDB:
```
import duckdb
conn = duckdb.connect()

conn.execute('''
    SELECT 
        *
    FROM read_json_auto('./account_data/*.json')
    ORDER BY bookingDate
''').df()
```

Account balance can be visualized by using a combination of DuckDB, pandas, and matplotlib:
```
import duckdb
conn = duckdb.connect()

df = conn.execute('''
    SELECT 
        bookingDate, CAST(transactionValue.value AS DOUBLE) AS value, transactionValue.unit AS unit
    FROM read_json_auto('./account_data/*.json')
    ORDER BY bookingDate
''').df()

BALANCE_START = <balance at the first downloaded transaction>
df["balance"] = df.value.cumsum() + BALANCE_START

df.plot(x="bookingDate", y="balance")
```

The same combination of tools could also be used to visualize the monthly grocery spendings:
```
import duckdb
conn = duckdb.connect()

grocery = conn.execute('''
    SELECT 
        bookingDate, -1 * CAST(transactionValue.value AS DOUBLE) AS value, transactionValue.unit AS unit, remittanceInfo
    FROM read_json_auto('./account_data/*.json')
    WHERE remittanceInfo ILIKE '%REWE%' OR remittanceInfo ILIKE '%Aldi%' OR remittanceInfo ILIKE '%Lidl%' OR remittanceInfo ILIKE '%Edeka%' OR remittanceInfo ILIKE '%Hit%'
    ORDER BY bookingDate
''').df()

grocery["month"] = grocery["bookingDate"].dt.to_period('M')

grocery.groupby("month").agg({"value":"sum"}).plot()
```
