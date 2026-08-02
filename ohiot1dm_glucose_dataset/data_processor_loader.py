import os
import zipfile
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from scipy.interpolate import CubicSpline
from torch.utils.data import Dataset, DataLoader
import torch as t

# Base path: repository root (parent of this package directory)
_REPO_ROOT = Path(__file__).parents[1]
path = str(_REPO_ROOT)


class OhioT1DMDataset(Dataset):
    def __init__(self, data_dirs, seq_length):
        self.seq_length = seq_length

        merged_data = pd.DataFrame()
        dataframes = []
        for data_dir in data_dirs:
            for subdir, dirs, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(subdir, file)
                    data_df = pd.read_csv(file_path)
                    merged_data = pd.concat([merged_data, data_df])
                    dataframes.append(data_df)

        merged_data.reset_index(inplace=True)
        scaler, fill_values = get_scaler(merged_data)
        self.scaler = scaler
        self.preprocessed_dfs = [preprocess(scaler, fill_values, df) for df in dataframes]
        self.data = [t.tensor(df.values, dtype=t.float32) for df in self.preprocessed_dfs]

    def __len__(self):
        return sum(len(data) - self.seq_length + 1 for data in self.data)

    def __getitem__(self, index):
        data_idx = 0
        while index >= len(self.data[data_idx]) - self.seq_length + 1:
            index -= len(self.data[data_idx]) - self.seq_length + 1
            data_idx += 1
        sequence = self.data[data_idx][index : index + self.seq_length]
        inputs = sequence[:-1, :]
        target = sequence[-1, :]
        return inputs, target


def create_dataloader(data_dirs, seq_length, batch_size):
    """Create a DataLoader for the given data directories."""
    dataset = OhioT1DMDataset(data_dirs, seq_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    def unscale(data):
        data = data.squeeze(0)
        df = pd.DataFrame(data, columns=dataset.preprocessed_dfs[0].columns)
        unscaled = dataset.scaler.inverse_transform(df)
        return t.tensor(unscaled)[None]

    dataloader.__dict__["unscale"] = unscale
    return dataloader


# Convenience path constants used by training_function and main
train_data_dirs = [
    str(_REPO_ROOT / "Ohio Data" / "Ohio2018_processed" / "train"),
    str(_REPO_ROOT / "Ohio Data" / "Ohio2020_processed" / "train"),
]
test_data_dirs = [
    str(_REPO_ROOT / "Ohio Data" / "Ohio2018_processed" / "test"),
    str(_REPO_ROOT / "Ohio Data" / "Ohio2020_processed" / "test"),
]


def preprocess(scaler, fill_values, data_df):
    """Scale one patient DataFrame and impute missing CBG via cubic spline."""
    data_df1 = data_df.copy()
    missing_cbg_indices = data_df1[data_df1["missing_cbg"] == 1].index

    cs = CubicSpline(
        data_df1.index[~data_df1.index.isin(missing_cbg_indices)],
        data_df1.loc[~data_df1.index.isin(missing_cbg_indices), "cbg"],
    )
    data_df1.loc[missing_cbg_indices, "cbg"] = cs(missing_cbg_indices)

    data_df1 = data_df1.drop(columns=["5minute_intervals_timestamp", "missing_cbg"])

    cbg = data_df1.pop("cbg")
    data_df1 = data_df1.assign(cbg=cbg)

    values = data_df1.values
    values = np.where(np.isnan(values), fill_values, values)

    data_df2 = pd.DataFrame(values, columns=data_df1.columns)
    data_df2 = pd.DataFrame(scaler.transform(data_df2), columns=data_df2.columns)
    return data_df2


def get_scaler(data_df):
    """Fit a MinMaxScaler on the merged training data."""
    data_df1 = data_df.copy()
    missing_cbg_indices = data_df1[data_df1["missing_cbg"] == 1].index

    cs = CubicSpline(
        data_df1.index[~data_df1.index.isin(missing_cbg_indices)],
        data_df1.loc[~data_df1.index.isin(missing_cbg_indices), "cbg"],
    )
    data_df1.loc[missing_cbg_indices, "cbg"] = cs(missing_cbg_indices)

    cbg = data_df1.pop("cbg")
    data_df1 = data_df1.assign(cbg=cbg)

    data_df1 = data_df1.drop(columns=["5minute_intervals_timestamp", "missing_cbg", "index"])

    fill_values = data_df1.min() - 0.01 * np.abs(data_df1.min())
    data_df2 = data_df1.fillna(fill_values)

    scaler = MinMaxScaler()
    scaler.fit(data_df2)

    assert np.isnan(fill_values.values).sum() == 0, "fill_values contained NaN"
    return scaler, fill_values
