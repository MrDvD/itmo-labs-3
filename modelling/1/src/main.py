import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from lib.report import ReportFiller
from typing import Any, Dict

if __name__ == "__main__":
    cfg = config.load('config.yml')

    pics_path = os.path.join(cfg['report']['dir'], 'pics')
    os.makedirs(pics_path, exist_ok=True)

    sequence_plot_path = os.path.join(pics_path, 'sequence_plot.pdf')
    autocorr_plot_path = os.path.join(pics_path, 'autocorr_plot.pdf')
    sequence_hist_plot_path = os.path.join(pics_path, 'sequence_hist.pdf')
    
    context: Dict[str, Any] = {
      'variant_number': cfg['variant_num'],
      'sequence_plot_path': sequence_plot_path,
      'autocorr_plot_path': autocorr_plot_path,
      'sequence_hist_plot_path': sequence_hist_plot_path,
    }

    sequence = list()
    with open(os.path.join("src", "sequence.txt")) as f:
        for line in f:
            raw_number = line.replace(",", ".").strip()
            sequence.append(float(raw_number))

    context = ReportFiller.compute_main_characteristics(context, sequence)
    context = ReportFiller.compute_autocorrelation(context, sequence)

    ReportFiller.plot_sequence(sequence, sequence_plot_path)
    ReportFiller.plot_autocorrelation(context["autocorr"], autocorr_plot_path)
    ReportFiller.plot_sequence_histogram(sequence, sequence_hist_plot_path)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()