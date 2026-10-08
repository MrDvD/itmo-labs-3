import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict
import pandas as pd

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

    for mode in ['random']:
        folds = ReportFiller.split_dataset(df, test_size=cfg['test_size'], random_state=cfg['random_seed'], k=cfg['k'], mode=mode)

        train_data, test_data = folds[0]

        plot_path = os.path.join(pics_path, f'folds_{mode}.pdf')
        ReportFiller.plot_folds(df, folds, plot_path=plot_path)
        ReportFiller.plot_validation_comparison(
            folds,
            test_data,
            plot_path=os.path.join(pics_path, f'feature_distributions_{mode}.pdf'),
            target_col=target_column,
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
            train_data,
            test_data,
            target_column,
            alpha=cfg['alpha'],
        )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()