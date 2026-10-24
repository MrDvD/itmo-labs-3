import os

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
import lib.config as config
import pandas as pd
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)

    student_mat = pd.read_csv('/lab/student-mat.csv', sep=';')
    student_por = pd.read_csv('/lab/student-por.csv', sep=';')
    
    context: Dict[str, Any] = {}

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
    # features = predictors + [target_column]

    reg = LogisticRegression()

    preprocessor = ColumnTransformer(
        transformers=[
            (
                'cat',
                OneHotEncoder(handle_unknown='ignore', sparse_output=False),
                categorical_columns,
            ),
            (
                'num',
                StandardScaler(),
                numeric_columns,
            ),
        ],
        remainder='drop',
    )

    pipe = Pipeline(steps=[
        ("preprocessor", preprocessor), 
        ("logistic", reg)
    ])

    pipe.fit(train[predictors], train[target_column])

    y_pred = pipe.predict(test[predictors])

    print(f"Accuracy:  {accuracy_score(test[target_column], y_pred):.4f}")
    print(f"Precision: {precision_score(test[target_column], y_pred, pos_label='yes'):.4f}")
    print(f"Recall:    {recall_score(test[target_column], y_pred, pos_label='yes'):.4f}")
    print(f"F1 Score:  {f1_score(test[target_column], y_pred, pos_label='yes'):.4f}")

    reg = SVC(
        kernel='linear',
        C=cfg['experiment']['C'],
    )

    pipe = Pipeline(steps=[
        ("preprocessor", preprocessor), 
        ("logistic", reg)
    ])

    pipe.fit(train[predictors], train[target_column])

    y_pred = pipe.predict(test[predictors])

    print(f"Accuracy:  {accuracy_score(test[target_column], y_pred):.4f}")
    print(f"Precision: {precision_score(test[target_column], y_pred, pos_label='yes'):.4f}")
    print(f"Recall:    {recall_score(test[target_column], y_pred, pos_label='yes'):.4f}")
    print(f"F1 Score:  {f1_score(test[target_column], y_pred, pos_label='yes'):.4f}")

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()