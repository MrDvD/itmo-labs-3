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

    seaborn_plot_path = os.path.join(pics_path, 'school_choice_reason.pdf')
    plots_path = os.path.join(pics_path, 'plots.pdf')
    teach_model_without_regularization_plot_path = os.path.join(pics_path, 'teach_model_without_regularization.pdf')
    teach_model_with_regularization_plot_path = os.path.join(pics_path, 'teach_model_with_regularization.pdf')

    student_mat = pd.read_csv('/lab/student-mat.csv', sep=';')
    student_por = pd.read_csv('/lab/student-por.csv', sep=';')

    df = pd.concat([student_mat, student_por], ignore_index=True)

    df['TotalAlc'] = df['Dalc'] + df['Walc']
    
    context: Dict[str, Any] = {
        'seaborn_plot_path': os.path.relpath(seaborn_plot_path, start=report_dir),
        'plots_path': os.path.relpath(plots_path, start=report_dir),
        'teach_model_with_regularization_plot_path': os.path.relpath(
            teach_model_with_regularization_plot_path, start=report_dir
        ),
        'teach_model_without_regularization_plot_path': os.path.relpath(
            teach_model_without_regularization_plot_path, start=report_dir
        ),
        'test_size': cfg['test_size'],
        'random_seed': cfg['random_seed'],
        'alpha': cfg['alpha'],
    }

    context = ReportFiller.make_eda(context, df, seaborn_plot_path, plots_path)
    train_data, test_data = ReportFiller.split_dataset(df, test_size=cfg['test_size'], random_state=cfg['random_seed'])

    target_column = 'TotalAlc'
    categorical_columns = ['sex', 'famsize', 'Pstatus']
    numeric_columns = ['age', 'Medu', 'Fedu', 'famrel', 'goout', 'absences', 'failures']
    predictors = categorical_columns + numeric_columns
    features = predictors + [target_column]

    train_data = train_data[features]
    test_data = test_data[features]

    train_nans = train_data.isnull().sum().sum()
    test_nans = test_data.isnull().sum().sum()

    if train_nans > 0 or test_nans > 0:
        raise ValueError(f"Found NaN values in train or test data. Train NaNs: {train_nans}, Test NaNs: {test_nans}")


    train_data = ReportFiller.prepare_features(train_data, categorical_columns, numeric_columns, target_column, is_train=True)
    test_data = ReportFiller.prepare_features(test_data, categorical_columns, numeric_columns, target_column)

    context = ReportFiller.teach_model_without_regularization(
        context,
        train_data,
        test_data,
        target_column,
        teach_model_without_regularization_plot_path,
    )
    context = ReportFiller.teach_model_with_regularization(
        context,
        train_data,
        test_data,
        target_column,
        teach_model_with_regularization_plot_path,
        alpha=cfg['alpha'],
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()