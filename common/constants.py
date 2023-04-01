import dataclasses
import os
import algosdk.mnemonic
from algosdk.v2client import algod, indexer

with open(".creds/api_key", "r") as file:
    API_KEY = file.readline().strip("\n")

with open(".creds/storage_api_key", "r") as file:
    STORAGE_KEY = file.readline()


ALGOD_API_ADDRESS = "https://testnet-algorand.api.purestake.io/ps2"
INDEXER_API_ADDRESS = "https://testnet-algorand.api.purestake.io/idx2"
ALGOD_CLIENT = algod.AlgodClient(API_KEY, ALGOD_API_ADDRESS, headers={"X-API-Key": API_KEY})
INDEXER_CLIENT = indexer.IndexerClient(API_KEY, INDEXER_API_ADDRESS, headers={"X-API-Key": API_KEY})

ORACLE_ALGO_ADDRESS = "4GLRF2BVZ32W5H5ISTOH7ZSTL6RVVFDN2QV3M5HEY66K34G2WX67U5ZETA"
ORACLE_SERVER_HOST, ORACLE_SERVER_PORT = "localhost", 8030
CLIENT_SERVER_HOST, CLIENT_SERVER_PORT = "localhost", 8031
ORACLE_SERVER_ADDRESS = f"{ORACLE_SERVER_HOST}:{ORACLE_SERVER_PORT}"


@dataclasses.dataclass
class OpCodes:
    """Valid op codes to be included in transactions"""
    UP_DATASET = "<UP_DATASET>"
    TRAIN_MODEL = "<TRAIN_MODEL>"
    QUERY_MODEL = "<QUERY_MODEL>"
    UPDATE_PRICE = "<UPDATE_PRICE>"
    DS_INCENTIVE = "<DS_INCENTIVE>"
    MODEL_INCENTIVE = "<MODEL_INCENTIVE>"
