import os
import lib.config as config
import numpy as np
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)
    
    context: Dict[str, Any] = {}

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()