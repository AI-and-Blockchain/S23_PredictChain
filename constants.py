import dataclasses
from algosdk.v2client import algod, indexer


with open(".creds/api_key", "r") as file:
    API_KEY = file.readline()


ALGOD_API_ADDRESS = "https://testnet-algorand.api.purestake.io/ps2"
INDEXER_API_ADDRESS = "https://testnet-algorand.api.purestake.io/idx2"
ALGOD_TOKEN = API_KEY
INDEXER_TOKEN = API_KEY
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_API_ADDRESS)
INDEXER_CLIENT = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_API_ADDRESS)

ORACLE_ALGO_ADDRESS = ""
ORACLE_SERVER_ADDRESS = ""


@dataclasses.dataclass
class OpCodes:
    """Valid op codes to be included in transactions"""
    UP_DATASET = "<UP_DATASET>"
    TRAIN_MODEL = "<TRAIN_MODEL>"
    QUERY_MODEL = "<QUERY_MODEL>"
    UPDATE_PRICE = "<UPDATE_PRICE>"
