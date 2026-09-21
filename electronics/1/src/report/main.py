import os
import common.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)

    ltspice_circuit_path = os.path.join(pics_path, 'ltspice_circuit.svg')
    
    context: Dict[str, Any] = {
        'variant_number': cfg['variant_num'],
        'ltspice_circuit_path': ltspice_circuit_path,
    }

    ReportFiller.render_ltspice_circuit(ltspice_circuit_path)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()