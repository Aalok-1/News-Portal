
import math
import re
from collections import Counter
from django.db.models import Q
from newspaper.models import Post, Comment

class ContentEngine:
    def __init__(self):
        self.posts = []
        self.tfidf_matrix = []
        self.vocab = {}
        self.idf = {}
        self._train()

    def _tokenize(self, text):
        # simple tokenization: lowercase, remove non-alphanumeric, split by space
        return re.findall(r'\w+', text.lower())

    def _train(self):
        # Fetch all active posts
        self.posts = list(Post.objects.filter(status='active', published_at__isnull=False))
        if not self.posts:
            return

        # Prepare corpus
        corpus = []
        doc_freq = Counter()
        
        for post in self.posts:
            text = f"{post.title} {post.content}"
            tokens = self._tokenize(text)
            # Remove stopwords (minimal list)
            stopwords = {'the', 'cnt', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
            
            term_counts = Counter(tokens)
            corpus.append(term_counts)
            
            # Update document frequency for IDF
            for term in term_counts:
                doc_freq[term] += 1

        # Calculate IDF
        num_docs = len(self.posts)
        self.vocab = sorted(doc_freq.keys())
        self.idf = {term: math.log(num_docs / (freq + 1)) for term, freq in doc_freq.items()}

        # Calculate TF-IDF Vectors
        self.tfidf_matrix = []
        for term_counts in corpus:
            vector = {}
            # Normalize by total terms in doc (optional but good for long docs)
            total_terms = sum(term_counts.values())
            
            for term, count in term_counts.items():
                tf = count / total_terms
                idf = self.idf[term]
                vector[term] = tf * idf
            
            # Use sparse representation (dict) to save memory
            self.tfidf_matrix.append(vector)

    def _cosine_similarity(self, vec1, vec2):
        # vec1 and vec2 are dicts {term: score}
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[term] * vec2[term] for term in intersection)
        
        magnitude1 = math.sqrt(sum(score**2 for score in vec1.values()))
        magnitude2 = math.sqrt(sum(score**2 for score in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)

    def get_similar_posts(self, post_id, n=5):
        try:
            target_index = next(i for i, p in enumerate(self.posts) if p.id == post_id)
        except StopIteration:
            return []

        target_vector = self.tfidf_matrix[target_index]
        scores = []
        
        for i, vector in enumerate(self.tfidf_matrix):
            if i == target_index:
                continue
            
            score = self._cosine_similarity(target_vector, vector)
            scores.append((score, self.posts[i]))
            
        # Sort by similarity desc
        scores.sort(key=lambda x: x[0], reverse=True)
        return [post for score, post in scores[:n]]

    def recommend(self, user, n=5):
        """
        Recommend items based on user's commented posts.
        Simple logic: Find posts similar to the ones the user commented on.
        """
        if not user.is_authenticated:
            # Fallback: return popular posts? For now, empty list as view handles existing popular fallback.
            return []

        # Get posts user commented on
        interacted_post_ids = Comment.objects.filter(user=user).values_list('post_id', flat=True).distinct()
        if not interacted_post_ids:
            return []

        # Find similarity to ALL interacted posts
        # Aggregate scores
        candidate_scores = {} # {post_id: max_similarity} or sum_similarity
        
        # Pre-compute indices for faster lookup
        post_id_to_index = {p.id: i for i, p in enumerate(self.posts)}
        
        interacted_indices = [post_id_to_index[pid] for pid in interacted_post_ids if pid in post_id_to_index]
        if not interacted_indices:
            return []

        # Iterate all loaded posts
        for i, vector in enumerate(self.tfidf_matrix):
            # Skip if user already interacted
            if self.posts[i].id in interacted_post_ids:
                continue
                
            # Calculate similarity against each interacted post and take the MAX score (or average)
            max_sim = 0
            for int_idx in interacted_indices:
                sim = self._cosine_similarity(vector, self.tfidf_matrix[int_idx])
                if sim > max_sim:
                    max_sim = sim
            
            if max_sim > 0:
                candidate_scores[self.posts[i]] = max_sim
        
        # Sort and return top N
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [post for post, score in sorted_candidates[:n]]
