import dataclasses
import sys
from flask import Flask, request
import os
import json
import copy
import models
sys.path.append("../")
import utils


with open(".creds/oracle_creds", "r") as file:
    SECRET = file.readline()


# NOTE: Maybe split database uploading and model training into two different operations
class Pricing:
    mult_cache = {}

    def calc_dataset_upload_price(self, size: int):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.UP_DATASET)
        return size * mult, txn_id

    def calc_model_train_price(self, raw_model: str, **kwargs):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)
        model = models.get_raw_model(raw_model, **kwargs)
        return model.model_complexity * mult, txn_id

    def calc_model_query_price(self, model: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.QUERY_MODEL)
        # TODO: Pricing logic
        return 0

    def get_price_multiplier(self, op: str) -> tuple[float, str]:
        """Gets the price multiplier from the database and returns it and the txn_id where it was last changed"""
        if not self.mult_cache.get(op):
            # get price from database
            self.mult_cache[op] = db_mult

        return self.mult_cache[op], txn_id

    def set_price_multiplier(self, op: str):
        """Sends an update txn.  Stores txn_id and the new price multiplier in the database"""
        txn = utils.transact(utils.ORACLE_ALGO_ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, 1,
                       note=f"{utils.OpCodes.UPDATE_PRICE}<ARG>:train<ARG>:{dataset_name}")

        # Save txn_id to database
        ...


class ClientTransactionMonitor(utils.TransactionMonitor):

    def process_incoming(self, txn):
        """Execute operations based on the OP code of the incoming transaction"""
        # Split into OP and ARGS
        data = txn["note"].split("<ARG>:")

        match data[0]:
            case utils.OpCodes.UP_DATASET:
                ...
            case utils.OpCodes.QUERY_MODEL:
                ...
            case utils.OpCodes.UPDATE_PRICE:
                ...


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
    if os.path.isdir("oracle"):
        os.chdir("oracle")
    app.run()