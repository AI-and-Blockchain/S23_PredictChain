from __future__ import annotations
from typing import Any
import sys, os
import requests
import json
from flask import Flask, request
from common import utils
from flask_cors import CORS

class ClientState:
    """Allows for the client state to persist between classes"""

    CLIENT_ADDRESS = ""
    CLIENT_SECRET = ""
    monitor: ClientTransactionMonitor = None

    @classmethod
    def init(cls):
        """Loads in the client credentials and initializes the monitor"""

        with open(".creds/test_client_creds", "r") as file:
            cls.CLIENT_ADDRESS = file.readline().strip("\n")
            cls.CLIENT_SECRET = file.readline().strip("\n")

        cls.monitor = ClientTransactionMonitor(cls.CLIENT_ADDRESS)


class ClientTransactionMonitor(utils.TransactionMonitor):
    """Class to keep the user updated on incoming transactions or responses from the oracle"""

    def __init__(self, address: str, all_time=False):
        """Class to keep the user updated on incoming transactions or responses from the oracle

        :param address: The address of the user
        :param all_time: Gathers complete transaction history if ``True`` instead of just recent transactions"""

        super(ClientTransactionMonitor, self).__init__(address, all_time=all_time)
        self.txn_queue = []
        """Stores queue of recent transactions for the user to see"""

    def process_incoming(self, txn: dict[str, Any]):
        """Processes the latest incoming transactions to the user

        :param txn: The incoming transaction dictionary"""

        # TODO: Alert user of incoming transaction
        print("Incoming transaction: ", txn)
        self.txn_queue.append(txn)

    def clear_queue(self):
        """Removes all unobserved transactions from the queue

        :return: The list of queued transactions"""

        tmp = self.txn_queue
        self.txn_queue = []
        return tmp


def get_dataset_upload_price(ds_size: int):
    """Retrieves the upload price from the oracle.  This can be verified with the returned transaction id

    :param ds_size: The size of the dataset that is planned to upload
    :return: The price of uploading a dataset and the transaction id where that price was last modified"""
    url = "http://localhost:8030/dataset_upload_price?ds_size=" + ds_size
    resp = requests.get(url)
    return resp.json()


def get_model_train_price(raw_model: str, ds_name: str):
    """Retrieves the model price from the oracle.  This can be verified with the returned transaction id

    :param raw_model: The name of the base model
    :param ds_name: The name of the dataset to train the model on
    :return: The price of training a model and the transaction id where that price was last modified"""

    url = "http://localhost:8030/model_train_price?raw_model=" + raw_model + "&ds_name=" + ds_name
    resp = requests.get(url)
    return resp


def get_model_query_price(trained_model: str):
    """Retrieves the query price from the oracle.  This can be verified with the returned transaction id

    :param trained_model: The name of the trained model to query
    :return: The price of querying a model and the transaction id where that price was last modified"""

    url = "http://localhost:8030/model_query_price?trained_model=" + trained_model
    resp = requests.get(url)
    return resp.json()


def add_dataset(ds_link: str, ds_name: str, ds_size: int):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model

    :param ds_link: The URL that links to the dataset.  This URL must yield a stream of bytes upon GET
    :param ds_name: The name that will be assigned to the new dataset
    :param ds_size: The size of the dataset
    :return: The id of the transaction to the oracle"""

    op = utils.OpCodes.UP_DATASET # op is included in locals() and is passed inside the note
    price = get_dataset_upload_price(ds_size)['price']
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS, price,
                          note=json.dumps(utils.flatten_locals(locals())))


def train_model(raw_model: str, trained_model: str, ds_name: str, **kwargs):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model

    :param raw_model: The raw model to train
    :param trained_model: The name of the new trained model
    :param ds_name: The name of the dataset to train the model on
    :return: The id of the transaction to the oracle"""

    op = utils.OpCodes.TRAIN_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_train_price(raw_model, ds_name),
                          note=json.dumps(utils.flatten_locals(locals())))


def query_model(trained_model: str, model_input):
    """Creates a transaction to ask for a query from the specified model

    :param trained_model: The trained model to query
    :param model_input: The input to the trained model
    :return: The id of the transaction to the oracle"""

    op = utils.OpCodes.QUERY_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_query_price(trained_model),
                          note=json.dumps(utils.flatten_locals(locals())))


app = Flask(__name__)
CORS(app)

@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the client is running properly

    :return: A ping message"""

    return {"pinged": "client"}


@app.route('/new_account', methods=["POST"])
def create_new_account():
    """Creates a new account keypair and returns it

    :return: Newly generated address credentials"""

    addr, priv = utils.create_account()
    return {"address": addr, "private_key": priv}


@app.route('/update_state', methods=["GET"])
def update_state():
    """Gets a report of recent updates to the state of the blockchain and reports them back to the user

    :return: A list of transactions that have recently been received by the client address"""

    txns = ClientState.monitor.clear_queue()
    return {"transactions": txns}


@app.route('/get_dataset_upload_size')
def dataset_upload_size():
    """Requests to see the price for a dataset
    :requires: size of data in bytes
    :example: ?ds_size=77

    :return: {Price, TXN ID}"""

    ds_size = request.args.get('ds_size')
    response = get_dataset_upload_price(ds_size)
    return response



""" 
File "C:\Users\pattec3\Desktop\Academics\AI&B\project\predict-chain\oracle\dataManager.py", line 169, in start
    raise FileExistsError()
FileExistsError
"""
@app.route('/add_dataset', methods=["GET"])
def add_dataset_api():
    """Requests to add a dataset from the UI to the client
    :requires: link to data, name and size of file in bytes
    :example: ?ds_link=https://matthew-misc-bucket.s3.amazonaws.com/datasets/dow_jones_index.csv&ds_name=test&ds_size=77

    :return: Oracle transaction ID """

    ds_link = request.args.get('ds_link')
    ds_name = request.args.get('ds_name')
    ds_size = request.args.get('ds_size')
    response = add_dataset(ds_link, ds_name, ds_size)
    return response



# NEED TO TEST
@app.route('/train_model', methods=["GET"])
def train_model_api():
    raw_model = request.args.get('raw_model')
    trained_model = request.args.get('trained_model')
    ds_name = request.args.get('ds_name')
    response = train_model(raw_model, trained_model, ds_name)
    return response 

# NEED TO TEST
@app.route('/get_model_train_price', methods=["GET"])
def model_train_price():
    raw_model = request.args.get('raw_model')
    ds_name = request.args.get('ds_name')
    response = get_model_train_price(raw_model, ds_name)
    return response

# NEED TO TEST
@app.route('/get_model_query_price', methods=["GET"])
def model_query_price():
    trained_model = request.args.get('trained_model')
    response = get_model_query_price(trained_model)
    return response


# NEED TO TEST
@app.route('/query_model', methods=["GET"])
def query_model_api():
    trained_model = request.args.get('trained_model')
    model_input = request.args.get('model_input')
    response = query_model(trained_model, model_input)
    return response