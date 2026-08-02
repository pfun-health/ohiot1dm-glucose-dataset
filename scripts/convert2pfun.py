#!/usr/bin/env python
"""convert2pfun.py — load OhioT1DM data and print a markdown summary."""

import os
from pathlib import Path
from typing import List, Optional

from torch.utils.data import DataLoader

from ohiot1dm_glucose_dataset.data_processor_loader import OhioT1DMDataset

_REPO_ROOT = Path(__file__).parents[1]


def load_data(
    data_folders: Optional[List[str | os.PathLike]] = None,
    nsize: Optional[int] = 100,
) -> OhioT1DMDataset:
    if data_folders is None:
        data_folders = sorted(_REPO_ROOT.glob("Ohio Data/*/*"))
        print("Ohio Data folders:\n", data_folders)
    return OhioT1DMDataset(data_folders, nsize)


def main() -> None:
    ds = load_data()
    df0 = ds.preprocessed_dfs[0]
    print(df0.to_markdown())


if __name__ == "__main__":
    main()
