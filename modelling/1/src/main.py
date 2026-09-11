import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')
    
    context: Dict[str, Any] = {
    #   'variant_number': cfg['variant_num'],
    }

    sequence = list()
    with open(os.path.join("src", "sequence.txt")) as f:
        raw_number = f.readline().replace(",", ".").strip()
        sequence.append(float(raw_number))

    # pics_path = os.path.join(cfg['report']['dir'], 'pics')
    # os.makedirs(pics_path, exist_ok=True)

    report = ReportFiller(context)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()