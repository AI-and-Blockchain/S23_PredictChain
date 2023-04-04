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

    SECRET = ""
    monitor: OracleTransactionMonitor = None

    @classmethod
    def init(cls):
        with open(".creds/test_oracle_creds", "r") as file:
            file.readline() # throw out address as it is not needed
            cls.SECRET = file.readline().strip("\n")

        cls.monitor = OracleTransactionMonitor()


class Pricing:
    """Class to keep track and modify the pricing of transactions"""
    mult_cache = {}

    @classmethod
    def calc_ds_usage_incentive(cls, ds_size: int, accuracy: float):
        """Calculates and returns the reward for a database being used in a model"""
        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.DS_INCENTIVE)
        return int(ds_size * mult / accuracy), txn_id

    @classmethod
    def calc_model_usage_incentive(cls, accuracy: float):
        """Calculates and returns the reward for a model being used"""
        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.MODEL_INCENTIVE)
        return int(mult / accuracy), txn_id

    @classmethod
    def calc_dataset_upload_price(cls, ds_size: int):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.UP_DATASET)
        return int(ds_size * mult), txn_id

    @classmethod
    def calc_model_train_price(cls, raw_model: str, ds_name: str, **kwargs):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)
        if "new_model_name" not in kwargs:
            kwargs["new_model_name"] = "tmp"

        handler = dataManager.load_dataset(ds_name)[0]
        model = models.PredictModel.create(raw_model, data_handler=handler, **kwargs)
        return int(model.model_complexity * mult * handler.size), txn_id

    @classmethod
    def calc_model_query_price(cls, trained_model: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = cls.get_price_multiplier(utils.OpCodes.QUERY_MODEL)
        model = models.get_trained_model(trained_model)[0]
        return int(model.model_complexity * mult), txn_id

    @classmethod
    def calc_op_price(cls, op: str, ds_size=None, raw_model=None, trained_model=None, ds_name=None, **kwargs):
        """Helper method to get the price for any given operation"""
        match op:
            case utils.OpCodes.UP_DATASET:
                return cls.calc_dataset_upload_price(ds_size)
            case utils.OpCodes.QUERY_MODEL:
                return cls.calc_model_query_price(trained_model)
            case utils.OpCodes.TRAIN_MODEL:
                return cls.calc_model_train_price(raw_model, ds_name, **kwargs)
    @classmethod
    def get_price_multiplier(cls, mul_op: str) -> tuple[float, str]:
        """Gets the price multiplier from the database and returns it and the txn_id where it was last changed"""
        if not cls.mult_cache.get(mul_op):
            db_mul = dataManager.database.hgetall("<PRICE>" + mul_op)
            if not len(db_mul):
                db_mul = {"mul": 1, "txn_id": "0txn"}
            cls.mult_cache[mul_op] = db_mul

        return cls.mult_cache[mul_op]["mul"], cls.mult_cache[mul_op]["txn_id"]

    @classmethod
    def set_price_multiplier(cls, mul_op: str, new_mul: float):
        """Sends an update txn.  Stores txn_id and the new price multiplier in the database"""
        op = utils.OpCodes.UPDATE_PRICE  # op is included in locals() and is passed inside the note
        txn_id = utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, utils.ORACLE_ALGO_ADDRESS, 0,
                             note=json.dumps(utils.flatten_locals(locals())))

        cls.mult_cache[mul_op] = {"mul_op": mul_op, "mul": new_mul, "txn_id": txn_id}
        # Save txn_id to database
        dataManager.database.hset("<PRICE>" + mul_op, mapping={"mul_op": mul_op, "mul": new_mul, "txn_id": txn_id})


class OracleTransactionMonitor(utils.TransactionMonitor):
    """Keeps the oracle updated on incoming transactions from users, real world events"""

    def __init__(self, all_time=False):
        super(OracleTransactionMonitor, self).__init__(utils.ORACLE_ALGO_ADDRESS, all_time=all_time)

    def process_incoming(self, txn):
        """Execute operations based on the OP code of the incoming transaction"""
        txn["note"] = json.loads(base64.b64decode(txn["note"]).decode())
        # Split into OP and ARGS
        op = txn["note"].pop("op")
        kwargs = {**txn["note"]}

        op_price, _ = Pricing.calc_op_price(op, **kwargs)
        if txn["amount"] < op_price:
            # Reject transaction
            utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, txn["sender"], txn["amount"],
                           note=json.dumps({"op": utils.OpCodes.REJECT, "initial_op": op, "reason": "UNDERFUNDED"}))
            return

        match op:
            case utils.OpCodes.UP_DATASET:
                return dataManager.save_dataset(**kwargs, txn_id=txn["id"], user_id=txn["sender"])

            case utils.OpCodes.QUERY_MODEL:
                model, meta, ds_meta = models.get_trained_model(kwargs["model_name"])
                output = model(kwargs["model_input"])
                loss_fn = models.PredictModel.get_loss_fn(model.loss_fn_name)

                # TODO: Get result from outside world
                accuracy = float(torch.sigmoid(-loss_fn(output, target)+math.e**2))

                # Reward model trainer
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, meta[1],
                               Pricing.calc_model_usage_incentive(accuracy)[0],
                               note=json.dumps({"op": utils.OpCodes.MODEL_INCENTIVE, "model_name": model.model_name}))
                # Reward dataset uploader
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, ds_meta[1],
                               Pricing.calc_ds_usage_incentive(dataManager.load_dataset(model.data_handler.dataset_name), accuracy)[0],
                               note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name}))

                # Report result back to the user
                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, txn["sender"], 0,
                               note=json.dumps({"op": utils.OpCodes.RESPONSE, "query_result": output}))

            case utils.OpCodes.UPDATE_PRICE:
                # Handle any additional price change logic here if needed
                ...

            case utils.OpCodes.TRAIN_MODEL:
                handler, dataset_attribs = dataManager.load_dataset(kwargs["ds_name"])
                model = models.PredictModel.create(**kwargs, data_handler=handler)
                accuracy, loss = model.train_model(**kwargs)

                utils.transact(utils.ORACLE_ALGO_ADDRESS, OracleState.SECRET, dataset_attribs["user_id"],
                               Pricing.calc_ds_usage_incentive(dataManager.load_dataset(model.data_handler.dataset_name), loss)[0],
                               note=json.dumps({"op": utils.OpCodes.DS_INCENTIVE, "dataset_name": model.data_handler.dataset_name}))

                models.save_trained_model(model, f"models/{kwargs['trained_model']}", txn["id"], txn["sender"])


app = Flask(__name__)


@app.route('/ping', methods=["GET"])
def ping():
    """Accepts pings to report that the oracle is running properly"""
    return {"pinged": "oracle"}


@app.route('/dataset_upload_price', methods=["GET"])
def report_dataset_upload_price():
    """Report back the latest dataset upload price"""
    price, txn_id = Pricing.calc_dataset_upload_price(**request.args)
    return {"price": price, "txn_id": txn_id}


@app.route('/model_train_price', methods=["GET"])
def report_model_train_price():
    """Report back the latest training price"""
    price, txn_id = Pricing.calc_model_train_price(**request.args)
    return {"price": price, "txn_id": txn_id}


@app.route('/model_query_price', methods=["GET"])
def report_model_query_price():
    """Report back the latest query price"""
    price, txn_id = Pricing.calc_model_query_price(**request.args)
    return {"price": price, "txn_id": txn_id}
