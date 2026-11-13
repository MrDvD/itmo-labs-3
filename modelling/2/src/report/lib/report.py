import json
from typing import List, Dict, Any
import urllib.request

class ReportFiller:
    @staticmethod
    def clean_absorbing_states(matrix: List[List[str]], zero_str: str = '$0$') -> List[List[str]]:
        n = len(matrix)
        if n == 0:
            return []

        absorbing = [
            i for i in range(n)
            if all(cell == zero_str for cell in matrix[i])
        ]

        if not absorbing:
            return [row[:] for row in matrix]

        absorbing_set = set(absorbing)

        cleaned = [
            [cell for j, cell in enumerate(matrix[i]) if j not in absorbing_set]
            for i in range(n)
            if i not in absorbing_set
        ]

        header = [''] + [str(i) for i in range(n) if i not in absorbing_set]
        result = [header]
        for row_idx, row in zip(
            (i for i in range(n) if i not in absorbing_set),
            cleaned,
        ):
            result.append([str(row_idx)] + row)

        return result

    @staticmethod
    def get_api_url(cfg: Dict[str, Any], endpoint_key: str) -> str:
        return f"http://{cfg['api']['host']}:{cfg['api']['port']}{cfg['api']['prefix']}{cfg['api'][endpoint_key]}"

    @staticmethod
    def get_stationary_probabilities(
        context: Dict[str, Any],
        state_names: List[List[str]],
        url: str,
        key: str
    ) -> Dict[str, Any]:
        iterations = 0
        while True:
            print(f"Iteration {iterations} of get_stationary_probabilities...")
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
            if len(data[0]) == 9 and len(data[1]) == 18:
                break
            iterations += 1

        static_probs = [
            [{"name": state_names[0][i], "value": data[0][i]} for i in range(len(data[0]))],
            [{"name": state_names[1][i], "value": data[1][i]} for i in range(len(data[1]))]
        ]

        new_context = context.copy()
        new_context[key] = static_probs
        return new_context

    @staticmethod
    def calc_characteristics_1(
        context: Dict[str, Any],
        static_probs: List[Dict[str, Any]],
        b: float,
        p1: float,
        p2: float,
        lmd: float,
        key: str,
    ) -> Dict[str, Any]:
        mu = 1 / b
        
        def get_p(state_name: str) -> float:
            for state in static_probs:
                if state['name'] == state_name:
                    return state['value']
            return 0.0

        A1 = lmd * p1 * b
        A2 = lmd * p2 * b

        l = sum([k * get_p(str(18 + k)) for k in range(1, 6)])

        m1 = get_p("12") + sum([get_p(str(18 + k)) for k in range(0, 6)])
        m2 = get_p("6") + sum([get_p(str(18 + k)) for k in range(0, 6)])
        m_sum = m1 + m2 + l

        throughput_p1 = mu * m1
        throughput_p2 = mu * m2
        throughput_sum = throughput_p1 + throughput_p2

        rho_p1 = throughput_p1 * b
        rho_p2 = throughput_p2 * b
        rho_sum = throughput_sum * b / 2

        wait_val = l / throughput_sum if throughput_sum > 0 else 0.0

        response_val = wait_val + b

        loss_val = 1 - (throughput_sum / lmd) if lmd > 0 else 0.0

        other_characteristics = {
            'load': {
                'P1': A1,
                'P2': A2,
                'sum': A1 + A2,
            },
            'utilization': {
                'P1': rho_p1,
                'P2': rho_p2,
                'sum': rho_sum,
            },
            'queue': {
                'P1': l,
                'P2': l,
                'sum': l,
            },
            'requests': {
                'P1': m1,
                'P2': m2,
                'sum': m_sum,
            },
            'wait': {
                'P1': wait_val,
                'P2': wait_val,
                'sum': wait_val,
            },
            'response': {
                'P1': response_val,
                'P2': response_val,
                'sum': response_val,
            },
            'loss': {
                'P1': loss_val,
                'P2': loss_val,
                'sum': loss_val,
            },
            'throughput': {
                'P1': throughput_p1,
                'P2': throughput_p2,
                'sum': throughput_sum,
            },
        }

        new_context = context.copy()
        new_context[key] = other_characteristics
        return new_context

    @staticmethod
    def calc_characteristics_2(
        context: Dict[str, Any],
        static_probs: List[Dict[str, Any]],
        b: float,
        p1: float,
        p2: float,
        p3: float,
        lmd: float,
        key: str,
    ) -> Dict[str, Any]:
        mu = 1 / b
        
        def get_p(state_name: str) -> float:
            for state in static_probs:
                if state['name'] == state_name:
                    return state['value']
            return 0.0

        A1 = lmd * p1 * b
        A2 = lmd * p2 * b
        A3 = lmd * p3 * b
        A_sum = A1 + A2 + A3

        l1 = 0.0
        l2 = sum([get_p(str(k)) for k in [5, 7, 13, 15, 21, 29]])
        l3 = 0.0
        l_sum = l1 + l2 + l3

        m1 = sum([get_p(str(k)) for k in [8, 10, 12, 13, 14, 15, 24, 28, 29]])
        m2 = sum([get_p(str(k)) for k in [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 28, 29]])
        m3 = sum([get_p(str(k)) for k in [2, 6, 7, 10, 14, 15, 16, 20, 21, 24, 28, 29]])
        m_sum = m1 + m2 + m3 + l_sum

        throughput_p1 = mu * m1
        throughput_p2 = mu * m2
        throughput_p3 = mu * m3
        throughput_sum = throughput_p1 + throughput_p2 + throughput_p3

        rho_p1 = throughput_p1 * b
        rho_p2 = throughput_p2 * b
        rho_p3 = throughput_p3 * b
        rho_sum = throughput_sum * b / 3

        wait_p1 = 0.0
        wait_p2 = l2 / throughput_p2 if throughput_p2 > 0 else 0.0
        wait_p3 = 0.0
        wait_sum = l_sum / throughput_sum if throughput_sum > 0 else 0.0

        response_p1 = b
        response_p2 = wait_p2 + b
        response_p3 = b
        response_sum = wait_sum + b

        loss_p1 = m1
        loss_p2 = m2
        loss_p3 = m3
        loss_sum = 1 - (throughput_sum / lmd) if lmd > 0 else 0.0

        other_characteristics = {
            'load': {
                'P1': A1,
                'P2': A2,
                'P3': A3,
                'sum': A_sum,
            },
            'utilization': {
                'P1': rho_p1,
                'P2': rho_p2,
                'P3': rho_p3,
                'sum': rho_sum,
            },
            'queue': {
                'P1': l1,
                'P2': l2,
                'P3': l3,
                'sum': l_sum,
            },
            'requests': {
                'P1': m1,
                'P2': m2,
                'P3': m3,
                'sum': m_sum,
            },
            'wait': {
                'P1': wait_p1,
                'P2': wait_p2,
                'P3': wait_p3,
                'sum': wait_sum,
            },
            'response': {
                'P1': response_p1,
                'P2': response_p2,
                'P3': response_p3,
                'sum': response_sum,
            },
            'loss': {
                'P1': loss_p1,
                'P2': loss_p2,
                'P3': loss_p3,
                'sum': loss_sum,
            },
            'throughput': {
                'P1': throughput_p1,
                'P2': throughput_p2,
                'P3': throughput_p3,
                'sum': throughput_sum,
            },
        }

        new_context = context.copy()
        new_context[key] = other_characteristics
        return new_context

    @staticmethod
    def plot_characteristics(
        other_characteristics_list: List[Dict[str, Any]],
        plot_path: str,
    ):
        import matplotlib.pyplot as plt
        import numpy as np

        characteristics = [
            'load', 'utilization', 'queue', 'requests', 
            'wait', 'response', 'loss', 'throughput'
        ]
        
        categories = ['P1', 'P2', 'P3', 'sum']
        
        _, axes = plt.subplots(2, 4, figsize=(18, 10))
        axes = axes.flatten()
        
        for idx, characteristic in enumerate(characteristics):
            ax = axes[idx]
            sys1_data = other_characteristics_list[0].get(characteristic, {})
            sys2_data = other_characteristics_list[1].get(characteristic, {})

            vals_sys1 = [sys1_data.get(cat, 0.0) for cat in categories]
            vals_sys2 = [sys2_data.get(cat, 0.0) for cat in categories]
            
            x = np.arange(len(categories))
            width = 0.35  

            ax.bar(x - width/2, vals_sys1, width, label='System 1', color='skyblue')
            ax.bar(x + width/2, vals_sys2, width, label='System 2', color='salmon')

            ax.set_title(f'{characteristic.capitalize()}', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            if idx == 0:
                ax.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()