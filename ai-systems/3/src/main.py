import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)
    
    context: Dict[str, Any] = {}

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()