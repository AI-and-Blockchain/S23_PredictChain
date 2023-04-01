import sys
import os
from common import constants
from common import utils
import oracle.oracleCore as oracleCore
import client.clientCore as clientCore


def sandbox():
    """Wrapper function for any informal testing code"""

    clientCore.train_model("hello", "there", dataset_name="dooble", general="kenobi")


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox()
    # =================================================== #
