import dataclasses
import sys
from flask import Flask, request
import os
import json
import copy
sys.path.append("../")
import utils


with open(".creds/oracle_creds", "r") as file:
    SECRET = file.readline()

# NOTE: Maybe split database uploading and model training into two different operations
class Pricing:
    def calc_model_train_price(self, raw_model: str, data_size: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        # TODO: Pricing logic
        utils.transact(utils.ORACLE_ALGO_ADDRESS, SECRET, utils.ORACLE_ALGO_ADDRESS, 1,
                       note=f"{utils.OpCodes.UPDATE_PRICE}<ARG>:train<ARG>:{dataset_name}")
        return 0

    def calc_model_query_price(self, model: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        # TODO: Pricing logic
        return 0


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


@app.route('/model_train_price', methods=["GET"])
def report_model_train_price():
    """Report back the latest training price"""
    # TODO: Also return txn where the price was last changed
    return {"price": Pricing.calc_model_train_price(*)}

@app.route('/model_query_price', methods=["GET"])
def report_model_query_price():
    """Report back the latest query price"""
    # TODO: Also return txn where the price was last changed
    return {"price": Pricing.calc_model_query_price(*)}


if __name__ == '__main__':
    if os.path.isdir("oracle"):
        os.chdir("oracle")
    app.run()