import os

from sklearn.preprocessing import MinMaxScaler, StandardScaler
import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict
import pandas as pd

from lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)

    student_mat = pd.read_csv('/lab/student-mat.csv', sep=';')
    student_por = pd.read_csv('/lab/student-por.csv', sep=';')

    df = pd.concat([student_mat, student_por], ignore_index=True)
    features = ['age', 'Medu', 'Fedu', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'failures']
    X = df[features].values
    y_true = list(df['studytime'].values)
    
    context: Dict[str, Any] = {
        'random_state': cfg['random_state'],
        'k': cfg['k'],
        'n_components': cfg['dbscan']['n_components'],
    }

    X_norm = pd.DataFrame(
        StandardScaler().fit_transform(X),
        columns=features
    )

    X_norm_2 = pd.DataFrame(
        MinMaxScaler().fit_transform(X),
        columns=features
    )

    INF = int(1e6)
    context = ReportFiller.use_own_kmeans(
        context,
        X_norm,
        y_true,
        INF,
        cfg['k'],
        cfg['random_state'],
        'custom_kmeans'
    )
    context = ReportFiller.use_sklearn_kmeans(
        context,
        X_norm,
        y_true,
        cfg['k'],
        cfg['random_state'],
        'sklearn_kmeans'
    )
    context = ReportFiller.use_hierarchical_clustering(
        context,
        X_norm,
        y_true,
        cfg['k'],
        'hierarchical_clustering'
    )
    context = ReportFiller.use_dbscan(
        context,
        X_norm,
        y_true,
        cfg['dbscan']['eps'],
        cfg['dbscan']['min_samples'],
        'dbscan'
    )
    context = ReportFiller.use_pca(
        context,
        X_norm,
        y_true,
        cfg['dbscan']['n_components'],
        cfg['dbscan']['eps'],
        cfg['dbscan']['min_samples'],
        'pca'
    )
    context = ReportFiller.use_normalization(
        context,
        X_norm_2,
        y_true,
        cfg['k'],
        'normalization'
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()