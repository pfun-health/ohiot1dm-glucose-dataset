#!/usr/bin/env python

"""convert2pfun.py"""

import os
from typing import Optional, List
from torch.utils.data import DataLoader
from ohiot1dm_glucose_dataset.data_processor_loader import OhioT1DMDataset
from pathlib import Path


def load_data(
    data_folders: Optional[List[str | os.PathLike]] = None, nsize: Optional[int] = 100
):
    if data_folders is None:
        data_folders = [p for p in Path("Ohio Data/").rglob("*/*")]
        print("Ohio Data folders:\n", data_folders)
    ds = OhioT1DMDataset(data_folders, nsize)
    return ds


def main():
    ds = load_data()
    df0 = ds.preprocessed_dfs[0]
    print(df0.to_markdown())


if __name__ == "__main__":
    main()
