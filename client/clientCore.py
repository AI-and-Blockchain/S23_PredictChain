from __future__ import annotations
import sys, os
import requests
import json
from flask import Flask
from common import utils





class ClientState:
    """Allows for the client state to persist between classes"""

    ADDRESS = ""
    SECRET = ""
    monitor: ClientTransactionMonitor = None

    @classmethod
    def init(cls):
        with open(".creds/test_client_creds", "r") as file:
            cls.ADDRESS = file.readline().strip("\n")
            cls.SECRET = file.readline().strip("\n")

        cls.monitor = ClientTransactionMonitor(cls.ADDRESS)


class ClientTransactionMonitor(utils.TransactionMonitor):
    """Class to keep the user updated on incoming transactions or responses from the oracle"""

    def __init__(self, address: str, all_time=False):
        super(ClientTransactionMonitor, self).__init__(address, all_time=all_time)
        self.txns = []

    def process_incoming(self, txn):
        """Processes the latest incoming transactions to the user"""
        # TODO: Alert user of incoming transaction
        print("Incoming transaction: ", txn)

    def pop_txns(self):
        """Removes all unobserved transactions from the queue"""
        tmp = self.txns
        self.txns = []
        return tmp


def get_dataset_upload_price(ds_size: int):
    """Retrieves the upload price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS, f"dataset_upload_price?ds_size={ds_size}"))
    return resp.json()


def get_model_train_price(raw_model: str, ds_name: str):
    """Retrieves the model price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS,
                        f"model_train_price?raw_model={raw_model}&ds_name={ds_name}"))
    return resp.json()


def get_model_query_price(trained_model: str):
    """Retrieves the model price from the oracle.  This can be verified with the returned txn_id"""
    resp = requests.get(os.path.join(utils.ORACLE_SERVER_ADDRESS, f"model_query_price?trained_model={trained_model}"))
    return resp.json()


def add_dataset(ds_link: str, ds_name: str, ds_size: int):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model"""
    op = utils.OpCodes.UP_DATASET # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.ADDRESS, ClientState.SECRET, utils.ORACLE_ALGO_ADDRESS, get_dataset_upload_price(ds_size),
                          note=json.dumps(utils.flatten_locals(locals())))


def train_model(raw_model: str, trained_model: str, ds_name: str, **kwargs):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model"""
    op = utils.OpCodes.TRAIN_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.ADDRESS, ClientState.SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_train_price(raw_model, ds_name),
                          note=json.dumps(utils.flatten_locals(locals())))


def query_model(trained_model: str, model_input):
    """Creates a transaction to ask for a query from the specified model"""
    op = utils.OpCodes.QUERY_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.ADDRESS, ClientState.SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_query_price(trained_model),
                          note=json.dumps(utils.flatten_locals(locals())))


app = Flask(__name__)
# TODO: Client endpoints for communicating with front end


@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the client is running properly"""
    return {"pinged": "client"}


@app.route('/new_account', methods=["POST"])
def create_new_account():
    """Creates a new account keypair and returns it"""
    addr, priv = utils.create_account()
    return {"address": addr, "private_key": priv}


@app.route('/update_state', methods=["GET"])
def update_state():
    """Gets a report of recent updates to the state of the blockchain and reports them back to the user"""
    txns = ClientState.monitor.pop_txns()
    return {"transactions": txns}
