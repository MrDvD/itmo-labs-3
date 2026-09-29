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
    ui_diagram_path = os.path.join(pics_path, 'ui_diagram.pdf')
    pi_diagram_path = os.path.join(pics_path, 'pi_diagram.pdf')
    nui_diagram_path = os.path.join(pics_path, 'nui_diagram.pdf')

    context: Dict[str, Any] = {
        'variant_number': cfg['variant_num'],
        'ltspice_circuit_path': ltspice_circuit_path,
        'ui_diagram_path': ui_diagram_path,
        'pi_diagram_path': pi_diagram_path,
        'nui_diagram_path': nui_diagram_path,
    }

    context = ReportFiller.get_resistance_values(context)
    context = ReportFiller.measure_ltspice_characteristics(context)
    context = ReportFiller.calculate_ltspice_characteristics(context)
    context = ReportFiller.fill_characteristics_table(context)

    ReportFiller.plot_ltspice_characteristics(context, ui_diagram_path, pi_diagram_path, nui_diagram_path)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()