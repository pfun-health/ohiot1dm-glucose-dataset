---
layout: default
title: Models
parent: API Reference
nav_order: 2
---

# Models
{: .no_toc }

**Module:** `ohiot1dm_glucose_dataset.lstm_model`

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## SimpleLSTM

```python
class SimpleLSTM(torch.nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        output_size: int,
    ) -> None
```

A single hidden-layer LSTM followed by a linear output layer.
Architecture follows Mirshekarian et al. with `BatchNorm1d` on the input.

**Parameters**

| Name | Type | Default in training | Description |
|---|---|---|---|
| `input_size` | `int` | 7 | Number of input features per time step |
| `hidden_size` | `int` | 5 | Number of LSTM hidden units |
| `num_layers` | `int` | 1 | Number of stacked LSTM layers |
| `output_size` | `int` | 7 | Number of output features |

**Architecture diagram**

```
Input  (batch, seq_len, input_size)
  │
  ├─ BatchNorm1d(input_size)          # applied per feature across the batch
  │
  ├─ LSTM(input_size → hidden_size,   # batch_first=True
  │       num_layers layers)
  │        └─ uses zero-initialised h₀, c₀
  │
  └─ Linear(hidden_size → output_size)   # applied to the last time step only

Output (batch, output_size)
```

**`forward(x: Tensor) → Tensor`**

| Parameter | Shape | Description |
|---|---|---|
| `x` | `(batch, seq_len, input_size)` | Input sequence |
| returns | `(batch, output_size)` | Prediction for the next time step |
