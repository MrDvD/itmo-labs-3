import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')
    
    context: Dict[str, Any] = {
      # 'variant_number': cfg['variant_num'],
    }

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)
    population_diagram_path = os.path.join(pics_path, 'population.pdf')
    colony_diagram_path = os.path.join(pics_path, 'colony.pdf')

    report = ReportFiller(context)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()