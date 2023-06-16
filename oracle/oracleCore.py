from __future__ import annotations
import time
import threading
import math
import sys
import torch
import base64
from flask import Flask, request
import os
import json
from oracle import models, dataManager, datasets
from common import utils


class OracleState:
    """Allows for the client state to persist between classes"""

    ORACLE_SECRET = ""
    monitor: OracleTransactionMonitor = None

    @classmethod
    def init(cls):
        """Initializes the internal state of the oracle and initializes the monitor"""

        with open("creds/oracle.creds", "r") as file:
            file.readline() # throw out address as it is not needed
            cls.ORACLE_SECRET = file.readline().strip("\n")

        cls.monitor = OracleTransactionMonitor()

        # Attempt to load database from saved if it exists
        if os.path.exists("database.json"):
            print("Loading database contents from file...")
            dataManager.load_database("database.json")
            print("Database keys", dataManager.database.keys())


class Pricing:
    """Class to keep track and modify the pricing of transactions"""

    mult_cache = {}
    """Dict to keep track of the multipliers for all of the prices"""

    @classmethod
    def calc_ds_usage_incentive(cls, ds_size: int, accuracy: float):
        """Calculates and returns the reward for a dataset being used in a model

        :param ds_size: The size of the dataset that has been used
        :param accuracy: The accuracy attained by the model trained on the dataset
        :return: The reward for having uploaded a useful dataset and the transaction id of the last time the reward multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.DS_INCENTIVE)
        return int(ds_size * mult * accuracy), txn_id

    @classmethod
    def calc_model_usage_incentive(cls, accuracy: float):
        """Calculates and returns the reward for a model being used

        :param accuracy: The accuracy attained by the model trained on the dataset
        :return: The reward for having trained a useful model and the transaction id of the last time the reward multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.MODEL_INCENTIVE)
        return int(mult * accuracy), txn_id

    @classmethod
    def calc_dataset_upload_price(cls, ds_size: int):
        """Calculates and returns the latest price and the transaction id where it was changed

        :param ds_size: The size of the dataset that is to be uploaded
        :return: The price of uploading a dataset and the transaction id of the last time the price multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.UP_DATASET)
        return int(ds_size * mult), txn_id

    @classmethod
    def calc_model_train_price(cls, raw_model: str, ds_name: str, hidden_dim: int, num_hidden_layers: int):
        """Calculates and returns the latest price and the transaction id where it was changed

        :param raw_model: The name of the raw model to train
        :param ds_name: The name of the dataset to train the model on
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :return: The price of training a model and the transaction id of the last time the price multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)

        handler = datasets.load_dataset(ds_name)[0]
        model = models.PredictModel.create(raw_model, "tmp", data_handler=handler,
                                           hidden_dim=hidden_dim, num_hidden_layers=num_hidden_layers)
        return int(model.model_complexity * mult * handler.size), txn_id

    @classmethod
    def calc_model_query_price(cls, trained_model: str):
        """Calculates and returns the latest price and the transaction id where it was changed

        :param trained_model: The name of the trained model to query
        :return: The price of querying that model and the transaction id of the last time the price multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.QUERY_MODEL)
        model = models.get_trained_model(trained_model)[0]
        return int(model.model_complexity * mult), txn_id

    @classmethod
    def calc_op_price(cls, op: str, ds_name=None, ds_size=None, raw_model=None, trained_model=None, hidden_dim=None, num_hidden_layers=None, **_):
        """Helper method to get the price for any given operation

        :param op: The operation to calculate the price for
        :param ds_name: The name of the dataset if involved in the operation
        :param ds_size: The size of the dataset if involved in the operation
        :param raw_model: The name of the raw model if involved in the operation
        :param trained_model: The name of the trained model if involved in the operation
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :return: The price of the given operation and the transaction id of the last time the price multiplier was changed"""

        if op == utils.OpCodes.UP_DATASET:
            return cls.calc_dataset_upload_price(ds_size)
        elif op == utils.OpCodes.QUERY_MODEL:
            return cls.calc_model_query_price(trained_model)
        elif op == utils.OpCodes.TRAIN_MODEL:
            return cls.calc_model_train_price(raw_model, ds_name, hidden_dim, num_hidden_layers)

        return 0, ""

    @classmethod
    def get_price_multiplier(cls, mul_op: str) -> tuple[float, str]:
        """Gets the price multiplier from the database and returns it and the transaction id where it was last changed

        :param mul_op: The operation to get the multiplier for
        :return: The multiplier and the transaction id of the last time the multiplier was changed"""

        if not cls.mult_cache.get(mul_op):
            db_mul = dataManager.database.get("<PRICE>" + mul_op)
            if not db_mul:
                db_mul = {"mul": 0.1, "txn_id": "0txn"}
            cls.mult_cache[mul_op] = db_mul

        return cls.mult_cache[mul_op]["mul"], cls.mult_cache[mul_op]["txn_id"]

    @classmethod
    def set_price_multiplier(cls, mul_op: str, new_mul: float):
        """Sends an update txn.  Stores transaction id and the new price multiplier in the database

        :param mul_op: The operation to set the multiplier for
        :param new_mul: The new multiplier for the price/reward associated with the operation
        :return: The transaction id of the multiplier changing transaction"""

        op = utils.OpCodes.UPDATE_PRICE  # op is included in locals() and is passed inside the note
        txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, utils.ORACLE_ALGO_ADDRESS, 0,
                                note=json.dumps(utils.flatten_locals(locals())))

        cls.mult_cache[mul_op] = {"mul_op": mul_op, "mul": new_mul, "txn_id": txn_id}
        # Save txn_id to database
        dataManager.database.set("<PRICE>" + mul_op, {"mul_op": mul_op, "mul": new_mul, "txn_id": txn_id})

        return txn_id


class EventMonitor:

    query_queue = {}
    _halt = False
    PAUSE_DURATION = 10

    @classmethod
    def query_endpoint(cls, endpoint: str):

        # TODO: Get latest event data from endpoint

        return {}

    def halt(self):
        """Halts the polling of the monitor"""
        self._halt = True

    @classmethod
    def monitor(cls):
        """Starts a thread to monitor any incoming events from the target endpoint"""

        print("Starting event monitor...")

        def inner_mon():
            while not cls._halt:
                queue_clone = cls.query_queue.copy()
                for txn_id in queue_clone:
                    event = cls.query_endpoint(cls.query_queue[txn_id]["endpoint"])
                    utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, utils.ORACLE_ALGO_ADDRESS, 0,
                                   note=json.dumps({"op": utils.OpCodes.EVENT_UPDATE, **cls.query_queue[txn_id],
                                                    "target": event["result"]}))
                    cls.query_queue.pop(txn_id)

                time.sleep(cls.PAUSE_DURATION)

        thread = threading.Thread(target=inner_mon, args=())
        thread.start()


class OracleTransactionMonitor(utils.TransactionMonitor):
    """Keeps the oracle updated on incoming transactions from users, real world events"""

    def __init__(self, all_time=False):
        """Keeps the oracle updated on incoming transactions from users, real world events

        :param all_time: Gathers complete transaction history if ``True`` instead of just recent transactions"""

        super(OracleTransactionMonitor, self).__init__(utils.ORACLE_ALGO_ADDRESS, all_time=all_time)

    def process_incoming(self, txn):
        """Execute operations based on the OP code of the incoming transaction

        :param txn: The incoming transaction"""

        # Decode and parse the note
        txn["note"] = json.loads(base64.b64decode(txn["note"]).decode())
        # Split into OP and ARGS
        op = txn["note"].pop("op")
        kwargs = {**txn["note"]}

        op_price, _ = Pricing.calc_op_price(op, **kwargs)

        def reject(reason: str):
            """Reject the incoming transaction

            :param reason: The reason for rejection"""

            reject_txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, txn["sender"], txn['payment-transaction']['amount'],
                           note=json.dumps({"op": utils.OpCodes.REJECT, "initial_op": op, "reason": reason}))
            print(f"Rejecting the incoming transaction with the reason of {reason}.  Reject transaction id: {reject_txn_id}")

        def accept(msg: str, **note_kwargs):
            """Accept the incoming transaction and sent a confirmation back to the sender

            :param msg: An additional message to print out
            :param note_kwargs: A dictionary or kwargs to send along with the confirmation"""

            tmp_txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, txn["sender"], 0,
                                         note=json.dumps({"op": utils.OpCodes.RESPONSE, "initial_op": op, **note_kwargs}))

            print(f"{msg}. Response transaction id: {tmp_txn_id}")

        if txn['payment-transaction']['amount'] < min(op_price, utils.ALGO_AMOUNT_CAP):
            # Reject transaction
            reject("UNDERFUNDED")
            return

        if op == utils.OpCodes.UP_DATASET:
            try:
                datasets.save_dataset("local", **kwargs, txn_id=txn["id"], user_id=txn["sender"])
            except FileExistsError:
                print("Dataset already exists!")
                reject("DS_EXISTS")
                return
            
            # Report result back to the user
            accept(f"Added a dataset with name {kwargs['ds_name']}", ds_name=kwargs['ds_name'])

        elif op == utils.OpCodes.TRAIN_MODEL:
            handler, dataset_attribs = datasets.load_dataset(kwargs["ds_name"])

            model = models.PredictModel.create(**kwargs, data_handler=handler)
            accuracy, loss = model.train_model(**kwargs)

            models.save_trained_model(model, txn["id"], txn["sender"])

            # Report result back to the user
            accept(f"Trained a {kwargs['raw_model']} model as {kwargs['trained_model']} on dataset {kwargs['ds_name']}",
                   accuracy=accuracy, loss=loss)

            incentive_txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, dataset_attribs["user_id"],
                           Pricing.calc_ds_usage_incentive(int(dataset_attribs["size"]), accuracy)[0],
                           note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name}))
            
            print(f"Database incentive transaction id: {incentive_txn_id}")

        elif op == utils.OpCodes.QUERY_MODEL:
            model, meta, ds_meta = models.get_trained_model(kwargs["trained_model"])

            # Query model
            output = model.query_model(torch.tensor(kwargs["model_input"]))

            output = output.tolist()

            if ds_meta.get("endpoint", ""):
                print("Adding event request to event queue")
                EventMonitor.query_queue[txn["id"]] = {"endpoint": ds_meta["endpoint"], "output": output, "input": kwargs["model_input"],
                                                 "query_user_id": txn["sender"], "query_txn_id": txn["id"]}

            # Report result back to the user
            accept(f"Queried model {kwargs['trained_model']} with a result of {output}", output=output, trained_model=kwargs["trained_model"])

        elif op == utils.OpCodes.EVENT_UPDATE:
            model, meta, ds_meta = models.get_trained_model(kwargs["trained_model"])
            loss_fn = models.PredictModel.get_loss_fn(model.loss_fn_name)
            output, target = kwargs["output"], kwargs["target"]

            accuracy = float(torch.sigmoid(-loss_fn(output, target) + math.e ** 2))

            # Report result back to the user
            resp_txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, kwargs["query_user_id"], 0,
                           note=json.dumps({"op": utils.OpCodes.RESPONSE, "output": output, "target": target,
                                            "accuracy": accuracy}))

            # Reward model trainer
            utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, meta["user_id"],
                           Pricing.calc_model_usage_incentive(accuracy)[0],
                           note=json.dumps({"op": utils.OpCodes.MODEL_INCENTIVE, "trained_model": model.model_name,
                                            "query_txn_id": kwargs["query_txn_id"], "event_txn_id": resp_txn_id}))

            _, dataset_attribs = datasets.load_dataset(model.data_handler.dataset_name)
            # Reward dataset uploader
            utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, ds_meta["user_id"],
                           Pricing.calc_ds_usage_incentive(dataset_attribs["size"], accuracy)[0],
                           note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name,
                                            "query_txn_id": kwargs["query_txn_id"], "event_txn_id": resp_txn_id}))

        elif op == utils.OpCodes.UPDATE_PRICE:
            # Handle any additional price change logic here if needed
            ...


app = Flask(__name__)


@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the oracle is running properly

    :return: A ping message"""

    return {"pinged": "oracle"}


