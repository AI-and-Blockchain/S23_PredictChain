import abc
import dataclasses
import database
import torch
import torch.nn as nn
from torch.autograd import Variable
# https://www.simplilearn.com/tutorials/machine-learning-tutorial/decision-tree-in-python
from sklearn.tree import DecisionTreeClassifier


class PredictModel:
    model_complexity = 0.0
    base_model_name = ""
    kwargs = {}

    def __init__(self, **kwargs):
        raise NotImplementedError("Base PredictModel class cannot be instantiated!")

    @classmethod
    def create(cls, model_name: str, **kwargs):
        for sub in cls.__subclasses__():
            if sub.__name__ == model_name or sub.base_model_name == model_name:
                return sub(**kwargs)

    @abc.abstractmethod
    def save(self, save_location) -> dict:
        ...

    @abc.abstractmethod
    def load(self, save_location):
        ...


# Define the model
class LSTM(nn.Module, PredictModel):
    # https://medium.com/@gpj/predict-next-number-using-pytorch-47187c1b8e33

    def __init__(self, input_size=0, hidden_size=0, output_size=0):
        super(LSTM, self).__init__()
        self.kwargs = locals()
        # LSTM
        self.lstm = nn.LSTM(input_size, hidden_size)
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)

        self.model_complexity = input_size+hidden_size+output_size
        self.base_model_name = "LSTM"

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out)
        return out

    def save(self, save_location):
        torch.save(self.state_dict(), save_location)
        model_attribs = {"base_model_name": self.base_model_name, "kwargs": self.kwargs}
        return model_attribs

    def load(self, save_location):
        self.load_state_dict(torch.load(save_location))


class RNN(nn.Module, PredictModel):
    # https://www.kaggle.com/code/kanncaa1/recurrent-neural-network-with-pytorch

    def __init__(self, input_size=0, hidden_size=0, layers=0, output_size=0):
        super(RNN, self).__init__()
        self.kwargs = locals()
        # Number of hidden dimensions
        self.hidden_dim = hidden_size
        # Number of hidden layers
        self.layer_dim = layers

        # RNN
        self.rnn = nn.RNN(input_size, hidden_size, layers, batch_first=True, nonlinearity='relu')
        # Fully connected
        self.fc = nn.Linear(hidden_size, output_size)

        self.model_complexity = input_size + hidden_size * layers + output_size
        self.base_model_name = "RNN"

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = Variable(torch.zeros(self.layer_dim, x.size(0), self.hidden_dim))

        # One time step
        out, hn = self.rnn(x, h0)
        out = self.fc(out[:, -1, :])
        return out

    def save(self, save_location):
        torch.save(self.state_dict(), save_location)
        model_attribs = {"base_model_name": self.base_model_name, "kwargs": self.kwargs}
        return model_attribs

    def load(self, save_location):
        self.load_state_dict(torch.load(save_location))


class DecisionTree(DecisionTreeClassifier, PredictModel):
    def __init__(self, **kwargs):
        super(DecisionTree, self).__init__(**kwargs)
        self.kwargs = locals()
        self.model_complexity = self.get_n_leaves() + self.get_depth()
        self.base_model_name = "DTree"

    def save(self, save_location):
        # TODO: Save tree params
        model_attribs = {"base_model_name": self.base_model_name, "kwargs": self.kwargs}
        return model_attribs

    def load(self, save_location):
        # TODO: Load tree params
        ...


def get_trained_model(model_name: str):
    model_attribs = database.database.get("<MODEL>" + model_name)
    model = PredictModel.create(model_name, **model_attribs["kwargs"])
    model.load(model_attribs["save_location"])
    return model


def save_trained_model(model: PredictModel, save_location: str):
    model_attribs = model.save(save_location)
    database.database.set("<MODEL>"+model.base_model_name, {"save_location": save_location, **model_attribs})


# Train the model
def train(model, data, loss_fn, optimizer, num_epochs):
    for epoch in range(num_epochs):
        for input_sequence, target in data:
            input_sequence = torch.Tensor(input_sequence).view(len(input_sequence), 1, -1)
            target = torch.Tensor(target).view(len(target), -1)

            # Forward pass
            output = model(input_sequence)
            loss = loss_fn(output, target)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()


# Test the model
def test(model, data, loss_fn):
    total_loss = 0
    for input_sequence, target in data:
        input_sequence = torch.Tensor(input_sequence).view(len(input_sequence), 1, -1)
        target = torch.Tensor(target).view(len(target), -1)
        output = model(input_sequence)
        total_loss += loss_fn(output, target).item()
    return total_loss / len(data)


def test_LSTM():
    # Set up the model, data, loss function and optimizer
    model = LSTM(1, 32, 1)
    data = [(list(range(10)), list(range(1, 11))), (list(range(10, 20)), list(range(11, 21)))]
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters())

    # Train the model
    train(model, data, loss_fn, optimizer, num_epochs=100)

    # Use the model to make predictions
    input_sequence = torch.Tensor(list(range(10, 20))).view(10, 1, -1)
    output = model(input_sequence)
    prediction = output[-1].item()
    print(f'Predicted next number: {prediction:.4f}')


def test_decision_tree():
    tree = DecisionTree(criterion="entropy", random_state=100, max_depth=3, min_samples_leaf=5)
    tree.fit(x, y)
    prediction = tree.predict(x)

# TODO: Add more basic models
