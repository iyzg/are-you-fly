"""
Simulation to measure realistic avoidance factors for the fly game.
Uses synthetic embeddings (no model download needed).

Key insight: we can control "semantic similarity" by generating embeddings
that cluster in subregions of 384-dim space. Common text clusters tightly,
creative text spreads out into unused regions.
"""

import numpy as np


class FlyStore:
    def __init__(self, store_dim=5000, top_k=10, ones_per_col=20, eps=None):
        self.store_dim = store_dim
        self.embed_dim = 384
        self.stored_embeds = np.ones(store_dim)
        self.top_k = top_k
        self.rng = np.random.default_rng(42)

        if eps is None:
            capacity = float(store_dim) / top_k
            self.eps = 1.0 / (1.05 * capacity)
        else:
            self.eps = eps

        # Build sparse random projection (same as app.py)
        self.random_proj = np.zeros((self.embed_dim, store_dim))
        for i in range(store_dim):
            rows = self.rng.choice(self.embed_dim, ones_per_col, replace=False)
            self.random_proj[rows, i] = 1

    def get_neurons(self, embedding):
        """Get the top-k neuron indices for an embedding vector."""
        proj = embedding @ self.random_proj
        top_k = np.argpartition(proj, kth=self.store_dim - self.top_k)
        return top_k[-self.top_k:]

    def query_embedding(self, embedding):
        """Score and update store with an embedding."""
        idxs = self.get_neurons(embedding)
        novelty = np.sum(self.stored_embeds[idxs]) / self.top_k

        self.stored_embeds[idxs] *= 0.05

        increment = np.ones(self.store_dim) * self.eps
        increment[idxs] = 0.0
        self.stored_embeds += increment
        self.stored_embeds = np.clip(self.stored_embeds, 0, 1)

        return int(novelty * 100)

    def depleted_fraction(self, threshold=0.5):
        return np.mean(self.stored_embeds < threshold)

    def mean_value(self):
        return np.mean(self.stored_embeds)

    def snapshot(self):
        return self.stored_embeds.copy()

    def restore(self, snap):
        self.stored_embeds = snap.copy()


def make_clustered_embeddings(rng, n, dim=384, n_clusters=10, spread=0.3):
    """
    Generate embeddings that cluster around a few centers.
    This models "common" text — many texts map to a few semantic regions.
    """
    # Make cluster centers (unit vectors in random directions)
    centers = rng.standard_normal((n_clusters, dim))
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    embeddings = []
    for i in range(n):
        center = centers[i % n_clusters]
        noise = rng.standard_normal(dim) * spread
        emb = center + noise
        emb /= np.linalg.norm(emb)
        embeddings.append(emb)
    return np.array(embeddings)


def make_diverse_embeddings(rng, n, dim=384):
    """
    Generate embeddings spread across the full space.
    This models "creative" text — each text is in a different region.
    """
    embeddings = rng.standard_normal((n, dim))
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings


def make_partially_creative_embeddings(rng, n, dim=384, common_centers=None,
                                        overlap_frac=0.3):
    """
    Mix of common and creative. overlap_frac of the entries land near
    common centers, the rest are in fresh territory.
    """
    n_overlap = int(n * overlap_frac)
    n_fresh = n - n_overlap

    embeddings = []

    # Some entries near common centers
    if common_centers is not None and n_overlap > 0:
        for i in range(n_overlap):
            center = common_centers[rng.integers(len(common_centers))]
            noise = rng.standard_normal(dim) * 0.3
            emb = center + noise
            emb /= np.linalg.norm(emb)
            embeddings.append(emb)

    # Rest are random/fresh
    for _ in range(n_fresh):
        emb = rng.standard_normal(dim)
        emb /= np.linalg.norm(emb)
        embeddings.append(emb)

    rng.shuffle(embeddings)
    return np.array(embeddings)


