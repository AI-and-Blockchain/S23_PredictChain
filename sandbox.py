import sys
import os
import utils


def sandbox(doas: str):
    """Wrapper function for any informal testing code, ensures that it is executed in the correct environment"""
    if doas == "oracle":
        os.chdir("oracle")
        sys.path.append(os.getcwd())
        import oracle.oracleCore as oracleCore
        import oracle.dataManager as dataManager
        import oracle.models as models
    elif doas == "client":
        os.chdir("client")
        sys.path.append(os.getcwd())
        import client.clientCore as clientCore
    else:
        raise ValueError("doas user must be one of [oracle, client]!")

    # Sandbox code below
    model = models.PredictModel.create("LSTM", "jimbo", dataManager.LocalDataHandler("hello"), "ce", input_size=56, hidden_size=6, output_size=5)
    print(model.model_name, model.base_model_name)


if __name__ == "__main__":
    # =============[NO CODE HERE OR BELOW]=============== #
    sandbox("oracle") # ================================= #
    # =================================================== #
