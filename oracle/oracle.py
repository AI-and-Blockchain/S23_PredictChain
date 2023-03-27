import abc
import dataclasses
import sys
import time
import base64
from flask import Flask, request
import os
import json
import copy
import requests
import models
import dataManager
sys.path.append("../")
import utils


class Pricing:
    mult_cache = {}

    def calc_dataset_upload_price(self, size: int):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.UP_DATASET)
        return size * mult, txn_id

    def calc_model_train_price(self, raw_model: str, dataset_name: str, **kwargs):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)
        model = models.PredictModel.create(raw_model, **kwargs)
        dataset = dataManager.database.get(dataset_name)
        return model.model_complexity * mult * dataset["size"], txn_id

    def calc_model_query_price(self, model_name: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.QUERY_MODEL)
        model = models.get_trained_model(model_name)
        return model.model_complexity * mult, txn_id

    def get_price_multiplier(self, op: str) -> tuple[float, str]:
        """Gets the price multiplier from the database and returns it and the txn_id where it was last changed"""
        if not self.mult_cache.get(op):
            # get price from database

            self.mult_cache[op] = dataManager.database.get("<PRICE>"+op)

        return self.mult_cache[op]["mul"], self.mult_cache[op]["txn_id"]

    def set_price_multiplier(self, op: str, new_mul: float):
        """Sends an update txn.  Stores txn_id and the new price multiplier in the database"""
        txn = utils.transact(utils.ORACLE_ALGO_ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, 1,
                             note=f"{utils.OpCodes.UPDATE_PRICE}<ARG>:{op}<ARG>:{new_mul}")

        self.mult_cache[op] = {"op": op, "mul": new_mul, "txn_id": txn["id"]}
        # Save txn_id to database
        dataManager.database.set("<PRICE>"+op, {"op": op, "mul": new_mul, "txn_id": txn["id"]})


class OracleTransactionMonitor(utils.TransactionMonitor):

    def process_incoming(self, txn):
        """Execute operations based on the OP code of the incoming transaction"""
        txn["note"] = base64.b64decode(txn["note"]).decode()
        # Split into OP and ARGS
        op = txn["note"].split("<ARG>:")[0]
        args = txn["note"].split("<ARG>:")[1:]

        match op:
            case utils.OpCodes.UP_DATASET:
                handler = dataManager.LocalDataHandler(args[1])
                return dataManager.save_dataset(handler, args[0])
            case utils.OpCodes.QUERY_MODEL:
                model = models.get_trained_model(args[0])
                return model(args[1])
            case utils.OpCodes.UPDATE_PRICE:
                ...
            case utils.OpCodes.TRAIN_MODEL:
                model = models.PredictModel.create(args[0], )
                handler = dataManager.LocalDataHandler(args[1])
                dataset = dataManager.load_dataset(handler)


app = Flask(__name__)


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


if __name__ == '__main__':

    with open(".creds/test_oracle_creds", "r") as file:
        SECRET = file.readline()

    if os.path.isdir("oracle"):
        os.chdir("oracle")

    monitor = OracleTransactionMonitor(utils.ORACLE_ALGO_ADDRESS)
    monitor.monitor()

    app.run(host=utils.ORACLE_SERVER_HOST, port=utils.ORACLE_SERVER_PORT)
