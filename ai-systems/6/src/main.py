import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
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
    
    context: Dict[str, Any] = {}

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()