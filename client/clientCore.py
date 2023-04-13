from __future__ import annotations
from typing import Any
import sys, os
import requests
import json
from flask import Flask, request, send_file, send_from_directory
from common import utils, constants
from flask_cors import CORS

class ClientState:
    """Allows for the client state to persist between classes"""

    CLIENT_ADDRESS = ""
    CLIENT_SECRET = ""
    monitor: ClientTransactionMonitor = None

    @classmethod
    def init(cls):
        """Loads in the client credentials and initializes the monitor"""

        with open("creds/client.creds", "r") as file:
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


def get_dataset_upload_price(ds_size: int) -> tuple[int, str]:
    """Retrieves the upload price from the oracle.  This can be verified with the returned transaction id

    :param ds_size: The size of the dataset that is planned to upload
    :return: The price of uploading a dataset and the transaction id where that price was last modified"""

    url = f"http://{constants.ORACLE_SERVER_ADDRESS}/dataset_upload_price?ds_size={ds_size}"
    resp_json = requests.get(url).json()
    return resp_json["price"], resp_json["txn_id"]


def get_model_train_price(raw_model: str, ds_name: str, hidden_dim: int, num_hidden_layers: int) -> tuple[int, str]:
    """Retrieves the model price from the oracle.  This can be verified with the returned transaction id

    :param raw_model: The name of the base model
    :param ds_name: The name of the dataset to train the model on
    :param hidden_dim: The dimension of the hidden layers
    :param num_hidden_layers: The number of hidden layers to put into the model
    :return: The price of training a model and the transaction id where that price was last modified"""

    url = f"http://{constants.ORACLE_SERVER_ADDRESS}/model_train_price?raw_model={raw_model}&ds_name={ds_name}" \
        f"&hidden_dim={hidden_dim}&num_hidden_layers={num_hidden_layers}"
    resp_json = requests.get(url).json()
    return resp_json["price"], resp_json["txn_id"]


def get_model_query_price(trained_model: str) -> tuple[int, str]:
    """Retrieves the query price from the oracle.  This can be verified with the returned transaction id

    :param trained_model: The name of the trained model to query
    :return: The price of querying a model and the transaction id where that price was last modified"""

    url = f"http://{constants.ORACLE_SERVER_ADDRESS}/model_query_price?trained_model={trained_model}"
    resp_json = requests.get(url).json()
    return resp_json["price"], resp_json["txn_id"]


def add_dataset(ds_name: str, ds_link: str, ds_size: int, time_attrib: str, endpoint="", sub_split_attrib=""):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model

    :param ds_name: The name that will be assigned to the new dataset
    :param ds_link: The URL that links to the dataset.  This URL must yield a stream of bytes upon GET
    :param ds_size: The size of the dataset
    :param time_attrib: The attribute of the data that denotes the passage of time
    :param endpoint: The name of the endpoint that is associated with the dataset
    :param sub_split_attrib: The attribute that is used to split the dataset into independent subsets
    :return: The id of the transaction to the oracle"""
    
    op = utils.OpCodes.UP_DATASET # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS, get_dataset_upload_price(ds_size)[0],
                          note=json.dumps(utils.flatten_locals(locals())))


def train_model(raw_model: str, trained_model: str, ds_name: str, num_epochs: int, target_attrib: str, hidden_dim: int, num_hidden_layers: int, **kwargs):
    """Creates a transaction to ask for a new dataset to be added and trained on a base model

    :param raw_model: The raw model to train
    :param trained_model: The name of the new trained model
    :param ds_name: The name of the dataset to train the model on
    :param num_epochs: The number of epochs to train the model for
    :param target_attrib: The name of the attribute that is used to test
    :param hidden_dim: The size of the hidden layers
    :param num_hidden_layers: The number of hidden layers
    :return: The id of the transaction to the oracle"""

    op = utils.OpCodes.TRAIN_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS,
                          get_model_train_price(raw_model, ds_name, hidden_dim, num_hidden_layers)[0],
                          note=json.dumps(utils.flatten_locals(locals())))


def query_model(trained_model: str, model_input: list):
    """Creates a transaction to ask for a query from the specified model

    :param trained_model: The trained model to query
    :param model_input: The input to the trained model
    :return: The id of the transaction to the oracle"""

    op = utils.OpCodes.QUERY_MODEL  # op is included in locals() and is passed inside the note
    return utils.transact(ClientState.CLIENT_ADDRESS, ClientState.CLIENT_SECRET, utils.ORACLE_ALGO_ADDRESS, get_model_query_price(trained_model)[0],
                          note=json.dumps(utils.flatten_locals(locals())))


app = Flask(__name__, static_folder="../docs/sphinx/_static")
CORS(app)

@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the client is running properly

    :return: A ping message"""

    return {"pinged": "client"}


