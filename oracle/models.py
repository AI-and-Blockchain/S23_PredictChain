import dataclasses

import torch
import torch.nn as nn
from torch.autograd import Variable
# https://www.simplilearn.com/tutorials/machine-learning-tutorial/decision-tree-in-python
from sklearn.tree import DecisionTreeClassifier


# Define the model
class LSTM(nn.Module):
    # https://medium.com/@gpj/predict-next-number-using-pytorch-47187c1b8e33

    def __init__(self, input_size, hidden_size, output_size):
        super(LSTM, self).__init__()

        # LSTM
        self.lstm = nn.LSTM(input_size, hidden_size)
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)

        self.model_complexity = input_size+hidden_size+output_size

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out)
        return out


class RNN(nn.Module):
    # https://www.kaggle.com/code/kanncaa1/recurrent-neural-network-with-pytorch

    def __init__(self, input_size, hidden_size, layers, output_size):
        super(RNN, self).__init__()

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


class DecisionTree(DecisionTreeClassifier):
    def __init__(self, *args, **kwargs):
        super(DecisionTree, self).__init__(*args, **kwargs)

        self.model_complexity = self.get_n_leaves() + self.get_depth()


def get_raw_model(raw_model: str, **kwargs):
    match raw_model:
        case "RNN":
            return RNN(**kwargs)
        case "LSTM":
            return LSTM(**kwargs)
        case "DTree":
            return DecisionTree(**kwargs)


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
