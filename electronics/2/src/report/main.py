import os
import common.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)

    context: Dict[str, Any] = {
        'variant_number': cfg['variant_num'],
    }

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()