import dataclasses
import os
import algosdk.mnemonic
from algosdk.v2client import algod, indexer

with open("creds/algo_api_key.creds", "r") as file:
    API_KEY = file.readline().strip("\n")

with open("creds/web3_api_key.creds", "r") as file:
    WEB3_API_KEY = file.readline()


ALGOD_API_ADDRESS = "https://testnet-algorand.api.purestake.io/ps2"
INDEXER_API_ADDRESS = "https://testnet-algorand.api.purestake.io/idx2"
ALGOD_CLIENT = algod.AlgodClient(API_KEY, ALGOD_API_ADDRESS, headers={"X-API-Key": API_KEY})
INDEXER_CLIENT = indexer.IndexerClient(API_KEY, INDEXER_API_ADDRESS, headers={"X-API-Key": API_KEY})

ORACLE_ALGO_ADDRESS = "4GLRF2BVZ32W5H5ISTOH7ZSTL6RVVFDN2QV3M5HEY66K34G2WX67U5ZETA"
ORACLE_SERVER_HOST, ORACLE_SERVER_PORT = "localhost", 8030
CLIENT_SERVER_HOST, CLIENT_SERVER_PORT = "localhost", 8031
ORACLE_SERVER_ADDRESS = f"{ORACLE_SERVER_HOST}:{ORACLE_SERVER_PORT}"

ALGO_AMOUNT_CAP = 1000
"""Hard limit for all transaction amounts.  Prevents test accounts from being drained"""


@dataclasses.dataclass
class OpCodes:
    """Valid op codes to be included in transactions"""

    UP_DATASET = "<UP_DATASET>"
    TRAIN_MODEL = "<TRAIN_MODEL>"
    QUERY_MODEL = "<QUERY_MODEL>"
    EVENT_UPDATE = "<EVENT_UPDATE>"
    UPDATE_PRICE = "<UPDATE_PRICE>"
    DS_INCENTIVE = "<DS_INCENTIVE>"
    MODEL_INCENTIVE = "<MODEL_INCENTIVE>"
    RESPONSE = "<RESP>"
    REJECT = "REJECT"
