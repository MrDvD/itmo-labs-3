import math
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class ReportFiller:
    @staticmethod
    def compute_main_characteristics(context: Dict[str, Any], sequence: List[float]) -> Dict[str, Any]:
        sample_sizes = [10, 20, 50, 100, 200]
        
        # Standard normal quantiles from Table 1 in the assignment
        z_quantiles = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }
        
        # 1. Baseline metrics (full sequence)
        N_full = len(sequence)
        if N_full == 0:
            raise ValueError("Sequence cannot be empty.")

        mu_full = sum(sequence) / N_full
        
        # Unbiased variance for full sequence
        var_full = sum((x - mu_full) ** 2 for x in sequence) / (N_full - 1) if N_full > 1 else 0.0
        std_full = math.sqrt(var_full)
        cv_full = (std_full / mu_full * 100.0) if mu_full != 0 else 0.0

        d_mu_full = {
            alpha: z * (std_full / math.sqrt(N_full)) 
            for alpha, z in z_quantiles.items()
        }

        # Dict structure to match Jinja template key paths
        metrics: Dict[str, Dict[str, str]] = {
            "mu": {"total": f"{mu_full:.4f}"},
            "d_mu_90": {"total": f"{d_mu_full[0.90]:.4f}"},
            "d_mu_95": {"total": f"{d_mu_full[0.95]:.4f}"},
            "d_mu_99": {"total": f"{d_mu_full[0.99]:.4f}"},
            "var": {"total": f"{var_full:.4f}"},
            "std": {"total": f"{std_full:.4f}"},
            "cv": {"total": f"{cv_full:.2f}"}
        }

        # 2. Subsample calculations (10, 20, 50, 100, 200)
        for N in sample_sizes:
            subsequence = sequence[:N]
            n_curr = len(subsequence)

            if n_curr == 0:
                continue

            # Mean
            mu_n = sum(subsequence) / n_curr
            
            # Variance logic per assignment (S_0^2 for N < 100, S^2 for N >= 100)
            if n_curr < 100:
                var_n = sum((x - mu_n) ** 2 for x in subsequence) / (n_curr - 1) if n_curr > 1 else 0.0
            else:
                var_n = sum((x - mu_n) ** 2 for x in subsequence) / n_curr

            std_n = math.sqrt(var_n)
            cv_n = (std_n / mu_n * 100.0) if mu_n != 0 else 0.0

            # Confidence margin d_mu = c * (sigma / sqrt(n))
            d_mu_n = {
                alpha: z * (std_n / math.sqrt(n_curr))
                for alpha, z in z_quantiles.items()
            }

            # --- Absolute values ("1") ---
            metrics["mu"][f"abs_{N}"] = f"{mu_n:.4f}"
            metrics["var"][f"abs_{N}"] = f"{var_n:.4f}"
            metrics["std"][f"abs_{N}"] = f"{std_n:.4f}"
            metrics["cv"][f"abs_{N}"] = f"{cv_n:.2f}"

            metrics["d_mu_90"][f"abs_{N}"] = f"{d_mu_n[0.90]:.4f}"
            metrics["d_mu_95"][f"abs_{N}"] = f"{d_mu_n[0.95]:.4f}"
            metrics["d_mu_99"][f"abs_{N}"] = f"{d_mu_n[0.99]:.4f}"

            # --- Relative errors ("%") compared to full-sequence baseline ---
            rel_mu = abs((mu_n - mu_full) / mu_full) * 100.0 if mu_full != 0 else 0.0
            rel_var = abs((var_n - var_full) / var_full) * 100.0 if var_full != 0 else 0.0
            rel_std = abs((std_n - std_full) / std_full) * 100.0 if std_full != 0 else 0.0
            rel_cv = abs((cv_n - cv_full) / cv_full) * 100.0 if cv_full != 0 else 0.0

            metrics["mu"][f"rel_{N}"] = f"{rel_mu:.2f}"
            metrics["var"][f"rel_{N}"] = f"{rel_var:.2f}"
            metrics["std"][f"rel_{N}"] = f"{rel_std:.2f}"
            metrics["cv"][f"rel_{N}"] = f"{rel_cv:.2f}"

            rel_d90 = abs((d_mu_n[0.90] - d_mu_full[0.90]) / d_mu_full[0.90]) * 100.0 if d_mu_full[0.90] != 0 else 0.0
            rel_d95 = abs((d_mu_n[0.95] - d_mu_full[0.95]) / d_mu_full[0.95]) * 100.0 if d_mu_full[0.95] != 0 else 0.0
            rel_d99 = abs((d_mu_n[0.99] - d_mu_full[0.99]) / d_mu_full[0.99]) * 100.0 if d_mu_full[0.99] != 0 else 0.0

            metrics["d_mu_90"][f"rel_{N}"] = f"{rel_d90:.2f}"
            metrics["d_mu_95"][f"rel_{N}"] = f"{rel_d95:.2f}"
            metrics["d_mu_99"][f"rel_{N}"] = f"{rel_d99:.2f}"

        # Update context dictionary and return
        context.update(metrics)
        return context

    @staticmethod
    def compute_autocorrelation(
        context: Dict[str, Any], sequence: List[float], max_lag: int = 10
    ) -> Dict[str, Any]:
        N = len(sequence)
        if N == 0:
            raise ValueError("Sequence cannot be empty.")

        mu = sum(sequence) / N
        var = sum((x - mu) ** 2 for x in sequence) / N

        autocorr_data: Dict[str, str] = {}

        for k in range(1, max_lag + 1):
            if k >= N or var == 0.0:
                r_k = 0.0
            else:
                gamma_k = sum((sequence[i] - mu) * (sequence[i + k] - mu) for i in range(N - k)) / N
                r_k = gamma_k / var
            autocorr_data[f"abs_{k}"] = f"{r_k:.4f}"
            rel_k = abs(r_k) * 100.0
            autocorr_data[f"rel_{k}"] = f"{rel_k:.2f}\\%"

        context["autocorr"] = autocorr_data
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
    def plot_sequence_histogram(sequence: List[float], output_path: str, bins: int = 10):
        plt.figure(figsize=(10, 6))
        plt.hist(sequence, bins=bins, color='lightgreen', edgecolor='black')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.grid(axis='y')
        plt.savefig(output_path)
        plt.close()