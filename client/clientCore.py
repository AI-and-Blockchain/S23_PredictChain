import sys, os
import requests
import json
from flask import Flask, request
import threading
sys.path.append("../")
import utils


ADDRESS = ""
SECRET = ""


def load_creds():
    global ADDRESS, SECRET
    with open("../.creds/test_client_creds", "r") as file:
        ADDRESS = file.readline().strip("\n")
        SECRET = file.readline().strip("\n")


def get_dataset_upload_price(size: int):
    """Retrieves the upload price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS, f"dataset_upload_price?size={size}"))
    return resp.json()


def get_model_train_price(raw_model: str, dataset_name: str):
    """Retrieves the model price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS,
                        f"model_train_price?model={raw_model}&dataset_name={dataset_name}"))
    return resp.json()


def get_model_query_price(trained_model: str):
    """Retrieves the model price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS, f"model_query_price?model={trained_model}"))
    return resp.json()


def add_dataset(link: str, dataset_name: str, data_size: int):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model"""
    op = utils.OpCodes.UP_DATASET # op is included in locals() and is passed inside the note
    return utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, get_dataset_upload_price(data_size),
                          note=json.dumps(locals().copy()))


def train_model(raw_model: str, new_model: str, dataset_name: str, **kwargs):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model"""
    op = utils.OpCodes.TRAIN_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_train_price(raw_model, dataset_name),
                          note=json.dumps(locals().copy()))


def query_model(trained_model: str, model_input):
    """Creates a transaction to ask for a query from the specified model"""
    op = utils.OpCodes.QUERY_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_query_price(trained_model),
                          note=json.dumps(locals().copy()))


class ClientTransactionMonitor(utils.TransactionMonitor):
    """Class to keep the user updated on incoming transactions or responses from the oracle"""
    def process_incoming(self, txn):
        """Processes the latest incoming transactions to the user"""
        # TODO: Alert user of incoming transaction
        print("Incoming transaction: ", txn)


def command_line():
    help_menu = """\
            h, ?: Help menu
            q: Quit
        """

    command = ""
    while command != "q":
        command = input("Command: ")
        match command:
            case "h" | "?":
                print(help_menu)
            case "txn":
                print(utils.transact(ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, 1,
                                     note=f"{utils.OpCodes.UP_DATASET}<ARG>:testarg1<ARG>:testarg2"))

    monitor.halt()
    print("Client stop")


app = Flask(__name__)
# TODO: Client endpoints for communicating with front end


if __name__ == "__main__":

    load_creds()

    if os.path.isdir("client"):
        os.chdir("client")

    monitor = ClientTransactionMonitor(ADDRESS)
    monitor.monitor()

    app.run(host="localhost", port=utils.CLIENT_SERVER_PORT)

    # command_line()
