import numpy as np
from typing import Dict, Any, List
from pandas import DataFrame
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics.cluster import normalized_mutual_info_score

class CustomKMeans:
    def __init__(
        self,
        n_clusters: int,
        max_iter: int,
        random_state: int,
    ):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.centroids = None
        self.labels_ = None

    def get_labels(self) -> List[int]:
        if self.labels_ is None:
            raise RuntimeError("CustomKMeans must be fitted before labels are requested")
        return list(self.labels_)

    def fit(self, X):
        X = np.array(X)
        np.random.seed(self.random_state)
        idx = np.random.choice(X.shape[0], self.n_clusters, replace=False)
        self.centroids = X[idx]

        for _ in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
            self.labels_ = np.argmin(distances, axis=1)

            new_centroids = np.array([
                X[self.labels_ == k].mean(axis=0) if np.sum(self.labels_ == k) > 0 else self.centroids[k]
                for k in range(self.n_clusters)
            ])

            if np.all(self.centroids == new_centroids):
                break
            self.centroids = new_centroids
        return self


class ReportFiller:
    @staticmethod
    def use_own_kmeans(
        context: Dict[str, Any],
        X_scaled: DataFrame,
        Y: List[float],
        max_iter: int,
        k: int,
        random_state: int,
        key: str,
    ) -> Dict[str, Any]:
        custom_kmeans = dict()

        kmeans = CustomKMeans(
            n_clusters=k,
            max_iter=max_iter,
            random_state=random_state
        )
        kmeans.fit(X_scaled)
        labels = kmeans.get_labels()

        unique_labels = set(labels)
        n_clusters = len(unique_labels)

        db = davies_bouldin_score(X_scaled, labels)
        nmi = normalized_mutual_info_score(Y, labels)

        custom_kmeans['labels'] = labels
        custom_kmeans['davies_bouldin_index'] = db
        custom_kmeans['normalized_mutual_info'] = nmi
        custom_kmeans['n_clusters'] = n_clusters
        custom_kmeans['name'] = "custom k-means"

        new_context = context.copy()
        new_context[key] = custom_kmeans

        return new_context

    @staticmethod
    def use_sklearn_kmeans(
        context: Dict[str, Any],
        X_scaled: DataFrame,
        Y: List[float],
        k: int,
        random_state: int,
        key: str,
    ) -> Dict[str, Any]:
        sklearn_kmeans = dict()
        
        kmeans = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=10
        )
        labels = kmeans.fit_predict(X_scaled)

        unique_labels = set(labels)
        n_clusters = len(unique_labels)
        
        db = davies_bouldin_score(X_scaled, labels)
        nmi = normalized_mutual_info_score(Y, labels)

        sklearn_kmeans['labels'] = labels
        sklearn_kmeans['davies_bouldin_index'] = db
        sklearn_kmeans['n_clusters'] = n_clusters
        sklearn_kmeans['name'] = "sklearn k-means"
        sklearn_kmeans['normalized_mutual_info'] = nmi

        new_context = context.copy()
        new_context[key] = sklearn_kmeans
        return new_context

    @staticmethod
    def use_hierarchical_clustering(
        context: Dict[str, Any],
        X_scaled: DataFrame,
        Y: List[float],
        k: int,
        key: str,
    ) -> Dict[str, Any]:
        hierarchical_clustering = dict()
        
        hc = AgglomerativeClustering(n_clusters=k)
        labels = hc.fit_predict(X_scaled)

        unique_labels = set(labels)
        n_clusters = len(unique_labels - {-1})

        db = davies_bouldin_score(X_scaled, labels)
        nmi = normalized_mutual_info_score(Y, labels)

        hierarchical_clustering['davies_bouldin_index'] = db
        hierarchical_clustering['labels'] = labels
        hierarchical_clustering['n_clusters'] = n_clusters
        hierarchical_clustering['name'] = "Агломеративная"
        hierarchical_clustering['normalized_mutual_info'] = nmi

        new_context = context.copy()
        new_context[key] = hierarchical_clustering
        return new_context

    @staticmethod
    def use_dbscan(
        context: Dict[str, Any],
        X_scaled: DataFrame,
        Y: List[float],
        eps: float,
        min_samples: int,
        key: str,
    ) -> Dict[str, Any]:
        dbscan_values = dict()
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X_scaled)

        unique_labels = set(labels)
        n_clusters = len(unique_labels - {-1})
        n_noise = int((labels == -1).sum())
        
        nmi = normalized_mutual_info_score(Y, labels)
        db = davies_bouldin_score(X_scaled, labels)

        dbscan_values['labels'] = labels
        dbscan_values['davies_bouldin_index'] = db
        dbscan_values['n_clusters'] = n_clusters
        dbscan_values['n_noise'] = n_noise
        dbscan_values['name'] = "DBSCAN"
        dbscan_values['normalized_mutual_info'] = nmi

        new_context = context.copy()
        new_context[key] = dbscan_values
        return new_context

    @staticmethod
    def use_pca(
        context: Dict[str, Any],
        X_scaled: DataFrame,
        Y: List[float],
        n_components: int,
        eps: float,
        min_samples: int,
        key: str,
    ) -> Dict[str, Any]:
        pca_values = dict()
        
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X_pca)

        unique_labels = set(labels)
        n_clusters = len(unique_labels - {-1})
        n_noise = int((labels == -1).sum())

        db = davies_bouldin_score(X_pca, labels)
        nmi = normalized_mutual_info_score(Y, labels)

        pca_values['davies_bouldin_index'] = db
        pca_values['labels'] = labels
        pca_values['n_clusters'] = n_clusters
        pca_values['n_noise'] = n_noise
        pca_values['name'] = "PCA"
        pca_values['normalized_mutual_info'] = nmi

        new_context = context.copy()
        new_context[key] = pca_values
        return new_context

    @staticmethod
    def use_normalization(
        context: Dict[str, Any],
        X_norm: DataFrame,
        Y: List[float],
        k: int,
        key: str,
    ) -> Dict[str, Any]:
        normalization_values = dict()

        hc = AgglomerativeClustering(n_clusters=k)
        labels = hc.fit_predict(X_norm)

        unique_labels = set(labels)
        n_clusters = len(unique_labels)

        db = davies_bouldin_score(X_norm, labels)
        nmi = normalized_mutual_info_score(Y, labels)

        normalization_values['davies_bouldin_index'] = db
        normalization_values['labels'] = labels
        normalization_values['n_clusters'] = n_clusters
        normalization_values['name'] = "Нормализация"
        normalization_values['normalized_mutual_info'] = nmi

        new_context = context.copy()
        new_context[key] = normalization_values
        return new_context