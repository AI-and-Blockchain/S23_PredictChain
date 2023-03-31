from client.clientCore import *


if __name__ == "__main__":

    ClientState.init()

    ClientState.monitor.monitor()

    app.run(host=utils.ORACLE_SERVER_HOST, port=utils.ORACLE_SERVER_PORT)

    # command_line()