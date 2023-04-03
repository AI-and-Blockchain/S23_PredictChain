#!/bin/bash

docker build -t predict-chain --build-arg base_img=predict-chain-base:latest .