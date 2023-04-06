from __future__ import annotations
import abc
import dataclasses
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common import utils
from oracle import dataManager
import torch
import torch.nn as nn
from torch.autograd import Variable
# https://www.simplilearn.com/tutorials/machine-learning-tutorial/decision-tree-in-python
from sklearn.tree import DecisionTreeClassifier


class PredictModel:

    model_complexity = 0.0
    base_model_name = ""

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "mae", **kwargs):
        """Interface for unifying behavior of different predictive models
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param loss_fn_name: The name of the loss function that the model will use"""
        ...

    def init(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "mae", **kwargs):
        """Initializes the values common to all types of predict model
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param loss_fn_name: The name of the loss function that the model will use"""

        # NOTE: __init__() is not used due to multiple inheritance problems with torch.nn models
        self.model_name = model_name
        self.data_handler = data_handler
        self.loss_fn_name = loss_fn_name
        self.kwargs = utils.flatten_locals(locals())

    @staticmethod
    def get_loss_fn(name: str):
        """Gets a loss function by name
        :param name: The name of the loss function
        :return: The torch loss function"""

        match name.lower():
            case "l1" | "mae":
                return torch.nn.L1Loss()
            case "mse":
                return torch.nn.MSELoss()
            case "ce" | "crossentropy":
                return torch.nn.CrossEntropyLoss()

    @staticmethod
    def get_optimizer(name: str):
        """Gets an optimizer by name
        :param name: The name of the optimizer
        :return: The torch optimizer"""

        match name.lower():
            case "adam":
                return torch.optim.Adam
            case "sgd":
                return torch.optim.SGD

    @classmethod
    def subclass_walk(cls, target_cls):
        """Recursively gathers all subclasses of a particular class
        :param target_cls: The class to search the subclasses of
        :return: A list of all the subclasses of this class"""

        all_subs = []
        subs = target_cls.__subclasses__()
        all_subs.extend(subs)
        for sub in subs:
            all_subs.extend(cls.subclass_walk(sub))
        return all_subs

    @classmethod
    def create(cls, base_model_name: str, new_model_name: str, data_handler: dataManager.DataHandler, loss_fn_name="mae", **kwargs) -> PredictModel:
        """Creates a model based off of a model name, returning an instance based off other provided parameters
        :param base_model_name: The name of the base model of this instance
        :param new_model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param loss_fn_name: The name of the loss function that the model will use
        :return: An instance of the specified model"""

        for sub in cls.subclass_walk(cls):
            if sub.__name__ == base_model_name or sub.base_model_name.lower() == base_model_name.lower():
                return sub(new_model_name, data_handler, loss_fn_name=loss_fn_name, **kwargs)

    @abc.abstractmethod
    def train_model(self, **kwargs):
        """Trains the model using the given parameters"""
        ...

    @abc.abstractmethod
    def eval_model(self, **kwargs):
        """Evaluates the model"""
        ...

    @abc.abstractmethod
    def save(self, save_location) -> dict:
        """Saves the model to disk and returns a dict of its attributes
        :param save_location: Saves the information of this given model to the given location"""
        ...

    @abc.abstractmethod
    def load(self, save_location):
        """Loads the model from disk, reapplying all of its loaded attributes
        :param save_location: The location to load the model from"""
        ...