def measure_neuron_overlap(store, seed_embeddings, test_embeddings):
    """
    Measure what fraction of test_embeddings' neurons overlap with
    neurons already activated by seed_embeddings.
    """
    # Collect all neurons activated by seeds
    seed_neurons = set()
    for emb in seed_embeddings:
        neurons = store.get_neurons(emb)
        seed_neurons.update(neurons)

    # Check overlap for test embeddings
    overlaps = []
    for emb in test_embeddings:
        neurons = set(store.get_neurons(emb))
        overlap = len(neurons & seed_neurons) / len(neurons)
        overlaps.append(overlap)

    return np.mean(overlaps), overlaps


def run_experiment(store_dim, top_k, eps, n_seeds, label=""):
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  D={store_dim}, k={top_k}, eps={eps:.6f}")
    W = 0.95 / eps
    f_theory = 1 - np.exp(-top_k * W / store_dim)
    print(f"  Memory window W = {W:.0f}, Theoretical f = {f_theory:.3f}")
    print(f"  Seeding {n_seeds} entries")
    print(f"{'='*70}")

    rng = np.random.default_rng(123)
    store = FlyStore(store_dim=store_dim, top_k=top_k, eps=eps)

    # ── Generate seed embeddings (common text, clustered) ─────────────
    n_clusters = 15  # ~15 common semantic regions
    seed_embeddings = make_clustered_embeddings(
        rng, n_seeds, n_clusters=n_clusters, spread=0.3
    )

    # Seed the store
    for emb in seed_embeddings:
        store.query_embedding(emb)

    f_actual = store.depleted_fraction(threshold=0.5)
    print(f"\n  Store state after seeding:")
    print(f"    Depleted fraction (< 0.5): {f_actual:.3f}")
    print(f"    Mean neuron value: {store.mean_value():.3f}")

    # ── Neuron overlap analysis ───────────────────────────────────────
    # Get the cluster centers for reuse
    centers = rng.standard_normal((n_clusters, 384))
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    print(f"\n  --- Neuron Overlap Analysis ---")
    print(f"  (What fraction of a player's neurons land in already-depleted regions)")

    # Type 1: Boring (same cluster centers as seeds)
    boring = make_clustered_embeddings(rng, 10, n_clusters=n_clusters, spread=0.2)
    overlap_boring, _ = measure_neuron_overlap(store, seed_embeddings, boring)
    print(f"\n    BORING (same clusters as seeds, tight spread):")
    print(f"      Avg neuron overlap: {overlap_boring:.1%}")

    # Type 2: Decent (same clusters, wider spread)
    decent = make_clustered_embeddings(rng, 10, n_clusters=n_clusters, spread=0.8)
    overlap_decent, _ = measure_neuron_overlap(store, seed_embeddings, decent)
    print(f"    DECENT (same clusters, wider spread):")
    print(f"      Avg neuron overlap: {overlap_decent:.1%}")

    # Type 3: Creative (fully random directions)
    creative = make_diverse_embeddings(rng, 10)
    overlap_creative, _ = measure_neuron_overlap(store, seed_embeddings, creative)
    print(f"    CREATIVE (random directions in embedding space):")
    print(f"      Avg neuron overlap: {overlap_creative:.1%}")

    # Type 4: Mix (30% near common, 70% fresh)
    mixed = make_partially_creative_embeddings(
        rng, 10, common_centers=centers, overlap_frac=0.3
    )
    overlap_mixed, _ = measure_neuron_overlap(store, seed_embeddings, mixed)
    print(f"    MIXED (30% common, 70% fresh):")
    print(f"      Avg neuron overlap: {overlap_mixed:.1%}")

    # ── Actual scoring (with store updates between entries) ───────────
    print(f"\n  --- Actual Scores (10 entries each, store updates between) ---")

    categories = [
        ("BORING ", make_clustered_embeddings(rng, 10, n_clusters=n_clusters, spread=0.2)),
        ("DECENT ", make_clustered_embeddings(rng, 10, n_clusters=n_clusters, spread=0.8)),
        ("CREATIVE", make_diverse_embeddings(rng, 10)),
        ("MIXED  ", make_partially_creative_embeddings(rng, 10, common_centers=centers, overlap_frac=0.3)),
    ]

    snap = store.snapshot()
    for cat_name, embeddings in categories:
        store.restore(snap)
        scores = []
        for emb in embeddings:
            score = store.query_embedding(emb)
            scores.append(score)

        total = sum(scores)
        avg = np.mean(scores)

        # Back-calculate avoidance: score = (1 - 0.95 * f * (1-a)) * 100
        if f_actual > 0:
            effective_a = 1 - (1 - avg / 100) / (0.95 * f_actual)
        else:
            effective_a = 0

        print(f"\n    {cat_name}:")
        print(f"      Scores:  {scores}")
        print(f"      Total:   {total}/1000")
        print(f"      Average: {avg:.1f}")
        print(f"      Effective avoidance: {effective_a:.1%}")


