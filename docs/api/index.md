---
layout: default
title: API Reference
nav_order: 4
has_children: true
---

# API Reference

The `ohiot1dm_glucose_dataset` package exposes the following public API:

```python
from ohiot1dm_glucose_dataset import (
    OhioT1DMDataset,
    SimpleLSTM,
    create_dataloader,
    train,
    plot_losses,
    preprocess,
    get_scaler,
    load_ohio_csv,
    convert_ohio_to_pfun,
    fit_patient,
    fit_patients,
    unscale_glucose,
    collect_predictions,
    collect_interpolation,
    regression_metrics,
    glucose_zone,
    zone_metrics,
)
```

Use the sub-pages for detailed descriptions of each symbol:
[Data Loading](data-loading), [Models](models), [Training](training),
[PFun CMA Compatibility](pfun-utils).