@app.route('/dataset_upload_price', methods=["GET"])
def report_dataset_upload_price():
    """Requests to see the price for uploading a dataset

    **Query Params**

    * ds_size (int) - The size of the dataset in bytes

    :return: The price of the transaction and the transaction id where that price was last changed"""

    price, txn_id = Pricing.calc_dataset_upload_price(int(request.args["ds_size"]))
    return {"price": price, "txn_id": txn_id}


@app.route('/model_train_price', methods=["GET"])
def report_model_train_price():
    """Requests to see the price for training a model

    **Query Params**

    * raw_model (str) - The name of the raw model to train
    * ds_name (str) - The name of the dataset to train the model on
    * hidden_dim (int) - The dimension of the hidden layers
    * num_hidden_layers (int) - The number of hidden layers to put into the model

    :return: The price of the transaction and the transaction id where that price was last changed"""

    price, txn_id = Pricing.calc_model_train_price(request.args["raw_model"], request.args["ds_name"],
                                                   int(request.args["hidden_dim"]), int(request.args["num_hidden_layers"]))
    return {"price": price, "txn_id": txn_id}


@app.route('/model_query_price', methods=["GET"])
def report_model_query_price():
    """Requests to see the price for querying a model

    **Query Params**

    * trained_model (str) - The name of the trained model to query

    :return: The price of the transaction and the transaction id where that price was last changed"""

    price, txn_id = Pricing.calc_model_query_price(request.args["trained_model"])
    return {"price": price, "txn_id": txn_id}


@app.route('/get_datasets', methods=["GET"])
def get_datasets():
    """Gets a dictionary of all the stored datasets and their attributes

    :return: A dictionary of all the stored datasets and their attributes"""

    return dataManager.enum_database("local", "<DS>")


@app.route('/get_models', methods=["GET"])
def get_models():
    """Gets a dictionary of all the stored models and their attributes

    :return: A dictionary of all the stored models and their attributes"""

    return dataManager.enum_database("local", "<MODEL>")
