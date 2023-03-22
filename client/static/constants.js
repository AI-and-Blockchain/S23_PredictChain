'use strict';
//import * as algosdk from 'https://cdn.jsdelivr.net/npm/algosdk@v2.1.0/dist/browser/algosdk.min.js';
import * as algosdk from 'algosdk';

const ALGOD_API_ADDRESS = "http://localhost";
const ALGOD_PORT = 4001;
const ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
console.log(algosdk.AlgodClient);
const ALGOD_CLIENT = new algosdk.Algodv2(ALGOD_TOKEN, ALGOD_API_ADDRESS, ALGOD_PORT);

export {ALGOD_CLIENT};