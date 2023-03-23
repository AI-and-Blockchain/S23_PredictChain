import sys, os
import requests
import threading
sys.path.append("../")
import utils


with open(".creds/client_creds", "r") as file:
    ADDRESS = file.readline()
    SECRET = file.readline()


def get_model_train_price(raw_model: str, data_size: int):
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS,
                        f"model_train_price?model={raw_model}&data_size={data_size}"))
    return resp.json()


def get_model_query_price(trained_model: str):
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS, f"model_query_price?model={trained_model}"))
    return resp.json()


def add_dataset(link: str, dataset_name: str, raw_model: str, data_size: int):
    return utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_train_price(raw_model, data_size),
                          note=f"{utils.OpCodes.UP_DATASET}<ARG>:{link}<ARG>:{dataset_name}")


def query_model(trained_model: str):
    return utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_query_price(trained_model),
                          note=f"{utils.OpCodes.QUERY_MODEL}<ARG>:{trained_model}")


class ClientTransactionMonitor(utils.TransactionMonitor):

    def process_incoming(self, txn):
        # TODO: Alert user of incoming transaction
        ...
