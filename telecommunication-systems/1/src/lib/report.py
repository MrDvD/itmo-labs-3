from typing import Any, Dict

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
                binary = bin(int(encoding_table[c], 16))[2:].zfill(4)
                for i in range(2):
                    encoding_message['binary_list'].append(binary[i*4:(i+1)*4])
            else:
                raise ValueError(f"Character '{c}' not found in encoding table.")
        encoding_message['hex'] = ' '.join(encoding_message['hex_list'])
        encoding_message['binary'] = ' '.join(encoding_message['binary_list'])
        encoding_message['length'] = len(message)
        new_context = context.copy()
        new_context[key] = encoding_message
        return new_context