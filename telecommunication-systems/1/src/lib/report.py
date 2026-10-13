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
    def plot_m2(binary_message: str, plot_path: str):
        import matplotlib.pyplot as plt
        import numpy as np

        binary_list = [int(bit) for bit in binary_message.replace(' ', '')]

        data = np.array(binary_list).reshape(-1, 8)

        plt.imshow(data, cmap='gray', aspect='auto')
        plt.axis('off')
        plt.savefig(plot_path, bbox_inches='tight', pad_inches=0)
        plt.close()