class BaseNN(nn.Module, PredictModel):

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, hidden_dim: int, num_hidden_layers: int, loss_fn_name: str = "mae", **kwargs):
        """Parent class encapsulating the behaviour of other neural network classes
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :param loss_fn_name: The name of the loss function that the model will use"""

        super(BaseNN, self).__init__()
        self.input_size = len(data_handler.dataframe.columns)
        self.output_size = 1 # self.input_size
        local_args = utils.flatten_locals(locals())
        self.init(**local_args)

    def train_model(self, num_epochs: int, target_attrib: str, learning_rate=0.01, optimizer_name="adam", **kwargs):
        """Trains the current neural net, giving regular eval updates over training
        :param num_epochs: The number of epochs to train the model for
        :param target_attrib: The attribute of the dataset to serve as the classifier
        :param learning_rate: The learning rate ofr training
        :param optimizer_name: The name of the optimizer to use while training"""

        loss_fn = self.get_loss_fn(self.loss_fn_name)
        optimizer = self.get_optimizer(optimizer_name)(self.parameters(), lr=learning_rate)

        x_train, y_train, x_test, y_test = self.preprocess_data(target_attrib=target_attrib, **kwargs)
        for epoch in range(num_epochs):
            for input_sequence, target in zip(x_train, y_train):
                input_sequence = torch.from_numpy(input_sequence).type('torch.FloatTensor')
                target = torch.tensor([target]).type('torch.FloatTensor')

                # Forward pass
                output = self.forward(input_sequence)
                # If output is given in batches, choose the last in the sequence
                if len(output.shape) == 2:
                    output = output[-1]
                loss = loss_fn(output, target)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            if epoch % 20 == 0:
                print(f"Evaluation for epoch {epoch}")
                accuracy, loss = self.eval_model(target_attrib, **kwargs)
                print(f"Accuracy: {accuracy}")
                print(f"Loss: {loss}")

    def eval_model(self, target_attrib: str, plot_eval=False, **kwargs):
        """Evaluates the performance of the network
        :param target_attrib: The attribute of the dataset to serve as the classifier
        :param plot_eval: Flag to govern weather pyplots will be generated during evaluation
        :return: The average accuracy of the model and the average loss of the value"""

        loss_fn = self.get_loss_fn(self.loss_fn_name)
        total_loss = 0
        total_accuracy = 0
        total_entries = 0

        _, _, x_test, y_test = self.preprocess_data(target_attrib=target_attrib, **kwargs)

        outputs = []
        targets = []
        for input_sequence, target in zip(x_test, y_test):
            input_sequence = torch.from_numpy(input_sequence).type('torch.FloatTensor')
            target = torch.tensor([target]).type('torch.FloatTensor')

            # Forward pass
            output = self.forward(input_sequence)
            # If output is given in batches, choose the last in the sequence
            if len(output.shape) == 2:
                output = output[-1]

            outputs.append(float(output))
            targets.append(float(target))
            total_accuracy += torch.sigmoid(-loss_fn(output, target)+math.e**2)
            total_loss += loss_fn(output, target).item()
            total_entries += 1

        if plot_eval:
            plt.plot(range(len(outputs)), outputs)
            plt.plot(range(len(outputs)), targets, '-.')
            plt.ylabel('Output')
            plt.show()

        return total_accuracy / total_entries, total_loss / total_entries

    def preprocess_data(self, target_attrib: str, lookback=1, sub_split_value=None, **kwargs):
        """Processes the dataframe from the data handler into labeled training and testing sets
        :param target_attrib: The attribute of the dataset to serve as the classifier
        :param lookback: The size of the sliding time window to give to recurrent models
        :param sub_split_value: The value of the particular sub_split to use
        :return: The labeled training and testing sets"""

        selected_data = self.data_handler.dataframe

        if sub_split_value is not None:
            selected_data = self.data_handler.sub_splits()[sub_split_value]

        selected_data = selected_data.astype(dtype=float).to_numpy()
        time_series = []

        # Sliding window data
        for index in range(len(selected_data) - lookback):
            time_series.append(selected_data[index: index + lookback])

        train_len = int(0.8*len(time_series))
        time_series = np.array(time_series)

        x_train = time_series[:train_len, :-1, :]
        x_test = time_series[train_len:, :-1]

        target_attrib_idx = self.data_handler.dataframe.columns.get_loc(target_attrib)
        y_train = time_series[:train_len, -1, target_attrib_idx]
        y_test = time_series[train_len:, -1, target_attrib_idx]

        return x_train, y_train, x_test, y_test

    def save(self, save_location):
        torch.save(self.state_dict(), save_location)
        model_attribs = {"base_model_name": self.base_model_name, **self.kwargs}
        return model_attribs

    def load(self, save_location):
        self.load_state_dict(torch.load(save_location))


class MLP(BaseNN):

    base_model_name = "MLP"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, hidden_dim: int, num_hidden_layers: int, loss_fn_name: str = "mae"):
        """Multi-layered perceptron implementation
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :param loss_fn_name: The name of the loss function that the model will use"""

        super(MLP, self).__init__(model_name, data_handler, hidden_dim, num_hidden_layers, loss_fn_name)
        # Fully connected layers
        fcs = [nn.Linear(self.input_size, hidden_dim), nn.ReLU()]
        for _ in range(num_hidden_layers-1):
            fcs.extend([nn.Linear(hidden_dim, hidden_dim), nn.ReLU()])
        fcs.append(nn.Linear(hidden_dim, self.output_size))

        # Store layers into sequential
        self.seq = nn.Sequential(*fcs)

        self.model_complexity = self.input_size + hidden_dim*num_hidden_layers + self.output_size

    def forward(self, x):
        out = self.seq(x)
        return out


class GRU(BaseNN):

    # https://blog.floydhub.com/gru-with-pytorch/

    base_model_name = "GRU"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, hidden_dim: int, num_hidden_layers: int, loss_fn_name: str = "mae", drop_prob=0.2):
        """GRU implementation
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :param loss_fn_name: The name of the loss function that the model will use
        :param drop_prob: Probability of dropout"""

        super(GRU, self).__init__(model_name, data_handler, hidden_dim, num_hidden_layers, loss_fn_name)
        self.hidden_dim = hidden_dim
        self.num_hidden_layers = num_hidden_layers

        # GRU
        self.gru = nn.GRU(self.input_size, hidden_dim, num_hidden_layers, dropout=drop_prob)
        self.fc = nn.Linear(hidden_dim, self.output_size)
        self.relu = nn.ReLU()

        self.model_complexity = self.input_size + hidden_dim * num_hidden_layers + self.output_size

    def forward(self, x):
        out, h = self.gru(x)
        out = self.fc(self.relu(out))
        return out

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = weight.new(self.num_hidden_layers, batch_size, self.hidden_dim).zero_()
        return hidden


