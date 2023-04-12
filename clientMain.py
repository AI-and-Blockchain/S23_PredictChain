import os
from client.clientCore import *
from subprocess import Popen


if __name__ == "__main__":

    ClientState.init()

    ClientState.monitor.monitor()

    react_dir = os.path.join(os.getcwd(), "client/predict-chain-ui")

    print("Running front end...")
    try:
        p = Popen(['npm', 'start'], cwd=react_dir)
    except FileNotFoundError:
        p = Popen(['npm', 'start'], cwd=react_dir, shell=True)

    try:
        app.run(host=utils.CLIENT_SERVER_HOST, port=utils.CLIENT_SERVER_PORT)
    except Exception:
        print("Terminating front end...")
        p.terminate()