from typing import Dict, Any, List
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline, clone
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

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