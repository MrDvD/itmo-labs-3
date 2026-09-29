from typing import Any, Dict
import matplotlib.pyplot as plt
import math
import json
import urllib.request

class ReportFiller:
    @staticmethod
    def get_resistance_values(context: Dict[str, Any], url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        resistance_values = data.get("R", [])
        
        new_context = context.copy()
        new_context["resistance"] = resistance_values
        new_context["ep"] = data.get("E", 0.0)
        return new_context

    @staticmethod
    def measure_ltspice_characteristics(context: Dict[str, Any], url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        measured = {
            "U": data["v_out"]["value"],
            "I": data["i_load"]["value"],
            "P": data["p_load"]["value"],
        }
        
        new_context = context.copy()
        new_context["measured"] = measured
        return new_context

    @staticmethod
    def calculate_ltspice_characteristics(context: Dict[str, Any]) -> Dict[str, Any]:
        measured = context.get("measured", {})
        U = measured.get("U", [])
        I = measured.get("I", [])
        N = len(I)
        calculated: Dict[str, Any] = {
            "r": [None] + [-(U[i + 1] - U[i]) / (I[i + 1] - I[i]) for i in range(1, N - 1)] + [None],
        }
        rp = math.sqrt(sum(x ** 2 for x in calculated["r"] if x is not None) / sum(1 for x in calculated["r"] if x is not None))

        ep = context["ep"]
        calculated["I"] = [ep / (x+rp) for x in context["resistance"]]
        calculated["U"] = [ep - rp * x for x in calculated["I"]]
        calculated["P"] = [u * i for u, i in zip(calculated["U"], calculated["I"])]
        calculated["eta"] = [1 - rp / (rp + x) for x in context["resistance"]]

        new_context = context.copy()
        new_context["rp"] = rp
        new_context["jp"] = ep / rp if rp != 0 else None
        new_context["calculated"] = calculated
        return new_context

    @staticmethod
    def fill_characteristics_table(context: Dict[str, Any]) -> Dict[str, Any]:
        calculated = context.get("calculated", {})
        measured = context.get("measured", {})

        table_data = []
        num_rows = len(calculated.get("I", []))

        for k in range(num_rows):
            row = {
                "k": k,
                "Rn": context.get("resistance", [])[k],
                "In": measured.get("I", [])[k] * 1000,
                "Un": measured.get("U", [])[k],
                "Pn": measured.get("P", [])[k] * 1000,
                "r": calculated.get("r", [])[k],
                "In_p": calculated.get("I", [])[k] * 1000,
                "Un_p": calculated.get("U", [])[k],
                "Pn_p": calculated.get("P", [])[k] * 1000,
                "eta": calculated.get("eta", [])[k],
            }
            table_data.append(row)

        new_context = context.copy()
        new_context["table_data"] = table_data
        return new_context

    @staticmethod
    def plot_ltspice_characteristics(context: Dict[str, Any], path_1: str, path_2: str) -> None:
        calculated = context.get("calculated", {})
        measured = context.get("measured", {})

        i_calc = calculated.get("I", [])
        i_meas = measured.get("I", [])

        # --- Plot 1: Voltage U ---
        plt.figure(figsize=(8, 5))
        if i_calc and "U" in calculated:
            plt.plot(i_calc, calculated["U"], 'b-o', label='U Calculated', linewidth=1.5)
        if i_meas and "U" in measured:
            plt.plot(i_meas, measured["U"], 'r--s', label='U LTspice', linewidth=1.5)

        plt.xlabel("Current I (A)", fontsize=10)
        plt.ylabel("Voltage U (V)", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig(path_1, dpi=300)
        plt.close()

        # --- Plot 2: Combined Power P & Efficiency η ---
        fig, ax1 = plt.subplots(figsize=(8, 5))

        # Color Palette: Blue for Calculated, Red for LTspice
        color_calc = 'tab:blue'
        color_meas = 'tab:red'

        # Primary Y-axis: Power P
        ax1.set_xlabel("Current I (A)", fontsize=10)
        ax1.set_ylabel("Power P (W)", fontsize=10)

        lines = []

        if i_calc and "P" in calculated:
            l1 = ax1.plot(i_calc, calculated["P"], color=color_calc, linestyle='-', marker='o', label='P Calculated', linewidth=1.5)
            lines.extend(l1)
        if i_meas and "P" in measured:
            l2 = ax1.plot(i_meas, measured["P"], color=color_meas, linestyle='-', marker='s', label='P LTspice', linewidth=1.5)
            lines.extend(l2)

        # Secondary Y-axis: Efficiency η
        ax2 = ax1.twinx()
        ax2.set_ylabel("Efficiency \u03b7 (%)", fontsize=10)

        if i_calc and "eta" in calculated:
            l3 = ax2.plot(i_calc, calculated["eta"], color=color_calc, linestyle='--', marker='o', label='\u03b7 Calculated', linewidth=1.5)
            lines.extend(l3)
        if i_meas and "eta" in measured:
            l4 = ax2.plot(i_meas, measured["eta"], color=color_meas, linestyle='--', marker='s', label='\u03b7 LTspice', linewidth=1.5)
            lines.extend(l4)

        # Consolidated Legend
        labels = [line.get_label() for line in lines]
        if lines:
            ax1.legend(lines, labels, loc='best')

        ax1.grid(True, linestyle='--', alpha=0.6)
        fig.tight_layout()
        plt.savefig(path_2, dpi=300)
        plt.close()