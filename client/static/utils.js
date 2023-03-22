'use strict';
import * as constants from './constants.js';
async function checkBalance(){
    let accountInfo = await constants.ALGOD_CLIENT.accountInformation("addr").do();
    console.log("Account balance: %d microAlgos", accountInfo.amount);
}
