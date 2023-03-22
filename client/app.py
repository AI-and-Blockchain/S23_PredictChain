from flask import Flask, render_template, request
import os
import json
import copy

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    if os.path.isdir("client"):
        os.chdir("client")
    app.run()
