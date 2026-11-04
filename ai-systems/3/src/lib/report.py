from typing import Dict, Any, List, Tuple
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline, clone
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class ReportFiller:
    @staticmethod
    def teach_models(
        context: Dict[str, Any],
        C: float,
        categorical_columns: List[str],
        numeric_columns: List[str],
        predictors: List[str],
        target_column: str,
        train: Any,
        test: Any,
    ) -> Dict[str, Any]:
        new_context = dict()
        
        logistic_regression_metrics = dict()
        
        reg_log = LogisticRegression()
    
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    'cat',
                    OneHotEncoder(sparse_output=False),
                    categorical_columns,
                ),
                (
                    'num',
                    StandardScaler(),
                    numeric_columns,
                ),
            ],
            remainder='drop',
        )
    
        pipe_log = Pipeline(steps=[
            ("preprocessor", clone(preprocessor)), 
            ("logistic", reg_log)
        ])
    
        pipe_log.fit(train[predictors], train[target_column])
    
        y_pred_log = pipe_log.predict(test[predictors])
    
        logistic_regression_metrics['accuracy'] = accuracy_score(test[target_column], y_pred_log)
        logistic_regression_metrics['precision'] = precision_score(test[target_column], y_pred_log, pos_label='yes')
        logistic_regression_metrics['recall'] = recall_score(test[target_column], y_pred_log, pos_label='yes')
        logistic_regression_metrics['f1'] = f1_score(test[target_column], y_pred_log, pos_label='yes')
    
        new_context['logistic_regression'] = logistic_regression_metrics
    
        support_vector_machine_metrics: Dict[str, Any] = {
            'C': C,
        }
    
        reg_svc = SVC(
            kernel='linear',
            C=C,
        )
    
        pipe_svc = Pipeline(steps=[
            ("preprocessor", clone(preprocessor)), 
            ("svc", reg_svc)
        ])
    
        pipe_svc.fit(train[predictors], train[target_column])
    
        y_pred_svc = pipe_svc.predict(test[predictors])
    
        support_vector_machine_metrics['accuracy'] = accuracy_score(test[target_column], y_pred_svc)
        support_vector_machine_metrics['precision'] = precision_score(test[target_column], y_pred_svc, pos_label='yes')
        support_vector_machine_metrics['recall'] = recall_score(test[target_column], y_pred_svc, pos_label='yes')
        support_vector_machine_metrics['f1'] = f1_score(test[target_column], y_pred_svc, pos_label='yes')
    
        new_context['support_vector_machine'] = support_vector_machine_metrics

        return context | new_context

    @staticmethod
    def calc_auc_roc(
        context: Dict[str, Any],
        Y_matrix: List[List[int]],
        P_matrix: List[List[float]],
    ) -> Dict[str, Any]:
        auc_roc = {
            'Y_matrix': Y_matrix,
            'P_matrix': P_matrix,
        }
        N_classes = len(Y_matrix[0])
        N_positive = [sum(x[i] for x in Y_matrix) for i in range(N_classes)]
        auc_roc['N_positive'] = N_positive

        def calc_auc(Y: List[int], P: List[float]) -> float:
            objects = sorted(zip(P, Y), reverse=True)
            N = len(Y)

            numerator = 0
            denominator = 0

            def I_scores(a: float, b: float) -> float:
                if a < b:
                    return 1
                elif a == b:
                    return 0.5
                else:
                    return 0

            def I_classes(a: float, b: float) -> float:
                return 1 if a < b else 0

            for i in range(N):
                for j in range(N):
                    numerator += I_scores(objects[i][0], objects[j][0]) * I_classes(objects[i][1], objects[j][1])
                    denominator += I_classes(objects[i][1], objects[j][1])
            
            auc = numerator / denominator if denominator != 0 else 0
            return auc

        auc_roc['auc_values'] = [calc_auc([a[i] for a in Y_matrix], [a[i] for a in P_matrix]) for i in range(N_classes)]
        auc_roc['auc_macro'] = sum(auc_roc['auc_values']) / len(auc_roc['auc_values']) if auc_roc['auc_values'] else 0
        auc_roc['auc_weighted'] = sum([auc_roc['auc_values'][i] * N_positive[i] / sum(N_positive) for i in range(N_classes)])
        auc_roc['auc_micro'] = calc_auc([b for a in Y_matrix for b in a], [b for a in P_matrix for b in a])
        auc_roc['auc_values_object'] = [calc_auc(Y_matrix[r], P_matrix[r]) for r in range(len(Y_matrix))]
        auc_roc['auc_samples'] = sum(auc_roc['auc_values_object']) / len(Y_matrix)

        new_context = {
            'auc_roc': auc_roc,
        }

        return context | new_context

    @staticmethod
    def plot_roc(
        Y_matrix: List[List[int]],
        P_matrix: List[List[float]],
        plot_path: str,
    ) -> None:
        n_classes = len(Y_matrix[0])

        hatches = ['///', '\\\\\\', '|||', '---', '+++', 'xxx',
                'ooo', '***', '...', 'OOO']
        cmap = plt.get_cmap('tab10')
        colors = [cmap(i) for i in range(10)]

        fig, ax = plt.subplots(figsize=(8, 8))

        for i in range(n_classes):
            Y = [row[i] for row in Y_matrix]
            P = [row[i] for row in P_matrix]

            N_pos = sum(Y)
            N_neg = len(Y) - N_pos

            objects = sorted(zip(P, Y), key=lambda t: t[0], reverse=True)

            fpr, tpr = [0.0], [0.0]
            tp, fp = 0, 0
            prev_score = None
            for score, label in objects:
                if label == 1:
                    tp += 1
                else:
                    fp += 1
                if prev_score is not None and score != prev_score:
                    fpr.append(fp / N_neg if N_neg else 0.0)
                    tpr.append(tp / N_pos if N_pos else 0.0)
                prev_score = score
            fpr.append(1.0)
            tpr.append(1.0)

            color = colors[i % len(colors)]

            ax.fill_between(
                fpr, tpr,
                facecolor='none',
                edgecolor=color,
                hatch=hatches[i % len(hatches)],
                linewidth=0.0,
                alpha=0.9,
            )
            ax.plot(
                fpr, tpr,
                color=color,
                linewidth=1.6,
                label=f"Class {i}",
            )

        ax.plot([0, 1], [0, 1], 'k--', linewidth=0.8,
                label="Chance")

        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.legend(loc="lower right", frameon=True)
        ax.grid(True, alpha=0.3)

        with PdfPages(plot_path) as pdf:
            pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def calc_pr(
        context: Dict[str, Any],
        Y: List[int],
        P: List[float],
        thresholds: List[float],
        key: str,
    ) -> Dict[str, Any]:
        accuracy_lst = list()
        recall_lst = list()
        precision_lst = list()
        
        pr_metrics = {
            'binary_thresholds': thresholds,
            'accuracy': accuracy_lst,
            'recall': recall_lst,
            'precision': precision_lst,
        }
        
        for td in thresholds:
            Y_pred = [1 if p >= td else 0 for p in P]

            TP, TN, FP, FN = 0, 0, 0, 0

            for j in range(len(Y)):
                if (Y[j], Y_pred[j]) == (1, 1):
                    TP += 1
                elif (Y[j], Y_pred[j]) == (0, 0):
                    TN += 1
                elif (Y[j], Y_pred[j]) == (0, 1):
                    FP += 1
                elif (Y[j], Y_pred[j]) == (1, 0):
                    FN += 1

            precision_lst.append(TP / (TP + FP) if (TP + FP) != 0 else 0)
            recall_lst.append(TP / (FN + TP) if (FN + TP) != 0 else 0)
            accuracy_lst.append((TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) != 0 else 0)
        new_context = {
            key: pr_metrics,
        }
        return context | new_context

    @staticmethod
    def plot_pr_sketch(
        precision_recall_pairs: List[Tuple[float, float]],
        plot_path: str,
    ) -> None:
        sorted_pairs = sorted(precision_recall_pairs, key=lambda x: x[1])
        
        recalls = [p[1] for p in sorted_pairs]
        precisions = [p[0] for p in sorted_pairs]

        fig, ax = plt.subplots(figsize=(6, 6))

        ax.plot(
            recalls, 
            precisions, 
            marker='o', 
            linestyle='-', 
            color='tab:blue', 
            linewidth=1.5, 
            markersize=8,
            label="PR Sketch"
        )

        for p, r in zip(precisions, recalls):
            ax.annotate(
                f'({r:.2f}, {p:.2f})', 
                (r, p), 
                textcoords="offset points", 
                xytext=(8, 5), 
                ha='left',
                fontsize=9
            )

        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower left", frameon=True)

        with PdfPages(plot_path) as pdf:
            pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def visualize_pr_calculation(
        context: Dict[str, Any],
        Y: List[int],
        P: List[float],
        threshold: float,
        key: str,
        colors: List[str],
    ) -> Dict[str, Any]:
        PP = [1 if p >= threshold else 0 for p in P]

        TP, FP, FN = list(), list(), list()
        visualization_metrics = {
            'Y': Y,
            'P': P,
            'PP': PP,
            'TP': TP,
            'FP': FP,
            'FN': FN,
            'threshold': threshold,
            'colors': colors,
        }

        color_tp, color_fp, color_fn = colors[0], colors[1], colors[2]

        tp_char = f"\\textcolor{{{color_tp}}}{{\\blacksquare}}"
        fp_char = f"\\textcolor{{{color_fp}}}{{\\blacksquare}}"
        fn_char = f"\\textcolor{{{color_fn}}}{{\\blacksquare}}"
        no_char = "$\\square$"

        tp_count, fp_count, fn_count = 0, 0, 0
        
        for j in range(len(Y)):
            if (Y[j], PP[j]) == (1, 1):
                tp_count += 1
                TP.append(tp_char)
            else:
                TP.append(no_char)
            if (Y[j], PP[j]) == (0, 1):
                fp_count += 1
                FP.append(fp_char)
            else:
                FP.append(no_char)
            if (Y[j], PP[j]) == (1, 0):
                fn_count += 1
                FN.append(fn_char)
            else:
                FN.append(no_char)

        visualization_metrics['precision'] = f"\\dfrac{{\\textcolor{{{color_tp}}}{{{tp_count}}}}}{{\\textcolor{{{color_tp}}}{{{tp_count}}} + \\textcolor{{{color_fp}}}{{{fp_count}}}}}"
        visualization_metrics['recall'] = f"\\dfrac{{\\textcolor{{{color_tp}}}{{{tp_count}}}}}{{\\textcolor{{{color_tp}}}{{{tp_count}}} + \\textcolor{{{color_fn}}}{{{fn_count}}}}}"

        new_context = {
            key: visualization_metrics,
        }
        return context | new_context