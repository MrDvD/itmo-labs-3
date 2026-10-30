import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    
    context: Dict[str, Any] = {
        'variant': cfg['variant'],
    }

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()