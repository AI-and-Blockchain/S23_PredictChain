from client.clientCore import *


if __name__ == "__main__":

    ClientState.init()

    ClientState.monitor.monitor()

    app.run(host=utils.CLIENT_SERVER_HOST, port=utils.CLIENT_SERVER_PORT)
