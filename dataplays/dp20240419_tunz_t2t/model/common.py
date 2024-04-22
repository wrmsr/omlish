from torch import Tensor
import torch.nn as nn


def initialize_weight(x: nn.Linear) -> None:
    nn.init.xavier_uniform_(x.weight)
    if x.bias is not None:
        nn.init.constant_(x.bias, 0)


class FeedForwardNetwork(nn.Module):
    def __init__(
            self,
            hidden_size: int,
            filter_size: int,
            dropout_rate: float,
    ) -> None:
        super().__init__()

        self.layer1 = nn.Linear(hidden_size, filter_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_rate)
        self.layer2 = nn.Linear(filter_size, hidden_size)

        initialize_weight(self.layer1)
        initialize_weight(self.layer2)

    def forward(
            self,
            x: Tensor,
    ) -> Tensor:
        x = self.layer1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.layer2(x)
        return x
