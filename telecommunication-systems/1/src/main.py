import os
import lib.config as config
from lib.artifacts import ArtifactsFiller
from typing import Any, Dict, Callable, Tuple
from lib.report import ReportFiller

if __name__ == "__main__":
    cfg = config.load('config.yml')

    report_dir = cfg['report']['dir']
    pics_path = os.path.join(report_dir, 'pics')
    
    context: Dict[str, Any] = {
        'list_number': cfg['list_number'],
        'bandwidth_list': cfg['bandwidths'],
        'bandwidth': cfg['bandwidths'][cfg['list_number'] % 2],
    }

    context['bit_interval'] = 1 / context['bandwidth'] * 1e3

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

    def pattern_calc_1(pattern: str) -> Callable[[str], Tuple[str, int]]:
        def inner(msg: str) -> Tuple[str, int]:
            nonlocal pattern
            return msg.replace(pattern, ' '), msg.count(pattern)
        return inner

    def encode_msg(msg: str) -> str:
        is_up = True
        encoded_msg = ''
        for c in msg:
            if c == '1':
                encoded_msg += 'U' if is_up else 'D'
                is_up = not is_up
            else:
                encoded_msg += '0'
        return encoded_msg

    def decode_msg(msg: str) -> str:
        decoded_msg = ''
        for c in msg:
            if c in ['U', 'D']:
                decoded_msg += '1'
            else:
                decoded_msg += c
        return decoded_msg

    patterns_1 = [
        {
            'name': '10',
            'freq': {
                'formula': r'C\slash 2',
                'exec': lambda C: C / 2,
            },
            'calc': pattern_calc_1('10'),
        },
        {
            'name': '01',
            'freq': {
                'formula': r'C\slash 2',
                'exec': lambda C: C / 2,
            },
            'calc': pattern_calc_1('01'),
        },
        {
            'name': '1',
            'freq': {
                'formula': r'C',
                'exec': lambda C: float(C),
            },
            'calc': pattern_calc_1('1'),
        },
        {
            'name': '0',
            'freq': {
                'formula': r'C',
                'exec': lambda C: float(C),
            },
            'calc': pattern_calc_1('0'),
        }
    ]

    pattern_info = {
        'M2': patterns_1.copy(),
        'RZ': patterns_1.copy(),
        'DM': patterns_1.copy(),
        'AMI': [
            {
                'name': '0101',
                'freq': {
                    'formula': r'C\slash 4',
                    'exec': lambda C: C / 4,
                },
                'calc': pattern_calc_1('0101'),
            },
            {
                'name': '11',
                'freq': {
                    'formula': r'C\slash 2',
                    'exec': lambda C: C / 2,
                },
                'calc': pattern_calc_1('11'),
            },
            {
                'name': '0',
                'freq': {
                    'formula': r'0',
                    'exec': lambda _: float(0),
                },
                'calc': pattern_calc_1('0'),
            }
        ],
        'CMI': [
            {
                'name': '10 («ров»)',
                'freq': {
                    'formula': r'C\slash 3',
                    'exec': lambda C: C / 3,
                },
                'calc': pattern_calc_1('D0'),
                'encode': encode_msg,
            },
            {
                'name': '01 («холм»)',
                'freq': {
                    'formula': r'C\slash 3',
                    'exec': lambda C: C / 3,
                },
                'calc': pattern_calc_1('0U'),
            },
            {
                'name': '1',
                'freq': {
                    'formula': r'C\slash 2',
                    'exec': lambda C: C / 2,
                },
                'calc': pattern_calc_1('1'),
                'encode': decode_msg,
            },
            {
                'name': '0',
                'freq': {
                    'formula': r'0',
                    'exec': lambda _: 0,
                },
                'calc': pattern_calc_1('0'),
            }
        ],
    }

    context = ReportFiller.calc_signal_params(
        context,
        context['bandwidth'],
        ''.join(context['encoding_message']['binary_list']),
        pattern_info,
        'signal_params',
    )

    artifacts = ArtifactsFiller(context, [cfg['report']['dir']])
    artifacts.compile_patterns()