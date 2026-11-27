import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')
    
    context: Dict[str, Any] = {}

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()