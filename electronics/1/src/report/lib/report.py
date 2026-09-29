from typing import Any, Dict
import matplotlib.pyplot as plt
import math

class ReportFiller:
    @staticmethod
    def get_resistance_values(context: Dict[str, Any]) -> Dict[str, Any]:
        resistance_values = [10, 20, 30, 40, 50, 60]
        new_context = context.copy()
        new_context["resistance"] = resistance_values
        return new_context

    @staticmethod
    def measure_ltspice_characteristics(context: Dict[str, Any]) -> Dict[str, Any]:
        measured = {
            "I": [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "U": [0, 1, 2, 3, 4, 5],
            "P": [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "nu": [0, 20, 40, 60, 80, 100]
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
            "r": [None] + [(U[i + 1] - U[i]) / (I[i + 1] - I[i]) for i in range(1, N - 1)] + [None],
        }
        rp = math.sqrt(sum(x ** 2 for x in calculated["r"] if x is not None) / sum(1 for x in calculated["r"] if x is not None))
        ep = U[0]

        calculated["I"] = [ep / (x+rp) for x in context["resistance"]]
        calculated["U"] = [ep - rp * x for x in calculated["I"]]
        calculated["P"] = [u * i for u, i in zip(calculated["U"], calculated["I"])]
        calculated["eta"] = [1 - rp / (rp + x) for x in context["resistance"]]

        new_context = context.copy()
        new_context["rp"] = rp
        new_context["ep"] = ep
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
                # "Rn": measured.get("R", [])[k],
                "Rn": 0,
                "In": measured.get("I", [])[k],
                "Un": measured.get("U", [])[k],
                "Pn": measured.get("P", [])[k],
                "r": calculated.get("r", [])[k],
                "In_p": calculated.get("I", [])[k],
                "Un_p": calculated.get("U", [])[k],
                "Pn_p": calculated.get("P", [])[k],
                # "eta": calculated.get("eta", [])[k],
                "eta": 0,
            }
            table_data.append(row)

        new_context = context.copy()
        new_context["table_data"] = table_data
        return new_context

    @staticmethod
    def plot_ltspice_characteristics(context: Dict[str, Any], path_1: str, path_2: str, path_3: str) -> None:
        calculated = context.get("calculated", {})
        measured = context.get("measured", {})



        plots_config = [
            {
                "path": path_1,
                "ylabel": "Voltage U (V)",
                "calc_key": "U",
                "meas_key": "U"
            },
            {
                "path": path_2,
                "ylabel": "Power P (W)",
                "calc_key": "P",
                "meas_key": "P"
            },
            {
                "path": path_3,
                "ylabel": "Efficiency \u03b7 (%)",
                "calc_key": "nu",
                "meas_key": "nu"
            }
        ]

        # Extract current data
        i_calc = calculated.get("I", [])
        i_meas = measured.get("I", [])

        for cfg in plots_config:
            plt.figure(figsize=(8, 5))

            # Plot calculated values if present
            if i_calc and cfg["calc_key"] in calculated:
                plt.plot(i_calc, calculated[cfg["calc_key"]], 'b-o', label='Calculated', linewidth=1.5)

            # Plot measured/simulated values if present
            if i_meas and cfg["meas_key"] in measured:
                plt.plot(i_meas, measured[cfg["meas_key"]], 'r--s', label='LTspice', linewidth=1.5)

            plt.xlabel("Current I (A)", fontsize=10)
            plt.ylabel(cfg["ylabel"], fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(loc='best')
            plt.tight_layout()

            # Save and clean up memory
            plt.savefig(cfg["path"], dpi=300)
            plt.close()