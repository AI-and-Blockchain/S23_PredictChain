from __future__ import annotations

import math
import sys
import torch
import base64
from flask import Flask, request
import os
import json
from oracle import models, dataManager
from common import utils


class OracleState:
    """Allows for the client state to persist between classes"""

    ORACLE_SECRET = ""
    monitor: OracleTransactionMonitor = None

    @classmethod
    def init(cls):
        """Loads in the oracle credentials and initializes the monitor"""

        with open(".creds/test_oracle_creds", "r") as file:
            file.readline() # throw out address as it is not needed
            cls.ORACLE_SECRET = file.readline().strip("\n")

        cls.monitor = OracleTransactionMonitor()


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
        return int(ds_size * mult / accuracy), txn_id

    @classmethod
    def calc_model_usage_incentive(cls, accuracy: float):
        """Calculates and returns the reward for a model being used
        :param accuracy: The accuracy attained by the model trained on the dataset
        :return: The reward for having trained a useful model and the transaction id of the last time the reward multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.MODEL_INCENTIVE)
        return int(mult / accuracy), txn_id

    @classmethod
    def calc_dataset_upload_price(cls, ds_size: int):
        """Calculates and returns the latest price and the transaction id where it was changed
        :param ds_size: The size of the dataset that is to be uploaded
        :return: The price of uploading a dataset and the transaction id of the last time the price multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.UP_DATASET)
        return int(ds_size * mult), txn_id

    @classmethod
    def calc_model_train_price(cls, raw_model: str, ds_name: str, **kwargs):
        """Calculates and returns the latest price and the transaction id where it was changed
        :param raw_model: The name of the raw model to train
        :param ds_name: The name of the dataset to train the model on
        :return: The price of training a model and the transaction id of the last time the price multiplier was changed"""

        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)
        if "new_model_name" not in kwargs:
            kwargs["new_model_name"] = "tmp"

        handler = dataManager.load_dataset(ds_name)[0]
        model = models.PredictModel.create(raw_model, data_handler=handler, **kwargs)
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
    def calc_op_price(cls, op: str, ds_name=None, ds_size=None, raw_model=None, trained_model=None, **kwargs):
        """Helper method to get the price for any given operation
        :param op: The operation to calculate the price for
        :param ds_name: The name of the dataset if involved in the operation
        :param ds_size: The size of the dataset if involved in the operation
        :param raw_model: The name of the raw model if involved in the operation
        :param trained_model: The name of the trained model if involved in the operation
        :return: The price of the given operation and the transaction id of the last time the price multiplier was changed"""

        match op:
            case utils.OpCodes.UP_DATASET:
                return cls.calc_dataset_upload_price(ds_size)
            case utils.OpCodes.QUERY_MODEL:
                return cls.calc_model_query_price(trained_model)
            case utils.OpCodes.TRAIN_MODEL:
                return cls.calc_model_train_price(raw_model, ds_name, **kwargs)
    @classmethod
    def get_price_multiplier(cls, mul_op: str) -> tuple[float, str]:
        """Gets the price multiplier from the database and returns it and the transaction id where it was last changed
        :param mul_op: The operation to get the multiplier for
        :return: The multiplier and the transaction id of the last time the multiplier was changed"""

        if not cls.mult_cache.get(mul_op):
            db_mul = dataManager.database.hgetall("<PRICE>" + mul_op)
            if not len(db_mul):
                db_mul = {"mul": 1, "txn_id": "0txn"}
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
        dataManager.database.hset("<PRICE>" + mul_op, mapping={"mul_op": mul_op, "mul": new_mul, "txn_id": txn_id})

        return txn_id


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
        if txn["amount"] < op_price:
            # Reject transaction
            utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, txn["sender"], txn["amount"],
                           note=json.dumps({"op": utils.OpCodes.REJECT, "initial_op": op, "reason": "UNDERFUNDED"}))
            return

        match op:
            case utils.OpCodes.UP_DATASET:
                dataManager.save_dataset(**kwargs, txn_id=txn["id"], user_id=txn["sender"])

            case utils.OpCodes.QUERY_MODEL:
                model, meta, ds_meta = models.get_trained_model(kwargs["model_name"])
                output = model(kwargs["model_input"])
                loss_fn = models.PredictModel.get_loss_fn(model.loss_fn_name)

                # TODO: Get result from outside world
                accuracy = float(torch.sigmoid(-loss_fn(output, target)+math.e**2))

                # Reward model trainer
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, meta[1],
                               Pricing.calc_model_usage_incentive(accuracy)[0],
                               note=json.dumps({"op": utils.OpCodes.MODEL_INCENTIVE, "model_name": model.model_name}))
                # Reward dataset uploader
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, ds_meta[1],
                               Pricing.calc_ds_usage_incentive(dataManager.load_dataset(model.data_handler.dataset_name), accuracy)[0],
                               note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name}))

                # Report result back to the user
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, txn["sender"], 0,
                               note=json.dumps({"op": utils.OpCodes.RESPONSE, "query_result": output}))

            case utils.OpCodes.UPDATE_PRICE:
                # Handle any additional price change logic here if needed
                ...

            case utils.OpCodes.TRAIN_MODEL:
                handler, dataset_attribs = dataManager.load_dataset(kwargs["ds_name"])
                model = models.PredictModel.create(**kwargs, data_handler=handler)
                accuracy, loss = model.train_model(**kwargs)

                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.ORACLE_SECRET, dataset_attribs["user_id"],
                               Pricing.calc_ds_usage_incentive(dataManager.load_dataset(model.data_handler.dataset_name), loss)[0],
                               note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name}))

                models.save_trained_model(model, f"models/{kwargs['trained_model']}", txn["id"], txn["sender"])


app = Flask(__name__)


@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the oracle is running properly
    :return A ping message"""

    return {"pinged": "oracle"}


@app.route('/dataset_upload_price', methods=["GET"])
def report_dataset_upload_price():
    """Report back the latest dataset upload price
    :return: The price of uploading the given dataset and the transaction id where the price multiplier was last changed"""

    price, txn_id = Pricing.calc_dataset_upload_price(**request.args)
    return {"price": price, "txn_id": txn_id}


@app.route('/model_train_price', methods=["GET"])
def report_model_train_price():
    """Report back the latest training price
    :return: The price of training the given model and the transaction id where the price multiplier was last changed"""

    price, txn_id = Pricing.calc_model_train_price(**request.args)
    return {"price": price, "txn_id": txn_id}


@app.route('/model_query_price', methods=["GET"])
def report_model_query_price():
    """Report back the latest query price
    :return: The price of querying the given model and the transaction id where the price multiplier was last changed"""

    price, txn_id = Pricing.calc_model_query_price(**request.args)
    return {"price": price, "txn_id": txn_id}
