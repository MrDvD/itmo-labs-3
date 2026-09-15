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

    sequence_plot_path = os.path.join(pics_path, 'sequence_plot.pdf')
    autocorr_plot_path = os.path.join(pics_path, 'autocorr_plot.pdf')
    sequence_hist_plot_path = os.path.join(pics_path, 'sequence_hist.pdf')
    erlang_plot_path = os.path.join(pics_path, 'erlang_plot.pdf')

    generated_sequence_plot_path = os.path.join(pics_path, 'generated_sequence_plot.pdf')
    generated_autocorr_plot_path = os.path.join(pics_path, 'generated_autocorr_plot.pdf')
    generated_sequence_hist_plot_path = os.path.join(pics_path, 'generated_sequence_hist_plot.pdf')
    
    context: Dict[str, Any] = {
        'variant_number': cfg['variant_num'],
        'sequence_plot_path': sequence_plot_path,
        'autocorr_plot_path': autocorr_plot_path,
        'sequence_hist_plot_path': sequence_hist_plot_path,
        'erlang_plot_path': erlang_plot_path,
        'generated_sequence_plot_path': generated_sequence_plot_path,
        'generated_autocorr_plot_path': generated_autocorr_plot_path,
        'generated_sequence_hist_plot_path': generated_sequence_hist_plot_path,
    }

    sequence = list()
    with open(os.path.join("src", "sequence.txt")) as f:
        for line in f:
            raw_number = line.replace(",", ".").strip()
            sequence.append(float(raw_number))

    np.random.seed(cfg['random_seed'])

    context = ReportFiller.compute_main_characteristics(context, sequence, key="main_chars")
    context = ReportFiller.compute_autocorrelation(context, sequence, key="autocorr", max_lag=10)
    context = ReportFiller.compute_histogram_distribution(context, sequence, key="main_hist", bins=10)
    context = ReportFiller.compute_hyperparameters(context, sequence)
    erlang_sequence = ReportFiller.compute_erlang_sequence(context, N=300, big_number=1000.0)

    context = ReportFiller.compute_main_characteristics(context, erlang_sequence, key="generated_chars", reference_values=context["main_chars"])
    context = ReportFiller.compute_autocorrelation(context, erlang_sequence, key="generated_autocorr", max_lag=10)
    context = ReportFiller.compute_histogram_distribution(context, erlang_sequence, key="generated_hist", bins=10)
    context = ReportFiller.compute_hyperparameters(context, erlang_sequence)

    context = ReportFiller.compute_correlation(context, sequence, erlang_sequence)

    ReportFiller.plot_sequence(sequence, sequence_plot_path)
    ReportFiller.plot_autocorrelation(context["autocorr"], autocorr_plot_path)
    ReportFiller.plot_sequence_histogram(sequence, sequence_hist_plot_path, tau=context['main_hist']['hist_nodes'])
    ReportFiller.plot_sequence_with_erlang_density(context, sequence, erlang_plot_path, tau=context['main_hist']['hist_nodes'])

    ReportFiller.plot_sequence(erlang_sequence, generated_sequence_plot_path)
    ReportFiller.plot_sequence_histogram(erlang_sequence, generated_sequence_hist_plot_path, tau=context['generated_hist']['hist_nodes'])
    ReportFiller.plot_autocorrelation(context["generated_autocorr"], generated_autocorr_plot_path)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()