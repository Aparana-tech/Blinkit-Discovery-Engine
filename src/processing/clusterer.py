import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN

logger = logging.getLogger(__name__)

class ReviewClusterer:
    """Uses local embeddings and HDBSCAN to cluster semantically similar reviews."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # MiniLM is small, fast, and great for clustering short texts locally
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # HDBSCAN is great because it doesn't require knowing the number of clusters (K)
        # min_cluster_size=3 means we need at least 3 similar reviews to form a theme
        self.clusterer = HDBSCAN(min_cluster_size=3, metric='euclidean')

    def cluster_reviews(self, records: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Embeds the text and clusters them.
        Returns a dictionary mapping cluster_id -> list of records in that cluster.
        cluster_id = -1 means 'noise' (didn't fit any cluster).
        """
        if not records:
            return {}

        texts = [r['text'] for r in records]
        
        logger.info(f"Generating embeddings for {len(texts)} reviews...")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        logger.info("Running HDBSCAN clustering...")
        labels = self.clusterer.fit_predict(embeddings)
        
        clusters = {}
        for idx, label in enumerate(labels):
            label_int = int(label)
            if label_int not in clusters:
                clusters[label_int] = []
            
            # Attach the cluster label to the record
            record = records[idx].copy()
            record['cluster_id'] = label_int
            clusters[label_int].append(record)
            
        logger.info(f"Found {len(clusters) - (1 if -1 in clusters else 0)} valid clusters (and noise)")
        return clusters
