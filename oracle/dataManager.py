import io
import web3storage
import redis
import json
import requests
import os
import pandas as pd
from common import utils

database = redis.Redis(decode_responses=True)
"""The database that is used to store oracle information"""

web3 = web3storage.Client(utils.STORAGE_KEY)
"""The storage client for IPFS"""


def enum_database(env: str, prefix: str):
    """Enumerates the given database, filtering keys by the given prefix

    :param env: The environment to look for the data in
    :param prefix: The common prefix between all the entry keys that will be enumerated
    :return: A dictionary of all the selected keys"""

    datasets = {}

    if env == "local":
        for key in database.scan_iter(f"{prefix}*"):
            datasets[key] = database.hgetall(key)
    else:
        raise NotImplementedError(f"Environment {env} has not been implemented!")

    return datasets


def load_database(filepath: str, overwrite=False):
    """Loads the contents of a json file and puts each item into the database

    :param filepath: The path to the file to be loaded
    :param overwrite: Flag to determine if an existing key will be overwritten by an incoming value"""

    with open(filepath, "r") as file:
        loaded = json.loads(file.read())

    for key in loaded:
        if not overwrite and database.exists(key):
            continue

        database.hset(key, mapping=loaded[key])


def save_database(filepath: str):
    """Saves the contents of the database to a file

    :param filepath: The file to save the database to"""

    saved = {}

    for key in database.scan_iter():
        saved[key] = database.hgetall(key)

    with open(filepath, "w") as file:
        file.write(json.dumps(saved))

