import json
from typing import Any, Dict, List

class ReportFiller:
    @staticmethod
    def encode_message(context: Dict[str, Any], message: str, encoding_table: Dict[str, str], key: str):
        encoding_message = {
            'initial_message': message,
            'hex_list': list(),
            'binary_list': list(),
            'length': 0,
        }
        for c in message:
            if c in encoding_table:
                encoding_message['hex_list'].append(encoding_table[c])
                encoding_message['binary_list'] += list(bin(int(encoding_table[c], 16))[2:].zfill(8))
            else:
                raise ValueError(f"Character '{c}' not found in encoding table.")
        encoding_message['hex'] = ' '.join(encoding_message['hex_list'])
        binary_list = encoding_message['binary_list']
        binary_bytes = [''.join(binary_list[i:i+4]) for i in range(0, len(binary_list), 4)]
        encoding_message['binary'] = ' '.join(binary_bytes)
        encoding_message['length'] = len(message)

        new_context = context.copy()
        new_context[key] = encoding_message
        return new_context

    @staticmethod
    def analyze_message(msg: str, patterns: List[str]) -> Dict[str, Any]:
        stats = dict()
        for pattern in patterns:
            count = 0
            while pattern in msg:
                msg = msg.replace(pattern, '')
                count += 1
            stats[pattern] = count
        return stats

    @staticmethod
    def calc_signal_params(context: Dict[str, Any], C: float, msg: str, pattern_info: Dict[str, Any], key: str):
        params = dict()
        for method, body in pattern_info.items():
            stats: Dict[str, Any] = {
                'patterns': list(),
            }
            edited_msg = msg

            min_freq = float('inf')
            max_freq = 0
            avg_freq = 0
            N = 0
            for pattern in body:
                pattern_instance_info = dict()

                calc = pattern['calc']
                name = pattern['name']
                freq = pattern['freq']['exec']

                if 'encode' in pattern:
                    encode = pattern['encode']
                    edited_msg = encode(edited_msg)

                pattern_instance_info['name'] = name
                edited_msg, n_loc = calc(edited_msg)

                N += n_loc
                pattern_instance_info['occurrences'] = n_loc

                freq_loc = freq(C)
                pattern_instance_info['freq'] = {
                    'formula': pattern['freq']['formula'],
                    'value': freq_loc,
                }
                avg_freq += freq_loc * n_loc
                min_freq = min(min_freq, freq_loc)
                max_freq = max(max_freq, freq_loc)

                stats['patterns'].append(pattern_instance_info)

            spectrum = max_freq - min_freq
            mid = min_freq + spectrum / 2
            stats['freq'] = {
                'low': min_freq,
                'high': max_freq,
                'spectrum': max_freq - min_freq,
                'avg': avg_freq / N,
                'bandwidth': 7 * max_freq - min_freq,
                'mid': mid,
                'is_high': avg_freq / N > mid,
            }
            params[method] = stats

        new_context = context.copy()
        new_context[key] = params

        return new_context