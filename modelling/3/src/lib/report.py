import math
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import numpy as np

class ReportFiller:
    @staticmethod
    def compute_main_characteristics(
        context: Dict[str, Any],
        sequence: List[float],
        key: str,
        reference_values: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        sample_sizes = [10, 20, 50, 100, 200]
        z_quantiles = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
        
        N_full = len(sequence)
        if N_full == 0:
            raise ValueError("Sequence cannot be empty.")

        # 1. Full sequence (300-measurements) calculations
        mu_full = sum(sequence) / N_full
        var_full = sum((x - mu_full) ** 2 for x in sequence) / (N_full - 1) if N_full > 1 else 0.0
        std_full = math.sqrt(var_full)
        cv_full = std_full / mu_full * 100 if mu_full != 0 else 0.0

        d_mu_full = {
            alpha: z * (std_full / math.sqrt(N_full)) 
            for alpha, z in z_quantiles.items()
        }

        # Helper to safely extract reference values dynamically
        def get_reference_target(metric_name: str, sub_key: str, fallback_val: float) -> float:
            if not reference_values:
                return fallback_val
            
            metric_dict = reference_values.get(metric_name)
            if isinstance(metric_dict, dict):
                raw_val = metric_dict.get(sub_key) or metric_dict.get("total")
            else:
                raw_val = metric_dict

            try:
                return float(raw_val)
            except (ValueError, TypeError):
                return fallback_val

        def calc_rel_error(val: float, metric_name: str, sub_key: str, fallback_ref: float) -> str:
            ref = get_reference_target(metric_name, sub_key, fallback_ref)
            if ref == 0.0:
                return "0.00"
            return f"{(val - ref) / ref * 100.0:.2f}"

        # 2. Base metrics structure (includes new `rel_total` key)
        metrics: Dict[str, Dict[str, Dict[str, str]]] = {
            key: {
                "mu": {
                    "total": f"{mu_full:.4f}",
                    "rel_total": calc_rel_error(mu_full, "mu", "total", mu_full)
                },
                "d_mu_90": {
                    "total": f"{d_mu_full[0.90]:.4f}",
                    "rel_total": calc_rel_error(d_mu_full[0.90], "d_mu_90", "total", d_mu_full[0.90])
                },
                "d_mu_95": {
                    "total": f"{d_mu_full[0.95]:.4f}",
                    "rel_total": calc_rel_error(d_mu_full[0.95], "d_mu_95", "total", d_mu_full[0.95])
                },
                "d_mu_99": {
                    "total": f"{d_mu_full[0.99]:.4f}",
                    "rel_total": calc_rel_error(d_mu_full[0.99], "d_mu_99", "total", d_mu_full[0.99])
                },
                "var": {
                    "total": f"{var_full:.4f}",
                    "rel_total": calc_rel_error(var_full, "var", "total", var_full)
                },
                "std": {
                    "total": f"{std_full:.4f}",
                    "rel_total": calc_rel_error(std_full, "std", "total", std_full)
                },
                "cv": {
                    "total": f"{cv_full:.2f}",
                    "rel_total": calc_rel_error(cv_full, "cv", "total", cv_full)
                }
            }
        }

        # 3. Subsample calculations
        for N in sample_sizes:
            subsequence = sequence[:N]
            n_curr = len(subsequence)
            if n_curr == 0:
                continue

            sub_key = f"abs_{N}"

            mu_n = sum(subsequence) / n_curr
            var_n = (sum((x - mu_n) ** 2 for x in subsequence) / (n_curr - 1)) if n_curr < 100 else (sum((x - mu_n) ** 2 for x in subsequence) / n_curr)
            std_n = math.sqrt(var_n)
            cv_n = std_n / mu_n * 100 if mu_n != 0 else 0.0

            d_mu_n = {
                alpha: z * (std_n / math.sqrt(n_curr))
                for alpha, z in z_quantiles.items()
            }

            # Absolute values
            metrics[key]["mu"][sub_key] = f"{mu_n:.4f}"
            metrics[key]["var"][sub_key] = f"{var_n:.4f}"
            metrics[key]["std"][sub_key] = f"{std_n:.4f}"
            metrics[key]["cv"][sub_key] = f"{cv_n:.2f}"
            metrics[key]["d_mu_90"][sub_key] = f"{d_mu_n[0.90]:.4f}"
            metrics[key]["d_mu_95"][sub_key] = f"{d_mu_n[0.95]:.4f}"
            metrics[key]["d_mu_99"][sub_key] = f"{d_mu_n[0.99]:.4f}"

            # Relative errors
            metrics[key]["mu"][f"rel_{N}"] = calc_rel_error(mu_n, "mu", sub_key, mu_full)
            metrics[key]["var"][f"rel_{N}"] = calc_rel_error(var_n, "var", sub_key, var_full)
            metrics[key]["std"][f"rel_{N}"] = calc_rel_error(std_n, "std", sub_key, std_full)
            metrics[key]["cv"][f"rel_{N}"] = calc_rel_error(cv_n, "cv", sub_key, cv_full)
            
            metrics[key]["d_mu_90"][f"rel_{N}"] = calc_rel_error(d_mu_n[0.90], "d_mu_90", sub_key, d_mu_full[0.90])
            metrics[key]["d_mu_95"][f"rel_{N}"] = calc_rel_error(d_mu_n[0.95], "d_mu_95", sub_key, d_mu_full[0.95])
            metrics[key]["d_mu_99"][f"rel_{N}"] = calc_rel_error(d_mu_n[0.99], "d_mu_99", sub_key, d_mu_full[0.99])

        context.update(metrics)
        return context

    @staticmethod
    def compute_histogram_distribution(
        context: Dict[str, Any], sequence: List[float], key: str, bins: int = 10
    ) -> Dict[str, Any]:
        N = len(sequence)
        if N == 0:
            raise ValueError("Sequence cannot be empty.")

        Amin = min(sequence)
        Amax = max(sequence)
        bin_width = (Amax - Amin) / bins

        # Generate bin node boundaries
        tau = [Amin + i * bin_width for i in range(bins + 1)]
        sorted_sequence = sorted(sequence)
        counts = [0] * bins

        # Bin frequency counting
        for value in sorted_sequence:
            for i in range(bins):
                if tau[i] <= value < tau[i + 1]:
                    counts[i] += 1
                    break
            else:
                if value == tau[-1]:
                    counts[-1] += 1

        # Calculate true height density h_i = nu_i / (n * l_i)
        hist_bins = [
            {
                "left": tau[i],
                "right": tau[i + 1],
                "freq": counts[i],
                "height": counts[i] / (N * bin_width),
            }
            for i in range(bins)
        ]

        context[key] = {
            "hist_bins": hist_bins,
            "hist_nodes": tau,
        }
        return context

    @staticmethod
    def compute_autocorrelation(
        context: Dict[str, Any], sequence: List[float], key: str, max_lag: int = 10
    ) -> Dict[str, Any]:
        N = len(sequence)
        if N <= 1:
            raise ValueError("Sequence length must be greater than 1.")

        autocorr_data: Dict[str, str] = {}

        for k in range(1, max_lag + 1):
            n_k = N - k  # Number of valid overlapping pairs for lag k
            
            if n_k <= 1:
                r_k = 0.0
            else:
                # Sub-sequences for lag k
                seq_a = sequence[:n_k]      # A = (x_1, x_2, ..., x_{N-k})
                seq_b = sequence[k:]        # A_k = (x_{1+k}, x_{2+k}, ..., x_N)

                # Local means for the valid length (N - k)
                mu_a = sum(seq_a) / n_k
                mu_b = sum(seq_b) / n_k

                # Local variances for the valid length (N - k)
                var_a = sum((x - mu_a) ** 2 for x in seq_a) / n_k
                var_b = sum((x - mu_b) ** 2 for x in seq_b) / n_k

                if var_a == 0.0 or var_b == 0.0:
                    r_k = 0.0
                else:
                    # Covariance and correlation coefficient over (N - k) items
                    cov_k = sum((seq_a[i] - mu_a) * (seq_b[i] - mu_b) for i in range(n_k)) / n_k
                    r_k = cov_k / math.sqrt(var_a * var_b)

            autocorr_data[f"abs_{k}"] = f"{r_k:.4f}"
            rel_k = abs(r_k) * 100.0
            autocorr_data[f"rel_{k}"] = f"{rel_k:.2f}\\%"

        context[key] = autocorr_data
        return context

    @staticmethod
    def compute_hyperparameters(
        context: Dict[str, Any], sequence: List[float]
    ) -> Dict[str, Any]:
        N = len(sequence)
        if N == 0:
            raise ValueError("Sequence cannot be empty.")

        mu = sum(sequence) / N
        var = sum((x - mu) ** 2 for x in sequence) / (N - 1)
        std = math.sqrt(var)

        if mu == 0:
            raise ValueError("Mean (mu) cannot be zero for CV calculation.")

        # Квадрат коэффициента вариации V^2 = (sigma / mu)^2
        v_sq = (std / mu) ** 2

        # Проверка условия применения распределения Эрланга (V^2 < 1)
        if v_sq >= 1.0:
            raise ValueError(
                f"Coefficient of variation squared (V^2 = {v_sq:.4f}) must be < 1 for Erlang (E_k) approximation."
            )

        # 1. Порядок распределения k (округление 1 / V^2)
        k = round(1.0 / v_sq)
        if k < 1:
            k = 1

        # 2. Интенсивность lambda = k / mu
        lambda_val = k / mu

        context["hyperparameters"] = {
            "k": str(k),
            "lambda": f"{lambda_val:.4f}",
        }
        return context

    @staticmethod
    def compute_erlang_sequence(context: Dict[str, Any], N: int = 300, big_number: float = 1000.0) -> List[float]:
        k = int(context["hyperparameters"]["k"])
        lambda_val = float(context["hyperparameters"]["lambda"])

        if k < 1 or lambda_val <= 0:
            raise ValueError("Invalid hyperparameters for Erlang distribution.")

        def erlang(x: float) -> float:
            if x < 0:
                return 0.0
            return (lambda_val**k) * (x ** (k - 1)) * np.exp(-lambda_val * x) / math.factorial(k - 1)

        erlang_sequence: List[float] = list()
        while len(erlang_sequence) < N:
            x, y = np.random.uniform(0, big_number), np.random.uniform(0, 1)
            if y < erlang(x):
                erlang_sequence.append(x)

        return erlang_sequence

    @staticmethod
    def compute_correlation(context: Dict[str, Any], sequence_1: List[float], sequence_2: List[float]) -> Dict[str, Any]:
        N = min(len(sequence_1), len(sequence_2))
        if N == 0:
            raise ValueError("Sequences cannot be empty.")

        mu_1 = sum(sequence_1[:N]) / N
        mu_2 = sum(sequence_2[:N]) / N
        var_1 = sum((x - mu_1) ** 2 for x in sequence_1[:N]) / (N - 1)
        var_2 = sum((x - mu_2) ** 2 for x in sequence_2[:N]) / (N - 1)

        covariance = sum((sequence_1[i] - mu_1) * (sequence_2[i] - mu_2) for i in range(N)) / (N - 1)

        correlation = covariance / math.sqrt(var_1 * var_2)

        context['correlation'] = round(correlation, 4)
        return context

    @staticmethod
    def plot_sequence(sequence: List[float], output_path: str):
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(sequence) + 1), sequence, marker='o', linestyle='-', color='b')
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_autocorrelation(autocorr_data: Dict[str, str], output_path: str):
        lags = [int(key.split('_')[1]) for key in autocorr_data.keys() if key.startswith('abs_')]
        values = [float(autocorr_data[f"abs_{lag}"]) for lag in lags]

        plt.figure(figsize=(10, 6))
        plt.bar(lags, values, color='skyblue')
        plt.xlabel('Lag')
        plt.ylabel('Autocorrelation')
        plt.xticks(lags)
        plt.grid(axis='y')
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_sequence_histogram(sequence: List[float], output_path: str, tau: List[float]):
        plt.figure(figsize=(10, 6))
        plt.hist(sequence, bins=tau, density=True, color='lightgreen', edgecolor='black')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.grid(axis='y')
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_sequence_with_erlang_density(
        context: Dict[str, Any],
        sequence: List[float],
        output_path: str,
        tau: List[float],
    ):
        # Извлечение параметров k и lambda из контекста
        k = int(context["hyperparameters"]["k"])
        lambda_val = float(context["hyperparameters"]["lambda"])

        plt.figure(figsize=(10, 6))

        # Нормированная гистограмма выборки
        plt.hist(
            sequence,
            bins=tau,
            density=True,
            color="lightgreen",
            edgecolor="black",
            alpha=0.6,
            label="Histogram",
        )

        # Расчет теоретической плотности Эрланга E_k(x)
        x_min, x_max = max(0.0, min(sequence)), max(sequence)
        x_grid = np.linspace(x_min, x_max, 500)

        pdf_erlang = (
            (lambda_val**k)
            * (x_grid ** (k - 1))
            * np.exp(-lambda_val * x_grid)
        ) / math.factorial(k - 1)

        plt.plot(
            x_grid,
            pdf_erlang,
            color="darkgreen",
            linewidth=2.5,
            label=f"f(x)",
        )

        plt.xlabel("Value")
        plt.ylabel("Density")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()