def convergence_test(store_dim, top_k, eps, label=""):
    """Watch how depleted fraction evolves as we seed more entries."""
    print(f"\n{'='*70}")
    print(f"  CONVERGENCE: {label}")
    print(f"{'='*70}")

    rng = np.random.default_rng(42)
    store = FlyStore(store_dim=store_dim, top_k=top_k, eps=eps)
    W = 0.95 / eps

    checkpoints = [10, 50, 100, 200, int(W * 0.5), int(W), int(W * 1.5), int(W * 2)]
    checkpoints = sorted(set(c for c in checkpoints if c > 0))

    total_seeds = max(checkpoints)
    embeddings = make_clustered_embeddings(rng, total_seeds, n_clusters=15, spread=0.3)

    print(f"\n  {'Seeds':>8}  {'f (< 0.5)':>10}  {'Mean value':>10}  {'% of W':>8}")
    print(f"  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*8}")

    idx = 0
    for checkpoint in checkpoints:
        while idx < checkpoint:
            store.query_embedding(embeddings[idx % len(embeddings)])
            idx += 1
        f = store.depleted_fraction(0.5)
        mean = store.mean_value()
        pct_w = checkpoint / W * 100
        print(f"  {checkpoint:>8}  {f:>10.3f}  {mean:>10.3f}  {pct_w:>7.0f}%")


def main():
    print("=" * 70)
    print("  FLY GAME EQUILIBRIUM SIMULATION")
    print("  (Using synthetic embeddings — no model needed)")
    print("=" * 70)

    # ── Convergence tests ─────────────────────────────────────────────
    convergence_test(
        store_dim=5000, top_k=10,
        eps=1.0 / (1.05 * 500),
        label="CURRENT (D=5000, W≈500)"
    )

    convergence_test(
        store_dim=10000, top_k=10,
        eps=0.95 / 357,
        label="PROPOSED (D=10000, W=357)"
    )

    # ── Full scoring experiments ──────────────────────────────────────

    # Current params at equilibrium
    run_experiment(
        store_dim=5000, top_k=10,
        eps=1.0 / (1.05 * 500),
        n_seeds=600,
        label="CURRENT PARAMS AT EQUILIBRIUM"
    )

    # Proposed params at equilibrium
    run_experiment(
        store_dim=10000, top_k=10,
        eps=0.95 / 357,
        n_seeds=500,
        label="PROPOSED PARAMS (D=10000, W=357, target f≈0.30)"
    )

    # Proposed with more seeding (well past equilibrium)
    run_experiment(
        store_dim=10000, top_k=10,
        eps=0.95 / 357,
        n_seeds=1000,
        label="PROPOSED PARAMS, DEEP EQUILIBRIUM (1000 seeds)"
    )

    # ── What about different f targets? ───────────────────────────────
    print("\n\n" + "=" * 70)
    print("  PARAMETER SWEEP: varying W to target different f values")
    print("=" * 70)

    D = 10000
    k = 10
    for target_f in [0.20, 0.25, 0.30, 0.35, 0.40]:
        # f = 1 - e^(-kW/D) → W = -D/k * ln(1-f)
        W = -D / k * np.log(1 - target_f)
        eps = 0.95 / W
        run_experiment(
            store_dim=D, top_k=k, eps=eps,
            n_seeds=int(W * 2),  # 2x memory window = well past equilibrium
            label=f"TARGET f={target_f:.2f} (W={W:.0f}, eps={eps:.5f})"
        )


if __name__ == "__main__":
    main()
