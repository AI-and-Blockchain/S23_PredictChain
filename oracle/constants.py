from algosdk.v2client import algod

ALGOD_API_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_API_ADDRESS)

ORACLE_ADDRESS = ""