@app.route('/_static/<path:filename>')
def send_static_file(filename):
    """Gets any folder located in the _static directory of the sphinx documentation

    :param filename: The name of the file to get
    :return: The corresponding file"""

    return send_from_directory(app.static_folder, filename)


@app.route('/docs', methods=["GET"])
def docs():
    """Gets the index page for the documentation

    :return: The index page for the documentation"""

    return send_file("../docs/sphinx/index.html")

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


@app.route('/get_dataset_upload_price')
def dataset_upload_price():
    """Requests to see the price for uploading a dataset

    **Query Params**

    * ds_size (int) - The size of the dataset in bytes

    :return: The price of the transaction and the transaction id where that price was last changed"""

    ds_size = int(request.args.get('ds_size'))
    price, txn_id = get_dataset_upload_price(ds_size)
    return {"price": price, "txn_id": txn_id}


@app.route('/get_datasets', methods=["GET"])
def get_datasets():
    """Gets a dictionary of all the stored datasets and their attributes

    :return: A dictionary of all the stored datasets and their attributes"""

    return requests.get(f"http://{constants.ORACLE_SERVER_ADDRESS}/get_datasets").json()


@app.route('/get_models', methods=["GET"])
def get_models():
    """Gets a dictionary of all the stored models and their attributes

    :return: A dictionary of all the stored models and their attributes"""

    return requests.get(f"http://{constants.ORACLE_SERVER_ADDRESS}/get_models").json()


@app.route('/add_dataset', methods=["POST"])
def add_dataset_api():
    """Requests to add a dataset from the UI to the client

    **JSON Data**

    * ds_name (str) - The name that will be assigned to the new dataset
    * ds_link (str) - The URL that links to the dataset.  This URL must yield a stream of bytes upon GET
    * ds_size (str) - The size of the dataset
    * time_attrib (str) - The attribute of the data that denotes the passage of time

    **Optional JSON Data**

    * endpoint (str) - The name of the endpoint that is associated with the dataset
    * sub_split_attrib (str) - The attribute that is used to split the dataset into independent subsets

    :return: The id of the transaction that was created"""

    txn_id = add_dataset(**request.json)
    return txn_id

@app.route('/get_model_train_price', methods=["GET"])
def model_train_price():
    """Requests to see the price for training a model

    **Query Params**

    * raw_model (str) - The name of the raw model to train
    * ds_name (str) - The name of the dataset to train the model on
    * hidden_dim (int) - The dimension of the hidden layers
    * num_hidden_layers (int) - The number of hidden layers to put into the model

    :return: The price of the transaction and the transaction id where that price was last changed"""

    price, txn_id = get_model_train_price(**request.args)
    return {"price": price, "txn_id": txn_id}


# NEED TO TEST
@app.route('/train_model', methods=["POST"])
def train_model_api():
    """Requests to train a model from the UI to the client

    **JSON Data**

    * raw_model (str) - The raw model to train
    * trained_model (str) - The name of the new trained model
    * ds_name (str) - The name of the dataset to train the model on
    * num_epochs (int) - The number of epochs to train the model for
    * target_attrib (str) - The name of the attribute that is used to test
    * hidden_dim (int) - The size of the hidden layers
    * num_hidden_layers (int) - The number of hidden layers

    **Optional JSON Data**

    * sub_split_value (str) - The value used to split the data along the saved sub_split attribute
    * loss_fn_name (str) - The name of the loss function to use while training
    * optimizer_name (str) - The name of the optimizer to use while training
    * learning_rate (float) - The learning rate to use while training
    * training_lookback (int) - The size of the lookback window to use when training time series networks

    :return: The id of the transaction that was created"""

    txn_id = train_model(**request.json)
    return txn_id



# NEED TO TEST
@app.route('/get_model_query_price', methods=["GET"])
def model_query_price():
    """Requests to see the price for querying a model

    **Query Params**

    * trained_model (str) - The name of the trained model to query

    :return: The price of the transaction and the transaction id where that price was last changed"""

    price, txn_id = get_model_query_price(**request.args)
    return {"price": price, "txn_id": txn_id}


# NEED TO TEST
@app.route('/query_model', methods=["POST"])
def query_model_api():
    """Requests to query a model from the UI to the client

    **JSON Data**

    * trained_model (str) - The name of the trained model to query
    * model_input (str) - The input to the model

    :return: The id of the transaction that was created"""

    txn_id = query_model(**request.json)
    return txn_id
