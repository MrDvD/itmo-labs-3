import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict
import pandas as pd
from sklearn.model_selection import train_test_split

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)

    student_mat = pd.read_csv('/lab/student-mat.csv', sep=';')
    student_por = pd.read_csv('/lab/student-por.csv', sep=';')

    df = pd.concat([student_mat, student_por], ignore_index=True)

    df['TotalAlc'] = df['Dalc'] + df['Walc']
    
    context: Dict[str, Any] = {
        'test_size': cfg['test_size'],
        'random_seed': cfg['random_seed'],
        'alpha': cfg['alpha'],
    }

    target_column = 'TotalAlc'
    categorical_columns = ['sex', 'famsize', 'Pstatus']
    numeric_columns = ['age', 'Medu', 'Fedu', 'famrel', 'goout', 'absences', 'failures']
    predictors = categorical_columns + numeric_columns
    features = predictors + [target_column]

    train_val_df, holdout_test_df = train_test_split(
        df,
        test_size=cfg['test_size'],
        random_state=cfg['random_seed'],
    )

    modes = ['random', 'stratified', 'grouped', 'grouped_one_out', 'time_series']

    for mode in modes:
        print(f"Working with mode: {mode}")
        folds = ReportFiller.split_dataset(
            train_val_df,
            test_size=cfg['test_size'],
            random_state=cfg['random_seed'],
            k=cfg['k'],
            mode=mode,
            groups=(
                train_val_df["famrel"].astype("category").to_numpy()
                if mode == "grouped"
                else train_val_df["failures"].astype("category").to_numpy()
                if mode == "grouped_one_out"
                else None
            ),
            target_col="sex" if mode == "stratified" else None,
            time_col="age" if mode == "time_series" else None,
        )

        ReportFiller.plot_validation_comparison(
            folds,
            holdout_test_df,
            plot_path=os.path.join(pics_path, f'feature_distributions_{mode}.pdf'),
            target_col=target_column,
        )

        for fold in folds:
            train_data, test_data = fold

            plot_path = os.path.join(pics_path, f'folds_{mode}.pdf')
            ReportFiller.plot_folds(
                train_val_df,
                folds,
                mode=mode,
                plot_path=plot_path,
                target_col="sex" if mode == "stratified" else None,
                group_col=(
                    "famrel"
                    if mode == "grouped"
                    else "failures"
                    if mode == "grouped_one_out"
                    else None
                ),
            )

            train_nans = train_data[features].isnull().sum().sum()
            test_nans = test_data[features].isnull().sum().sum()

            if train_nans > 0 or test_nans > 0:
                raise ValueError(f"Found NaN values in train or test data. Train NaNs: {train_nans}, Test NaNs: {test_nans}")

            train_data = train_data[features]
            test_data = test_data[features]

            scaler, train_data = ReportFiller.prepare_features(train_data, categorical_columns, numeric_columns, target_column, is_train=True)
            _, test_data = ReportFiller.prepare_features(test_data, categorical_columns, numeric_columns, target_column, scaler=scaler)

            context = ReportFiller.teach_model(
                context,
                (train_data, test_data),
                target_column,
                alpha=cfg['alpha'],
                fold_type=mode,
            )

    context = ReportFiller.plot_metrics_comparison(
        context,
        modes,
        "metrics_comparison",
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()