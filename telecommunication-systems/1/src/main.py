import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict
from lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    os.makedirs(pics_path, exist_ok=True)

    m2_plot_path = os.path.join(pics_path, 'm2_plot.pdf')
    
    context: Dict[str, Any] = {
        'm2_plot_path': os.path.relpath(m2_plot_path, 'report/'),
    }

    encoding_table = {
        "А": "C0", "Р": "D0", "а": "E0", "р": "F0", " ": "20",
        "Б": "C1", "С": "D1", "б": "E1", "с": "F1", ",": "2C",
        "В": "C2", "Т": "D2", "в": "E2", "т": "F2", ".": "2E",
        "Г": "C3", "У": "D3", "г": "E3", "у": "F3", "0": "30",
        "Д": "C4", "Ф": "D4", "д": "E4", "ф": "F4", "1": "31",
        "Е": "C5", "Х": "D5", "е": "E5", "х": "F5", "2": "32",
        "Ж": "C6", "Ц": "D6", "ж": "E6", "ц": "F6", "3": "33",
        "З": "C7", "Ч": "D7", "з": "E7", "ч": "F7", "4": "34",
        "И": "C8", "Ш": "D8", "и": "E8", "ш": "F8", "5": "35",
        "Й": "C9", "Щ": "D9", "й": "E9", "щ": "F9", "6": "36",
        "К": "CA", "Ъ": "DA", "к": "EA", "ъ": "FA", "7": "37",
        "Л": "CB", "Ы": "DB", "л": "EB", "ы": "FB", "8": "38",
        "М": "CC", "Ь": "DC", "м": "EC", "ь": "FC", "9": "39",
        "Н": "CD", "Э": "DD", "н": "ED", "э": "FD",
        "О": "CE", "Ю": "DE", "о": "EE", "ю": "FE",
        "П": "CF", "Я": "DF", "п": "EF", "я": "FF",
    }

    context = ReportFiller.encode_message(context, cfg['initial_message'], encoding_table, 'encoding_message')

    ReportFiller.plot_m2(context['encoding_message']['binary'], m2_plot_path)

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()