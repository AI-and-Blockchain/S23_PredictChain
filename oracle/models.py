import abc
import dataclasses
import dataManager
import torch
import torch.nn as nn
from torch.autograd import Variable
# https://www.simplilearn.com/tutorials/machine-learning-tutorial/decision-tree-in-python
from sklearn.tree import DecisionTreeClassifier


class PredictModel:
    model_complexity = 0.0
    base_model_name = ""

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", **kwargs):
        ...

    def init(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", **kwargs):
        self.model_name = model_name
        self.data_handler = data_handler
        self.loss_fn_name = loss_fn_name
        self.kwargs = {"model_name": model_name, "dataset_name": data_handler.dataset_name,
                       "loss_fn_name": loss_fn_name, **locals()["kwargs"]}

    @staticmethod
    def get_loss_fn(name: str):
        match name.lower():
            case "l1" | "mae":
                return torch.nn.L1Loss()
            case "mse":
                return torch.nn.MSELoss()
            case "ce" | "crossentropy":
                return torch.nn.CrossEntropyLoss()

    @staticmethod
    def get_optimizer(name: str):
        match name.lower():
            case "adam":
                return torch.optim.Adam
            case "sgd":
                return torch.optim.SGD

    @classmethod
    def create(cls, base_model_name: str, new_model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", **kwargs):
        for sub in cls.__subclasses__():
            if sub.__name__ == base_model_name or sub.base_model_name == base_model_name:
                return sub(new_model_name, data_handler, loss_fn_name, **kwargs)

    @abc.abstractmethod
    def train_model(self, **kwargs):
        ...

    @abc.abstractmethod
    def eval_model(self, **kwargs):
        ...

    @abc.abstractmethod
    def save(self, save_location) -> dict:
        ...

    @abc.abstractmethod
    def load(self, save_location):
        ...


class NN(nn.Module, PredictModel):

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", input_size=0, output_size=0, **kwargs):
        super(NN, self).__init__()
        self.init(model_name, data_handler, loss_fn_name, input_size=input_size, output_size=output_size, **kwargs)

    def train_model(self, optimizer_name: str, num_epochs: int, learning_rate: float):
        loss_fn = self.get_loss_fn(self.loss_fn_name)
        optimizer = self.get_optimizer(optimizer_name)(self.parameters(), lr=learning_rate)

        for epoch in range(num_epochs):
            for input_sequence, target in self.data_handler.get_data_loader():
                input_sequence = torch.Tensor(input_sequence).view(len(input_sequence), 1, -1)
                target = torch.Tensor(target).view(len(target), -1)

                # Forward pass
                output = self.forward(input_sequence)
                loss = loss_fn(output, target)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

    def eval_model(self):
        loss_fn = self.get_loss_fn(self.loss_fn_name)
        total_loss = 0
        total_correct = 0
        total_entries = 0
        for input_sequence, target in self.data_handler.get_data_loader():
            input_sequence = torch.Tensor(input_sequence).view(len(input_sequence), 1, -1)
            target = torch.Tensor(target).view(len(target), -1)

            output = self.forward(input_sequence)

            if output == target:
                total_correct += 1
            total_loss += loss_fn(output, target).item()
            total_entries += 1
        return total_correct / total_entries, total_loss / total_entries

    def save(self, save_location):
        torch.save(self.state_dict(), save_location)
        model_attribs = {"base_model_name": self.base_model_name, **self.kwargs}
        return model_attribs

    def load(self, save_location):
        self.load_state_dict(torch.load(save_location))


# Define the model
class LSTM(NN):
    # https://medium.com/@gpj/predict-next-number-using-pytorch-47187c1b8e33

    base_model_name = "LSTM"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", input_size=0, hidden_size=0, output_size=0):
        super(LSTM, self).__init__(model_name, data_handler, loss_fn_name, input_size=input_size,
                                   hidden_size=hidden_size, output_size=output_size)
        # LSTM
        self.lstm = nn.LSTM(input_size, hidden_size)
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)

        self.model_complexity = input_size+hidden_size+output_size

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out)
        return out


class RNN(NN):
    # https://www.kaggle.com/code/kanncaa1/recurrent-neural-network-with-pytorch

    base_model_name = "RNN"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", input_size=0, hidden_size=0, layers=0, output_size=0):
        super(RNN, self).__init__(model_name, data_handler, loss_fn_name, input_size=input_size,
                                  hidden_size=hidden_size, layers=layers, output_size=output_size)
        # Number of hidden dimensions
        self.hidden_dim = hidden_size
        # Number of hidden layers
        self.layer_dim = layers

        # RNN
        self.rnn = nn.RNN(input_size, hidden_size, layers, batch_first=True, nonlinearity='relu')
        # Fully connected
        self.fc = nn.Linear(hidden_size, output_size)

        self.model_complexity = input_size + hidden_size * layers + output_size

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = Variable(torch.zeros(self.layer_dim, x.size(0), self.hidden_dim))

        # One time step
        out, hn = self.rnn(x, h0)
        out = self.fc(out[:, -1, :])
        return out


class DecisionTree(DecisionTreeClassifier, PredictModel):

    base_model_name = "DTree"

    def __init__(self, model_name: str, data_handler: dataManager.DataHandler, loss_fn_name: str = "ce", **kwargs):
        super(DecisionTree, self).__init__(**kwargs)
        self.init(model_name, data_handler, loss_fn_name, **kwargs)
        self.model_complexity = self.get_n_leaves() + self.get_depth()

    def train_model(self):
        for input_sequence, target in self.data_handler.get_data_loader():
            self.fit(input_sequence, target)

    def eval_model(self):
        loss_fn = self.get_loss_fn(self.loss_fn_name)
        total_loss = 0
        total_correct = 0
        total_entries = 0
        for input_sequence, target in self.data_handler.get_data_loader():
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
    model_attribs = dataManager.database.hgetall("<MODEL>" + model_name)
    model = PredictModel.create(model_attribs["base_model_name"], model_name,
                                model_attribs["dataset_name"], model_attribs["loss_fn_name"], **model_attribs["kwargs"])
    model.load(model_attribs["save_location"])
    return model, (model_attribs["txn_id"], model_attribs["user_id"]), (model_attribs["ds_txn_id"], model_attribs["ds_user_id"])


def save_trained_model(model: PredictModel, save_location: str, txn_id: str, user_id: str):
    model_attribs = model.save(save_location)
    dataset_attribs = dataManager.database.hgetall("<DS>" + model.data_handler.dataset_name)

    dataManager.database.set("<MODEL>"+model.model_name, {"save_location": save_location,
                            **model_attribs, "txn_id": txn_id, "user_id": user_id,
                            "ds_txn_id": dataset_attribs["txn_id"], "ds_user_id": dataset_attribs["user_id"]})


# TODO: Add more basic models
