---
layout: default
title: Training
parent: API Reference
nav_order: 3
---

# Training
{: .no_toc }

**Module:** `ohiot1dm_glucose_dataset.training_function`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## train

```python
def train(
    net_class: type,
    input_size: int,
    hidden_size: int,
    num_layers: int,
    output_size: int,
    lr: float = 0.01,
    num_epochs: int = 100,
    batch_size: int = 256,
) -> tuple[list[float], list[float], nn.Module]
```

Full training loop for any `nn.Module` that accepts the standard
`SimpleLSTM`-style constructor signature.

**Learning-rate schedule:** `lr` is divided by 10 at epoch 80 (consistent with
Tena et al., arXiv:2109.02178).

**Checkpointing:** the model state with the lowest validation MSE is restored
at the end and also saved to `best_model.pth` and `simple_lstm_model.pth` in
the current working directory.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `net_class` | `type` | Model class (e.g. `SimpleLSTM`) |
| `input_size` | `int` | Number of input features |
| `hidden_size` | `int` | Number of hidden units |
| `num_layers` | `int` | Number of stacked layers |
| `output_size` | `int` | Number of output features |
| `lr` | `float` | Initial learning rate |
| `num_epochs` | `int` | Total training epochs |
| `batch_size` | `int` | Mini-batch size |

**Returns** `(train_losses, test_losses, model)`:

| Name | Type | Description |
|---|---|---|
| `train_losses` | `list[float]` | Per-epoch mean train MSE |
| `test_losses` | `list[float]` | Per-epoch mean test MSE |
| `model` | `nn.Module` | Best model (lowest validation MSE) |

**Example**

```python
from ohiot1dm_glucose_dataset import SimpleLSTM, train

train_losses, test_losses, model = train(
    net_class=SimpleLSTM,
    input_size=7,
    hidden_size=5,
    num_layers=1,
    output_size=7,
    lr=1e-3,
    batch_size=500,
    num_epochs=150,
)
```

---

## plot_losses

```python
def plot_losses(
    train_losses: list[float],
    test_losses: list[float],
) -> None
```

Displays a 2-panel matplotlib figure showing train and test MSE from epoch 20
onwards (epoch 0–19 skipped to avoid the large initial transient).
