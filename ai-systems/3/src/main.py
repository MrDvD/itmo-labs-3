import os

from sklearn.model_selection import train_test_split
import lib.config as config
import pandas as pd
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict, List, Tuple

from lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)

    roc_path = os.path.join(pics_path, 'roc.pdf')
    pr_path = os.path.join(pics_path, 'pr.pdf')

    student_mat = pd.read_csv('/lab/student-mat.csv', sep=';')
    student_por = pd.read_csv('/lab/student-por.csv', sep=';')
    
    context: Dict[str, Any] = {
        'roc_path': os.path.relpath(roc_path, 'report'),
        'pr_path': os.path.relpath(pr_path, 'report'),
    }

    df = pd.concat([student_mat, student_por], ignore_index=True)

    train, test = train_test_split(
        df,
        test_size=cfg['experiment']['test_size'],
        random_state=cfg['experiment']['random_state'],
    )

    target_column = 'higher'
    categorical_columns = ['famsup', 'schoolsup']
    numeric_columns = ['age', 'Medu', 'Fedu', 'absences', 'failures', 'G3', 'studytime']
    predictors = categorical_columns + numeric_columns

    context = ReportFiller.teach_models(
        context,
        cfg['experiment']['C'],
        categorical_columns,
        numeric_columns,
        predictors,
        target_column,
        train,
        test
    )

    Y_matrix = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 1, 0],
        [1, 0, 0],
    ]

    P_matrix = [
        [0.7, 0.6, 0.5],
        [0.3, 0.4, 0.6],
        [0.5, 0.9, 0.2],
        [0.4, 0.5, 0.1],
    ]

    context = ReportFiller.calc_auc_roc(
        context,
        Y_matrix,
        P_matrix
    )

    ReportFiller.plot_roc(
        Y_matrix,
        P_matrix,
        roc_path,
    )

    context = ReportFiller.calc_pr(
        context,
        [x[1] for x in Y_matrix],
        [x[1] for x in P_matrix],
        cfg['experiment']['binary_thresholds'],
        'pr_curve',
    )

    precision_recall_pairs: List[Tuple[float, float]] = list(zip(context['pr_curve']['precision'], context['pr_curve']['recall']))

    ReportFiller.plot_pr_sketch(
        precision_recall_pairs,
        pr_path,
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()