import sys
import os
import utils

# TODO for checkin: transaction requests on client, wallet creation, IPFS, another model, transaction kwargs


def sandbox(doas: str):
    """Wrapper function for any informal testing code, ensures that it is executed in the correct environment"""
    if doas == "oracle":
        os.chdir("oracle")
        sys.path.append(os.getcwd())
        import oracle.oracleCore as oracleCore
        import oracle.dataManager as dataManager
        import oracle.models as models
        oracleCore.load_creds()
        # Sandbox code below

        monitor = oracleCore.OracleTransactionMonitor(utils.ORACLE_ALGO_ADDRESS, all_time=True)
        monitor.monitor()

    elif doas == "client":
        os.chdir("client")
        sys.path.append(os.getcwd())
        import client.clientCore as clientCore
        clientCore.load_creds()
        # Sandbox code below

        clientCore.train_model("hello", "there", dataset_name="dooble", general="kenobi")
    else:
        raise ValueError("doas user must be one of [oracle, client]!")


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox("oracle") # ================================= #
    # =================================================== #
