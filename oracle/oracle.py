import abc
import dataclasses
import sys
from flask import Flask, request
import os
import json
import copy
import requests
import models
import database
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

    def calc_model_train_price(self, raw_model: str, dataset_name: str, **kwargs):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.TRAIN_MODEL)
        model = models.PredictModel.create(raw_model, **kwargs)
        dataset = database.database.get(dataset_name)
        return model.model_complexity * mult * dataset["size"], txn_id

    def calc_model_query_price(self, model: str):
        """Calculates and returns the latest price and the txn_id where it was changed"""
        mult, txn_id = self.get_price_multiplier(utils.OpCodes.QUERY_MODEL)
        model = models.PredictModel.create(raw_model, **kwargs)
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
        op = txn["note"].split("<ARG>:")[0]
        args = txn["note"].split("<ARG>:")[1:]

        match op:
            case utils.OpCodes.UP_DATASET:
                handler = LocalDataHandler(args[1])
                save_dataset(handler, args[0])
            case utils.OpCodes.QUERY_MODEL:
                ...
            case utils.OpCodes.UPDATE_PRICE:
                ...


class DataHandler:

    SAVE_MODE = 0
    LOAD_MODE = 1

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.env = ""

    @abc.abstractmethod
    def start(self, mode: int):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_chunk(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_all(self, data: bytes):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_chunk(self, chunk_size=1024):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_all(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def finish(self):
        raise NotImplementedError()


class LocalDataHandler(DataHandler):

    def __init__(self, dataset_name):
        super().__init__(dataset_name)
        self.env = "local"
        self.dataset_name = dataset_name
        self.file = None
        self.file_path = f"data/{dataset_name}"
        self.mode = None

    def start(self, mode: int):
        self.mode = mode
        if mode == self.SAVE_MODE:
            if os.path.isfile(self.file_path):
                raise FileExistsError()
            self.file = open(self.file_path, "ab")
        elif mode == self.LOAD_MODE:
            self.file = open(self.file_path, "rb")

    def save_chunk(self, data: bytes):
        if self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def save_all(self, data: bytes):
        if self.mode != self.SAVE_MODE:
            raise AttributeError("Cannot perform save operation when not in save mode!")
        self.file.write(data)

    def load_chunk(self, chunk_size=1024):
        if self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")
        return self.file.read(chunk_size)

    def load_all(self):
        if self.mode != self.LOAD_MODE:
            raise AttributeError("Cannot perform load operation when not in load mode!")
        return self.file.read()

    def finish(self):
        self.file.close()
        self.file = None
        self.mode = None


def save_dataset(handler: DataHandler, link: str):
    handler.start(handler.SAVE_MODE)
    size = 0
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            size += len(chunk)
            handler.save_chunk(chunk)

    handler.finish()
    database.database.set("<DS>"+handler.dataset_name, {"env": handler.env, "size": size})


def load_dataset(handler: DataHandler):
    handler.start(handler.LOAD_MODE)
    data = b''
    chunk = handler.load_chunk()
    while chunk:
        data += chunk
        chunk = handler.load_chunk()

    handler.finish()
    dataset = database.database.get("<DS>"+handler.dataset_name)
    return {**dataset, "data": data}


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
