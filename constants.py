import dataclasses
from algosdk.v2client import algod, indexer

ALGOD_API_ADDRESS = "http://localhost:4001"
INDEXER_API_ADDRESS = "http://localhost:8980"
ALGOD_TOKEN = "a" * 64
INDEXER_TOKEN = "a" * 64
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_API_ADDRESS)
INDEXER_CLIENT = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_API_ADDRESS)

ORACLE_ALGO_ADDRESS = ""
ORACLE_SERVER_ADDRESS = ""


@dataclasses.dataclass
class OpCodes:
    UP_DATASET = "<UP_DATASET>"
    QUERY_MODEL = "<QUERY_MODEL>"
    UPDATE_PRICE = "<UPDATE_PRICE>"
