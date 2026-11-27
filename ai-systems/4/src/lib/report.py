from typing import Dict, Any, Tuple, Optional, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
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
                        shuffle=True,
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

            case _:
                raise ValueError(f"Invalid mode: {mode}.")

    @staticmethod
    def plot_folds(
        data: DataFrame,
        folds: List[Tuple[DataFrame, DataFrame]],
        mode: str,
        plot_path: str,
        time_col: Optional[str] = None,
        target_col: Optional[str] = None,
        group_col: Optional[str] = None,
    ) -> None:
        if time_col is not None:
            data = data.sort_values(by=time_col)

        n_samples = len(data)
        n_folds = len(folds)
        show_groups = mode in ("stratified", "grouped", "grouped_one_out") and (target_col is not None or group_col is not None)
        ratio_col = group_col if mode in ["grouped","grouped_one_out"] else target_col

        if show_groups:
            fig, (ax, ax_ratio) = plt.subplots(
                2, 1, figsize=(12, max(3, n_folds * 0.6) + 3),
                gridspec_kw={"height_ratios": [max(3, n_folds * 0.6), 3]},
            )
        else:
            fig, ax = plt.subplots(figsize=(12, max(3, n_folds * 0.6)))

        for fold_num, (train_df, test_df) in enumerate(folds):
            y_pos = n_folds - 1 - fold_num
            train_positions = data.index.get_indexer(train_df.index)
            test_positions = data.index.get_indexer(test_df.index)

            if len(train_positions) > 0:
                ax.barh(y_pos, 1.0, left=train_positions, color="#3498db", height=0.6)
            if len(test_positions) > 0:
                ax.barh(y_pos, 1.0, left=test_positions, color="#e74c3c", height=0.6)

            # Annotate the group used by this fold (for grouped mode)
            if mode in ["grouped", "grouped_one_out"] and group_col is not None and len(test_df) > 0:
                grp = test_df[group_col].mode().iloc[0]
                ax.text(
                    n_samples * 1.01, y_pos, f"grp={grp}",
                    va="center", ha="left", fontsize=8, color="#333",
                )

        ax.set_yticks(range(n_folds))
        ax.set_yticklabels([f"Fold {i + 1}" for i in reversed(range(n_folds))])
        ax.set_xlabel("Sample Index" if time_col is None else f"Index (sorted by {time_col})")
        ax.set_xlim(0, n_samples)
        ax.legend(
            handles=[
                mpatches.Patch(color="#3498db", label="Train"),
                mpatches.Patch(color="#e74c3c", label="Test"),
            ],
            loc="upper right", bbox_to_anchor=(1.15, 1),
        )

        if show_groups:
            classes = sorted(data[ratio_col].unique())
            n_classes = len(classes)
            x = np.arange(n_folds)
            w = 0.4 / n_classes

            for i, cls in enumerate(classes):
                train_r = [(tr[ratio_col] == cls).mean() for tr, _ in folds]
                test_r = [(te[ratio_col] == cls).mean() for _, te in folds]
                offset = (i - (n_classes - 1) / 2) * w * 2
                ax_ratio.bar(x + offset - w / 2, train_r, w, label=f"{cls} (train)")
                ax_ratio.bar(x + offset + w / 2, test_r, w, label=f"{cls} (test)")

            ax_ratio.set_xticks(x)
            ax_ratio.set_xticklabels([f"Fold {i + 1}" for i in range(n_folds)])
            ax_ratio.set_ylabel("Ratio")
            ax_ratio.set_xlabel(f"Group ({ratio_col})")
            ax_ratio.legend(fontsize=8)

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
        fold: Tuple[DataFrame, DataFrame],
        target_column: str,
        alpha: float,
        fold_type: str,
    ) -> Dict[str, Any]:
        train_data, test_data = fold
        X_train = train_data.drop(columns=[target_column])
        y_train = train_data[target_column].to_numpy()

        X_test = test_data.drop(columns=[target_column])
        y_test = test_data[target_column].to_numpy()

        ridge_model = Ridge(alpha=alpha)
        ridge_model.fit(X_train, y_train)

        key = f"fold_{fold_type}_metrics"

        y_pred = ridge_model.predict(X_test)

        new_context = context.copy()
        new_context[key] = new_context.get(key, list())
        new_context[key].append({
            "rmse": root_mean_squared_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
            "mae": mean_absolute_error(y_test, y_pred),
        })

        return new_context

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

    @staticmethod
    def plot_metrics_comparison(
        context: Dict[str, Any],
        modes: List[str],
        key: str
    ) -> Dict[str, Any]:
        all_metrics = dict()
        for cross_val_type in modes:
            subkey = f"fold_{cross_val_type}_metrics"
            metrics = context[subkey]
            n_folds = len(metrics)
            all_metrics[subkey] = {
                "rmse": sum([m["rmse"] for m in metrics]) / n_folds,
                "r2": sum([m["r2"] for m in metrics]) / n_folds,
                "mae": sum([m["mae"] for m in metrics]) / n_folds,
            }

        new_context = context.copy()
        new_context[key] = all_metrics
        return new_context