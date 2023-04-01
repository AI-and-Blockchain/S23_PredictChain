FROM ubuntu:22.04

RUN echo "Building base container..."

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && apt-get install -y python3.10 python3-pip nodejs npm && rm -rf /var/lib/apt/lists/*

RUN python3 --version && pip3 --version && node --version && npm --version

RUN pip install -r requirements.txt

RUN pwd && ls -la
