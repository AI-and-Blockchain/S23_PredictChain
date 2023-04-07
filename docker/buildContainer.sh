#!/bin/bash

if [[ "$(docker images -q predict-chain-base:latest 2> /dev/null)" != "" ]]; then
  echo "Building container..."
  docker build --rm -t predict-chain --build-arg base_img=predict-chain-base:latest .
  else
    echo "Building base container..."
    docker/.buildBaseContainer.sh
    echo "Building container..."
    docker build --rm -t predict-chain --build-arg base_img=predict-chain-base:latest .
fi