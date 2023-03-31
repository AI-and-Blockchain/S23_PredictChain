from oracle.oracleCore import *


if __name__ == "__main__":

    OracleState.init()

    OracleState.monitor.monitor()

    app.run(host=utils.ORACLE_SERVER_HOST, port=utils.ORACLE_SERVER_PORT)

    # command_line()