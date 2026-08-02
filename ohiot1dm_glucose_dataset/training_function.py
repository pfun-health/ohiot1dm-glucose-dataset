import torch as t
from torch import nn

import torch.optim as optim
import matplotlib.pyplot as plt
from pathlib import Path

from ohiot1dm_glucose_dataset.data_processor_loader import create_dataloader

_REPO_ROOT = Path(__file__).parents[1]
train_data_dirs = [
    str(_REPO_ROOT / "Ohio Data" / "Ohio2018_processed" / "train"),
    str(_REPO_ROOT / "Ohio Data" / "Ohio2020_processed" / "train"),
]
test_data_dirs = [
    str(_REPO_ROOT / "Ohio Data" / "Ohio2018_processed" / "test"),
    str(_REPO_ROOT / "Ohio Data" / "Ohio2020_processed" / "test"),
]


def train(
    net_class: type,
    input_size: int,
    hidden_size: int,
    num_layers: int,
    output_size: int,
    lr: float = 0.01,
    num_epochs: int = 100,
    batch_size: int = 256,
):
    """Train *net_class* on the Ohio T1DM dataset and return the best model.

    Learning rate is divided by 10 at epoch 80 (following Tena et al.).
    Returns (train_losses, test_losses, model).
    """
    train_dataloader = create_dataloader(
        data_dirs=train_data_dirs,
        seq_length=25,
        batch_size=batch_size,
    )
    test_dataloader = create_dataloader(
        data_dirs=test_data_dirs,
        seq_length=25,
        batch_size=batch_size,
    )

    model = net_class(input_size, hidden_size, num_layers, output_size)
    print(model)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    train_losses: list[float] = []
    test_losses: list[float] = []
    best_validation_loss = float("inf")
    best_model_dict = None

    for epoch in range(num_epochs):
        # ── Learning-rate schedule ──────────────────────────────────────────
        if epoch == 80:
            for g in optimizer.param_groups:
                g["lr"] /= 10

        # ── Training pass ───────────────────────────────────────────────────
        epoch_train_losses = []
        model.train()
        for inputs, targets in train_dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            epoch_train_losses.append(loss)

        # ── Validation pass ─────────────────────────────────────────────────
        model.eval()
        epoch_test_losses = []
        with t.no_grad():
            for inputs, targets in test_dataloader:
                outputs = model(inputs)
                loss = criterion(outputs[:, -1], targets[:, -1])
                epoch_test_losses.append(loss.item())

        mean_train_loss = t.mean(t.tensor(epoch_train_losses))
        mean_test_loss = t.mean(t.tensor(epoch_test_losses))
        print(
            f"Epoch {epoch + 1}/{num_epochs}"
            f"\tTrain MSE: {mean_train_loss.item():.9f}"
            f"\tTest MSE:  {mean_test_loss.item():.9f}"
        )
        train_losses.append(mean_train_loss.item())
        test_losses.append(mean_test_loss.item())

        if mean_test_loss.item() < best_validation_loss:
            best_validation_loss = mean_test_loss.item()
            best_model_dict = model.state_dict()

    plot_losses(train_losses, test_losses)
    t.save(best_model_dict, "best_model.pth")

    assert best_model_dict is not None
    model.load_state_dict(best_model_dict)
    t.save(model.state_dict(), "simple_lstm_model.pth")

    return train_losses, test_losses, model


def plot_losses(train_losses: list[float], test_losses: list[float]) -> None:
    """Plot train and test MSE loss curves (skipping the first 20 epochs)."""
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(8, 5))

    axs[0].plot(t.arange(len(train_losses[20:])), train_losses[20:], label="train")
    axs[0].set_ylabel("MSE Loss")
    axs[0].legend()
    axs[0].set_title("Train Loss")

    axs[1].plot(t.arange(len(test_losses[20:])), test_losses[20:], label="test", color="orange")
    axs[1].set_ylabel("MSE Loss")
    axs[1].legend()
    axs[1].set_title("Test Loss")

    plt.xlabel("Epoch (offset by 20)")
    plt.tight_layout()
    plt.show()