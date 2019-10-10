import pandas as pd
from sklearn.datasets.base import Bunch

from ..transport import load_parquet_dataset


def load_ihdp():
    base = "https://raw.github.com/inovex/justcause-data/master/ihdp/"

    covariates, replications = load_parquet_dataset(base, "ihdp")

    replications["sample_id"] = replications.groupby("rep").cumcount()
    full = pd.merge(covariates, replications, how="left", on="sample_id")
    full["ite"] = full["y_1"] - full["y_0"]

    cov_names = list(covariates.columns)
    cov_names.remove("sample_id")

    ihdp = Bunch(data=full, covariate_names=cov_names, has_test=True)

    return ihdp
