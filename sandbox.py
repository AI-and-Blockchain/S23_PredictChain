import json
import sys
import base64
import os
import datetime
import pandas as pd
from common import constants
from common import utils
from oracle import dataManager, models, datasets
import oracle.oracleCore as oracleCore
import client.clientCore as clientCore


def sandbox():
    """Wrapper function for any informal testing code"""
    oracleCore.OracleState.init()

    # datasets.load_data("data/dow_jones_index/preprocessed.csv")

    # handler = dataManager.LocalDataHandler("dow_jones_index", "time_step", "stock")

    # model = models.PredictModel.create("GRU", "tom", handler, hidden_dim=5, num_hidden_layers=1)
    # model.train_model(target_attrib="close", num_epochs=50, lookback=10, sub_split_value=0, plot_eval=True)

    # link = "https://matthew-misc-bucket.s3.amazonaws.com/datasets/dow_jones_index.csv"
    # dataManager.save_dataset("local", "dow_jones_index", link, "0txn", "0user", "time_step", sub_split_attrib="stock")

    """
    note = {
        "op": utils.OpCodes.UP_DATASET,
        "ds_name": "dow_jones_index",
        "ds_link": "https://matthew-misc-bucket.s3.amazonaws.com/datasets/dow_jones_index.csv",
        "ds_size": 420,
        "time_attrib": "time_step",
        "sub_split_attrib": "stock"
    }#"""

    """
    note = {
        "op": utils.OpCodes.TRAIN_MODEL,
        "ds_name": "dow_jones_index",
        "raw_model": "GRU",
        "trained_model": "testModel",
        "hidden_dim": 5,
        "num_hidden_layers": 1,
        "num_epochs": 3,
        "target_attrib": "close"
    }#"""

    #"""
    note = {
        "op": utils.OpCodes.QUERY_MODEL,
        "ds_name": "dow_jones_index",
        "trained_model": "testModel",
        "model_input": [
            [1, 0, 56, 16.98, 17.15, 15.96, 16.68, 132981863, -1.76678, 66.17769355, 80023895, 16.81, 16.58, -1.36823,
            76, 0.179856],
            [1, 0, 63, 16.81, 16.94, 16.13, 16.58, 109493077, -1.36823, -17.66315005, 132981863, 16.58, 16.03, -3.31725,
            69, 0.180941],
            [1, 0, 70, 16.58, 16.75, 15.42, 16.03, 114332562, -3.31725, 4.419900447, 109493077, 15.95, 16.11, 1.00313,
            62, 0.187149]
        ]
    }#"""


    mock_txn = {"id": "0txn", "sender": "0user", "payment-transaction": {"amount": float("inf")},
                "note": base64.b64encode(json.dumps(note).encode())}

    oracleCore.OracleState.monitor.process_incoming(mock_txn)


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
