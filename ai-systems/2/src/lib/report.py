from typing import Dict, Any, Tuple, Optional, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from pandas import DataFrame
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import (
    train_test_split, 
    StratifiedKFold, 
    GroupKFold, 
    LeaveOneGroupOut, 
    TimeSeriesSplit
)

class ReportFiller:
    @staticmethod
    def split_dataset(
        data: DataFrame, 
        test_size: float,
        random_state: int,
        mode: str,
        k: int,
        target_col: Optional[str] = None,
        groups: Optional[np.ndarray] = None,
        time_col: Optional[str] = None,
        purge_gap: int = 0
    ) -> List[Tuple[DataFrame, DataFrame]]:
        match mode:
            case "random":
                folds = list()
                for i in range(k):
                    train_indices, test_indices = train_test_split(
                        data.index, 
                        test_size=test_size, 
                        random_state=random_state + i,
                        shuffle=True
                    )
                    folds.append((data.loc[train_indices], data.loc[test_indices]))
                return folds

            case "stratified":
                if target_col is None:
                    raise ValueError("target_col must be provided for stratified mode.")
                
                skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=random_state)
                return [
                    (data.iloc[train_indices], data.iloc[test_indices])
                    for train_indices, test_indices in skf.split(data, data[target_col])
                ]

            case "grouped":
                if groups is None:
                    raise ValueError("groups array must be provided for grouped mode.")
                
                gkf = GroupKFold(n_splits=k)
                return [
                    (data.iloc[train_indices], data.iloc[test_indices])
                    for train_indices, test_indices in gkf.split(data, groups=groups)
                ]

            case "grouped_one_out":
                if groups is None:
                    raise ValueError("groups array must be provided for grouped_one_out mode.")
                
                logo = LeaveOneGroupOut()
                return [
                    (data.iloc[train_indices], data.iloc[test_indices])
                    for train_indices, test_indices in logo.split(data, groups=groups)
                ]

            case "time_series":
                if time_col is not None:
                    data = data.sort_values(by=time_col)
                
                tscv = TimeSeriesSplit(n_splits=k)
                return [
                    (data.iloc[train_indices], data.iloc[test_indices])
                    for train_indices, test_indices in tscv.split(data)
                ]

            case "purged":
                if time_col is not None:
                    data = data.sort_values(by=time_col)
                tscv = TimeSeriesSplit(n_splits=k)
                folds = list()
                for train_indices, test_indices in tscv.split(data):
                    if purge_gap > 0:
                        train_indices = train_indices[:-purge_gap]
                    
                    folds.append((
                        data.iloc[train_indices], 
                        data.iloc[test_indices]
                    ))

                return folds

            case _:
                raise ValueError(f"Invalid mode: {mode}.")

    @staticmethod
    def plot_folds(
        data: DataFrame,
        folds: List[Tuple[DataFrame, DataFrame]],
        plot_path: str,
        time_col: Optional[str] = None,
    ) -> None:

        if time_col is not None:
            data = data.sort_values(by=time_col)

        n_samples = len(data)
        n_folds = len(folds)

        _, ax = plt.subplots(figsize=(12, max(3, n_folds * 0.6)))

        for fold_num, (train_df, test_df) in enumerate(folds):
            y_pos = n_folds - 1 - fold_num

            train_positions = data.index.get_indexer(train_df.index)
            test_positions = data.index.get_indexer(test_df.index)

            if len(train_positions) > 0:
                ax.barh(
                    y_pos,
                    width=1.0,
                    left=train_positions,
                    color="#3498db",
                    edgecolor="none",
                    height=0.6,
                )

            if len(test_positions) > 0:
                ax.barh(
                    y_pos,
                    width=1.0,
                    left=test_positions,
                    color="#e74c3c",
                    edgecolor="none",
                    height=0.6,
                )

        ax.set_yticks(range(n_folds))
        ax.set_yticklabels([f"Fold {i + 1}" for i in reversed(range(n_folds))])
        ax.set_xlabel("Sample Index" if time_col is None else f"Index (sorted by {time_col})")
        ax.set_xlim(0, n_samples)

        train_patch = mpatches.Patch(color="#3498db", label="Train")
        test_patch = mpatches.Patch(color="#e74c3c", label="Test")
        ax.legend(
            handles=[train_patch, test_patch],
            loc="upper right",
            bbox_to_anchor=(1.15, 1),
        )

        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

    @staticmethod
    def prepare_features(
        data: DataFrame,
        categorical_columns: list,
        numerical_columns: list,
        target_column: str,
        is_train: bool = False,
        scaler: StandardScaler | None = None
    ) -> Tuple[StandardScaler, DataFrame]:
        data = pd.get_dummies(data, columns=categorical_columns, drop_first=False)
        if scaler is None:
            scaler = StandardScaler()
        if is_train:
            mask = pd.Series(True, index=data.index)
            for col in numerical_columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                mask &= (data[col] >= Q1 - 1.5 * IQR) & (data[col] <= Q3 + 1.5 * IQR)
            data = data[mask].reset_index(drop=True)
            scaler = scaler.fit(data[numerical_columns + [target_column]])
        data[numerical_columns + [target_column]] = scaler.transform(data[numerical_columns + [target_column]])
        return scaler, data

    @staticmethod
    def teach_model(
        context: Dict[str, Any],
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        target_column: str,
        alpha: float,
    ) -> Dict[str, Any]:
        X_train = train_data.drop(columns=[target_column])
        y_train = train_data[target_column].to_numpy()

        X_test = test_data.drop(columns=[target_column])
        y_test = test_data[target_column].to_numpy()

        ridge_model = Ridge(alpha=alpha)
        ridge_model.fit(X_train, y_train)

        y_pred_ridge_train = ridge_model.predict(X_train)
        y_pred_ridge_test = ridge_model.predict(X_test)

        ridge_metrics = {
            "train_rmse": root_mean_squared_error(y_train, y_pred_ridge_train),
            "test_rmse": root_mean_squared_error(y_test, y_pred_ridge_test),
            "train_r2": r2_score(y_train, y_pred_ridge_train),
            "test_r2": r2_score(y_test, y_pred_ridge_test),
            "train_mae": mean_absolute_error(y_train, y_pred_ridge_train),
            "test_mae": mean_absolute_error(y_test, y_pred_ridge_test),
        }

        lasso_model = Lasso(alpha=alpha)
        lasso_model.fit(X_train, y_train)

        y_pred_lasso_train = lasso_model.predict(X_train)
        y_pred_lasso_test = lasso_model.predict(X_test)

        lasso_metrics = {
            "train_rmse": root_mean_squared_error(y_train, y_pred_lasso_train),
            "test_rmse": root_mean_squared_error(y_test, y_pred_lasso_test),
            "train_r2": r2_score(y_train, y_pred_lasso_train),
            "test_r2": r2_score(y_test, y_pred_lasso_test),
            "train_mae": mean_absolute_error(y_train, y_pred_lasso_train),
            "test_mae": mean_absolute_error(y_test, y_pred_lasso_test),
        }

        context["regularization_results"] = {
            "alpha": alpha,
            "ridge": {
                "model": ridge_model,
                "metrics": ridge_metrics,
                "coefficients": pd.Series(
                    ridge_model.coef_.ravel(), index=X_train.columns
                ),
            },
            "lasso": {
                "model": lasso_model,
                "metrics": lasso_metrics,
                "coefficients": pd.Series(
                    lasso_model.coef_.ravel(), index=X_train.columns
                ),
            },
        }

        return context

    @staticmethod
    def plot_validation_comparison(
        folds: List[Tuple[pd.DataFrame, pd.DataFrame]],
        test: pd.DataFrame,
        plot_path: str,
        target_col: str,
    ) -> None:
        fig, ax = plt.subplots(figsize=(8, 5))

        for i, (_, val_df) in enumerate(folds):
            min_val = int(np.floor(min(val_df[target_col].min(), test[target_col].min())))
            max_val = int(np.ceil(max(val_df[target_col].max(), test[target_col].max())))
    
            bins = np.arange(min_val, max_val + 1, 1)
            sns.histplot(
                val_df[target_col],
                color="#db6521",
                kde=True,
                stat="density",
                alpha=0.35,
                ax=ax,
                label="Fold validation" if i == 0 else None,
                bins=bins,
            )

        sns.histplot(
            test[target_col],
            color="#2680c9",
            kde=True,
            stat="density",
            alpha=0.55,
            ax=ax,
            label="Actual test",
            bins=bins,
        )

        ax.set_xlabel(target_col)
        ax.set_ylabel("Density")
        ax.legend()

        fig.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()