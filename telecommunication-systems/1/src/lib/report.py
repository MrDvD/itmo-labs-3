import json
from typing import Any, Callable, Dict, List

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

    @staticmethod
    def encode_b4b5(context: Dict[str, Any], message: str, encoding_table: Dict[str, str], key: str):
        encoding_message = {
            'initial_message': message,
            'hex_list': list(),
            'binary_list': list(),
            'length': 0,
            'redundancy': 0,
        }

        message = message.replace(' ', '')
        for i in range(0, len(message), 4):
            nibble = message[i:i+4]
            if nibble in encoding_table:
                encoding_message['binary_list'] += list(encoding_table[nibble])
            else:
                raise ValueError(f"Nibble '{nibble}' not found in encoding table.")
        for i in range(0, len(encoding_message['binary_list']), 8):
            byte = ''.join(encoding_message['binary_list'][i:i+8])
            encoding_message['hex_list'].append(hex(int(byte, 2))[2:].upper().zfill(2))
        encoding_message['hex'] = ' '.join(encoding_message['hex_list'])
        binary_list = encoding_message['binary_list']
        binary_bytes = [''.join(binary_list[i:i+4]) for i in range(0, len(binary_list), 4)]
        
        encoding_message['binary'] = ' '.join(binary_bytes)
        encoding_message['redundancy'] = 100 * (len(binary_list) - len(message)) / len(message)
        encoding_message['length'] = len(binary_bytes)

        new_context = context.copy()
        new_context[key] = encoding_message
        return new_context

    @staticmethod
    def encode_scramble(context: Dict[str, Any], message: str, scrambler: Callable[[str,int],str], key: str):
        encoding_message = {
            'initial_message': message,
            'binary_list': list(),
        }
        message = message.replace(' ', '')
        for i in range(len(message)):
            encoding_message['binary_list'] += list(scrambler(message, i))
        
        binary_list = encoding_message['binary_list']
        binary_bytes = [''.join(binary_list[i:i+4]) for i in range(0, len(binary_list), 4)]
        encoding_message['binary'] = ' '.join(binary_bytes)
        encoding_message['hex'] = ' '.join(
            map(
                lambda b: hex(int(''.join(b), 2))[2:].upper(),
                [binary_bytes[i:i+2] for i in range(0, len(binary_bytes), 2)]
            )
        )
        encoding_message['length'] = len(message)

        new_context = context.copy()
        new_context[key] = encoding_message
        return new_context