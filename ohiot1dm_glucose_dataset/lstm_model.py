import torch.nn as nn
import torch as t


class SimpleLSTM(nn.Module):
    """Single hidden-layer LSTM followed by a linear output layer.

    Architecture follows Mirshekarian et al. with an added BatchNorm1d
    applied to the input at each time step.

    Args:
        input_size:  Number of input features per time step.
        hidden_size: Number of LSTM hidden units.
        num_layers:  Number of stacked LSTM layers.
        output_size: Number of output features (typically equals input_size).
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        output_size: int,
    ) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_norm = nn.BatchNorm1d(input_size)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: t.Tensor) -> t.Tensor:
        h0 = t.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = t.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        return self.fc(out[:, -1, :])
