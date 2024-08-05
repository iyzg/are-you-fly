from flask import Flask, request, jsonify
from flask_cors import CORS

import numpy as np
from sentence_transformers import SentenceTransformer


class SimilarityStoreApp():
    def __init__(self, store_dim=5000, top_k=10, ones_per_col=20):
        self.store_dim = store_dim
        self.embed_dim = 384

        self.stored_embeds = np.ones(store_dim)
        # NOTE: k is like number of hash functions from bloom filter
        self.top_k = top_k
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        # NOTE: Random projects act like random hash functions
        self.random_proj = np.zeros((self.embed_dim, store_dim))
        self.rng = np.random.default_rng()

        # Calculate how long to recover
        self.storage_capacity = store_dim / top_k
        self.eps = 1.0 / 1.05 * self.storage_capacity

        # Turn it into sparse, binary matrix with some number of 1s per column
        cols = np.repeat(np.arange(0, store_dim, dtype=np.int32), ones_per_col)
        rows = np.zeros((self.store_dim * ones_per_col))
        for i in range(self.store_dim):
            rows[ones_per_col*i:ones_per_col*i+ones_per_col] = self.rng.choice(
                self.embed_dim, ones_per_col, replace=False)
        
        rows = rows.astype(np.int32)
        self.random_proj[rows, cols] = 1
        print('[+] Finished loading model')

    def _embed(self, text):
        # Use MiniLM for embedding
        embeds = self.model.encode(text)
        proj = embeds @ self.random_proj
        top_k = np.argpartition(proj, kth=self.store_dim - self.top_k)
        return top_k[-self.top_k:]

    def calculate_novelty(self, text):
        idxs = self._embed(text)
        # calculate novelty
        novelty = 0.0
        novelty = np.sum(self.stored_embeds[idxs]) / self.top_k

        # set to 0.0
        self.stored_embeds[idxs] = 0.0

        # For anything not in idxs, add a bit
        increment = np.ones(self.store_dim) * self.eps
        increment[idxs] = 0.0
        self.stored_embeds += increment
        self.stored_embeds = np.clip(self.stored_embeds, 0, 1)

        novelty = round(novelty, 3)
        novelty = int(novelty * 100)
        return novelty


app = Flask(__name__)
fly_app = SimilarityStoreApp()
CORS(app, supports_credentials=True)


@app.route("/api/novelty", methods=["POST"])
def search():
    error = None
    result = []

    text = request.get_json().get("text")
    try:
        result = fly_app.calculate_novelty(text=text)
    except Exception as err:
        error = str(err)
    return jsonify(error=error, result=result)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
