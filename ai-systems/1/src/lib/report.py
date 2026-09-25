from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pandas import DataFrame, Timestamp, Timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

class ReportFiller:
    @staticmethod
    def make_eda(context: Dict[str, Any], data: DataFrame, seaborn_plot_path: str, plots_path: str) -> Dict[str, Any]:
        groupby_aggr_result = data.groupby(['Medu', 'sex'])['G3'].agg(['mean', 'median', 'count']).reset_index()

        context['groupby_aggr_result'] = groupby_aggr_result.head()

        current_year = 2026
        birth_years = current_year - data['age']
        random_days = np.random.randint(0, 365, size=len(data))
        data['bday'] = [
            Timestamp(f'{year}-01-01') + Timedelta(days=int(day))
            for year, day in zip(birth_years, random_days)
        ]

        resampled_df = (
            data.resample('ME', on='bday')['G3']
                .mean()
                .reset_index(name='G3')
        )

        context['resampled_df'] = resampled_df.head()

        plt.figure(figsize=(8, 5))
        sns.barplot(data=data, x='reason', y='G3', hue='sex', palette='Set2')
        plt.xlabel('Reason')
        plt.ylabel('G3 Score')
        plt.savefig(seaborn_plot_path)
        plt.close()

        _, axes = plt.subplots(2, 2, figsize=(12, 10))

        sns.histplot(data, y='G3', stat='probability', kde=True, ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Relative frequency histogram & KDE')

        sns.boxplot(x=data['G3'], ax=axes[0, 1], color='lightgreen')
        axes[0, 1].set_title('Boxplot of G3 scores')

        sns.violinplot(
            x=data['sex'], 
            y=data['G3'], 
            hue=data['sex'],
            legend=False,
            ax=axes[1, 0], 
            palette='pastel'
        )
        axes[1, 0].set_title('Violinplot of G3 scores by gender')

        sns.scatterplot(data=data, x='age', y='G3', hue='sex', ax=axes[1, 1])
        axes[1, 1].set_title('Scatterplot: age vs G3 score')

        plt.tight_layout()
        plt.savefig(plots_path)
        plt.close()

        reason_encoded = pd.get_dummies(data, columns=['reason'], prefix='reason', drop_first=False)
        cols = [col for col in reason_encoded.columns if col.startswith('reason_')]
        context['reason_encoded'] = reason_encoded[cols].head()

        return context

    @staticmethod
    def split_dataset(data: DataFrame, test_size: float, random_state: int) -> Tuple[DataFrame, DataFrame]:
        rng = np.random.default_rng(random_state)

        shuffled_indices = rng.permutation(len(data))
        test_set_size = int(len(data) * test_size)
        
        test_indices = shuffled_indices[:test_set_size]
        train_indices = shuffled_indices[test_set_size:]

        return data.iloc[train_indices], data.iloc[test_indices]

    @staticmethod
    def prepare_features(data: DataFrame, categorical_columns: list, numerical_columns: list, target_column: str, is_train: bool = False) -> DataFrame:
        data = pd.get_dummies(data, columns=categorical_columns, drop_first=False)
        if is_train:
            for col in numerical_columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
        scaler = StandardScaler()
        data[numerical_columns + [target_column]] = scaler.fit_transform(data[numerical_columns + [target_column]])
        return data

    @staticmethod
    def teach_model_without_regularization(
        context: Dict[str, Any],
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        target_column: str,
        plot_path: str,
    ):
        X_train = train_data.drop(columns=[target_column])
        y_train = train_data[target_column]

        X_test = test_data.drop(columns=[target_column])
        y_test = test_data[target_column]

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        metrics = {
            "train_rmse": root_mean_squared_error(y_train, y_train_pred),
            "test_rmse": root_mean_squared_error(y_test, y_test_pred),
            "train_r2": r2_score(y_train, y_train_pred),
            "test_r2": r2_score(y_test, y_test_pred),
            "train_mae": mean_absolute_error(y_train, y_train_pred),
            "test_mae": mean_absolute_error(y_test, y_test_pred),
        }

        _, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].scatter(y_test, y_test_pred, alpha=0.6, color="blue")
        axes[0].plot(
            [y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()],
            "r--",
            lw=2,
            label="Ideal Fit",
        )
        axes[0].set_xlabel("y_test")
        axes[0].set_ylabel("y_pred")
        axes[0].set_title("Fact vs Pred")
        axes[0].legend()
        axes[0].grid(True)

        residuals = y_test - y_test_pred
        axes[1].scatter(y_test_pred, residuals, alpha=0.6, color="purple")
        axes[1].axhline(y=0, color="r", linestyle="--", lw=2)
        axes[1].set_xlabel("y_pred")
        axes[1].set_ylabel("y_test - y_pred")
        axes[1].set_title("Residuals vs Predicted Values")
        axes[1].grid(True)

        plt.tight_layout()

        plt.savefig(plot_path, dpi=300)
        plt.close()

        context['regression_results'] = {
            "model": model,
            "metrics": metrics,
            "predictions": {
                "train": y_train_pred,
                "test": y_test_pred,
            },
            "coefficients": pd.Series(model.coef_, index=X_train.columns),
            "intercept": model.intercept_,
        }

        return context

    @staticmethod
    def teach_model_with_regularization(
        context: Dict[str, Any],
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        target_column: str,
        plot_path: str,
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

        random_seed = context.get("random_seed", 42)
        lasso_model = Lasso(alpha=alpha, random_state=random_seed)
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

        _, axes = plt.subplots(1, 2, figsize=(14, 5))

        coef_df = pd.DataFrame(
            {
                "Ridge (L2)": ridge_model.coef_.ravel(),
                "Lasso (L1)": lasso_model.coef_.ravel(),
            },
            index=X_train.columns,
        )

        coef_df.plot(kind="bar", ax=axes[0], alpha=0.8)
        axes[0].axhline(0, color="black", linestyle="--", linewidth=0.8)
        axes[0].set_title("Feature Weights")
        axes[0].set_ylabel("Weight")
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].grid(True, linestyle=":", alpha=0.6)

        axes[1].scatter(
            y_test,
            y_pred_ridge_test,
            alpha=0.6,
            color="blue",
            label="Ridge",
        )
        axes[1].scatter(
            y_test,
            y_pred_lasso_test,
            alpha=0.6,
            color="orange",
            label="Lasso",
        )

        y_min = float(y_test.min())
        y_max = float(y_test.max())
        axes[1].plot(
            [y_min, y_max], [y_min, y_max], "r--", lw=2, label="Ideal Fit"
        )

        axes[1].set_xlabel("y_test")
        axes[1].set_ylabel("y_pred")
        axes[1].set_title("Ridge vs Lasso: Fact vs Pred")
        axes[1].legend()
        axes[1].grid(True)

        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

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