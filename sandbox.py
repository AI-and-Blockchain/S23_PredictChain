import sys
import os
import datetime
import pandas as pd
from common import constants
from common import utils
from oracle import dataManager, models
from oracle.oracleUtils import datasets
import oracle.oracleCore as oracleCore
import client.clientCore as clientCore


def sandbox():
    """Wrapper function for any informal testing code"""

    # datasets.load_data("data/dow_jones_index/preprocessed.csv")

    handler = dataManager.LocalDataHandler("dow_jones_index", "time_step", "stock")

    model = models.LSTM("tom", handler, 5, 1)
    model.train_model(num_epochs=3, lookback=3, sub_split_value=0, output_attrib="close")


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