class LSTM(BaseNN):
    # https://medium.com/@gpj/predict-next-number-using-pytorch-47187c1b8e33
    # https://blog.floydhub.com/gru-with-pytorch/

    base_model_name = "LSTM"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, hidden_dim: int, num_hidden_layers: int, loss_fn_name: str = "mae", drop_prob=0.2):
        """LSTM implementation
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :param loss_fn_name: The name of the loss function that the model will use
        :param drop_prob: Probability of dropout"""

        super(LSTM, self).__init__(model_name, data_handler, hidden_dim, num_hidden_layers, loss_fn_name)
        self.hidden_dim = hidden_dim
        self.num_hidden_layers = num_hidden_layers

        # LSTM
        self.lstm = nn.LSTM(self.input_size, hidden_dim, num_hidden_layers, dropout=drop_prob)
        # Fully connected layer
        self.fc = nn.Linear(hidden_dim, self.output_size)
        self.relu = nn.ReLU()

        self.model_complexity = self.input_size + hidden_dim*num_hidden_layers + self.output_size

    def forward(self, x):
        out, h = self.lstm(x)
        out = self.fc(self.relu(out))
        return out

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = (weight.new(self.n_layers, batch_size, self.hidden_dim).zero_(),
                  weight.new(self.n_layers, batch_size, self.hidden_dim).zero_())
        return hidden


class RNN(BaseNN):

    # https://www.kaggle.com/code/kanncaa1/recurrent-neural-network-with-pytorch

    base_model_name = "RNN"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, hidden_dim: int, num_hidden_layers: int, loss_fn_name: str = "mae"):
        """RNN implementation
        :param model_name: The name given to this instance of a model
        :param data_handler: The handler for the dataset that the model will use
        :param hidden_dim: The dimension of the hidden layers
        :param num_hidden_layers: The number of hidden layers to put into the model
        :param loss_fn_name: The name of the loss function that the model will use"""

        super(RNN, self).__init__(model_name, data_handler, hidden_dim, num_hidden_layers, loss_fn_name)
        self.hidden_dim = hidden_dim
        self.num_hidden_layers = num_hidden_layers

        # RNN
        self.rnn = nn.RNN(self.input_size, hidden_dim, num_hidden_layers, nonlinearity='relu')
        # Fully connected
        self.fc = nn.Linear(hidden_dim, self.output_size)

        self.model_complexity = self.input_size + hidden_dim*num_hidden_layers + self.output_size

    def forward(self, x):
        # Initialize hidden state with zeros

        # One time step
        out, h = self.rnn(x)
        out = self.fc(out)
        return out


class DecisionTree(DecisionTreeClassifier, PredictModel):
    """Decision tree implementation"""

    base_model_name = "DTree"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "mae", **kwargs):
        super(DecisionTree, self).__init__(**kwargs)
        self.init(model_name, data_handler, loss_fn_name, **kwargs)
        self.model_complexity = self.get_n_leaves() + self.get_depth()

    def train_model(self):
        for input_sequence, target in self.data_handler.data_loader():
            self.fit(input_sequence, target)

    def eval_model(self):
        loss_fn = self.get_loss_fn(self.loss_fn_name)
        total_loss = 0
        total_correct = 0
        total_entries = 0
        for input_sequence, target in self.data_handler.data_loader():
            output = self.predict(input_sequence)

            if output == target:
                total_correct += 1
            total_loss += loss_fn(output, target).item()
            total_entries += 1
        return total_correct / total_entries, total_loss / total_entries

    def save(self, save_location):
        # TODO: Save tree params
        model_attribs = {"base_model_name": self.base_model_name, **self.kwargs}
        return model_attribs

    def load(self, save_location):
        # TODO: Load tree params
        ...


def get_trained_model(model_name: str):
    """Gets a trained model by name and returns the model along with transaction and user metadata
    :param model_name: The name of the trained model to load
    :return: The loaded model and associated metadata"""

    model_attribs = dataManager.database.hgetall("<MODEL>" + model_name)
    model = PredictModel.create(model_attribs["base_model_name"], model_name,
                                model_attribs["dataset_name"], model_attribs["loss_fn_name"], **model_attribs["kwargs"])
    model.load(model_attribs["save_location"])
    return model, (model_attribs["txn_id"], model_attribs["user_id"]), (model_attribs["ds_txn_id"], model_attribs["ds_user_id"])


def save_trained_model(model: PredictModel, save_location: str, txn_id: str, user_id: str):
    """Saves a model to disk and to the database along with user and metadata information
    :param model: The model to save
    :param save_location: The location to save the model to
    :param txn_id: The id of the transaction that initiated the saving of this model
    :param user_id: The address of the user that is saving this model"""

    model_attribs = model.save(save_location)
    dataset_attribs = dataManager.database.hgetall("<DS>" + model.data_handler.dataset_name)

    dataManager.database.hset("<MODEL>"+model.model_name, mapping={"save_location": save_location,
                            **model_attribs, "txn_id": txn_id, "user_id": user_id,
                            "ds_txn_id": dataset_attribs["txn_id"], "ds_user_id": dataset_attribs["user_id"]})

