import torch
import torch.nn as nn


# Define the model
class LSTM(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTM, self).__init__()

        # LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size)
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.fc(x)
        return x


class RNN(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim, n_layers):
        super(RNN, self).__init__()

        self.hidden_dim = hidden_dim
        self.n_layers = n_layers

        # RNN layer
        self.rnn = nn.RNN(input_size, hidden_dim, n_layers, batch_first=True)
        # Fully connected layer
        self.fc = nn.Linear(hidden_dim, output_size)

    def forward(self, x):
        batch_size = x.size(0)

        # Initializing hidden state for first input using method defined below
        hidden = self.init_hidden(batch_size)

        # Passing in the input and hidden state into the model and obtaining outputs
        out, hidden = self.rnn(x, hidden)

        # Reshaping the outputs such that it can be fit into the fully connected layer
        out = out.contiguous().view(-1, self.hidden_dim)
        out = self.fc(out)

        return out, hidden

    def init_hidden(self, batch_size):
        # This method generates the first hidden state of zeros which we'll use in the forward pass
        # We'll send the tensor holding the hidden state to the device we specified earlier as well
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_dim)
        return hidden


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


# Setup the model, data, loss function and optimizer
model = NextNumberPredictor(1, 32, 1)
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