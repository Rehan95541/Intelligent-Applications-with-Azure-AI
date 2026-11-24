"""
Test embedder + vector store.

Run from inside v2/:
    python test_embedder.py

Expected: all checks pass, and the battery query returns battery-related
reviews before delivery-related ones (similarity ordering is correct).
"""

import sys
from pathlib import Path

# Allow importing v2 modules when running from v2/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from embedder import Embedder
from vector_store import VectorStore


def check(label, condition, detail=""):
    marker = "[+]" if condition else "[x]"
    print(f"  {marker} {'PASS' if condition else 'FAIL'}: {label}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print("\n" + "=" * 60)
    print("STEP B — EMBEDDER + VECTOR STORE TEST")
    print("=" * 60)

    all_ok = True

    # ---------- 1. Embedder loads ----------
    print("\n[1] Loading embedder (first run downloads ~90 MB model)")
    try:
        emb = Embedder()
        all_ok &= check("Embedder instantiated", True)
    except Exception as e:
        print(f"  [x] FAIL: {e}")
        print("\nIf this failed, run: pip install sentence-transformers torch")
        return 1

    # ---------- 2. Embed produces correct shape ----------
    print("\n[2] Embedding shape")
    sample_texts = [
        "Battery drains very fast",
        "Delivery was two days late",
        "Excellent picture quality",
        "Customer support never replied",
        "Charging port broke after a week",
    ]
    vectors = emb.embed(sample_texts)
    all_ok &= check(
        "Shape is (5, 384)",
        vectors.shape == (5, 384),
        f"got {vectors.shape}"
    )
    all_ok &= check(
        "Vectors are L2-normalized (norm ≈ 1)",
        abs(float((vectors ** 2).sum(axis=1).mean()) - 1.0) < 0.01,
        f"mean squared norm = {(vectors ** 2).sum(axis=1).mean():.4f}"
    )

    # ---------- 3. Vector store builds ----------
    print("\n[3] Vector store build")
    store = VectorStore(dimension=384)
    print(f"  [!] Backend: {store.backend_name}")

    metadata = [
        {"product": "Laptop", "sentiment": "Negative", "feedback": sample_texts[0], "row_index": 0},
        {"product": "Phone",  "sentiment": "Negative", "feedback": sample_texts[1], "row_index": 1},
        {"product": "Tablet", "sentiment": "Positive", "feedback": sample_texts[2], "row_index": 2},
        {"product": "Laptop", "sentiment": "Negative", "feedback": sample_texts[3], "row_index": 3},
        {"product": "Phone",  "sentiment": "Negative", "feedback": sample_texts[4], "row_index": 4},
    ]
    store.add(vectors, metadata)
    all_ok &= check("Store length = 5", len(store) == 5, f"got {len(store)}")

    # ---------- 4. Semantic search: battery query ----------
    print("\n[4] Semantic search — 'battery is bad'")
    q = emb.embed_one("the battery is really bad")
    results = store.search(q, k=3, threshold=0.0)

    all_ok &= check("Got 3 results", len(results) == 3, f"got {len(results)}")

    if results:
        top_feedback = results[0]["metadata"]["feedback"].lower()
        all_ok &= check(
            "Top result is battery-related",
            "battery" in top_feedback or "charging" in top_feedback,
            f"top: '{results[0]['metadata']['feedback']}'"
        )
        print("\n  Top 3 for 'battery is bad':")
        for r in results:
            print(f"    sim={r['similarity']:.3f}  {r['metadata']['feedback']}")

    # ---------- 5. Similarity ordering: battery > delivery ----------
    print("\n[5] Similarity ordering — battery query should rank battery reviews higher")
    if len(results) >= 2:
        battery_sim = max(
            (r["similarity"] for r in results if "battery" in r["metadata"]["feedback"].lower()),
            default=0.0
        )
        delivery_sim = max(
            (r["similarity"] for r in results if "delivery" in r["metadata"]["feedback"].lower()),
            default=0.0
        )
        all_ok &= check(
            "Battery review ranks higher than delivery review",
            battery_sim > delivery_sim,
            f"battery={battery_sim:.3f}, delivery={delivery_sim:.3f}"
        )

    # ---------- 6. Threshold filter ----------
    print("\n[6] Similarity threshold")
    high_threshold = store.search(q, k=5, threshold=0.6)
    low_threshold = store.search(q, k=5, threshold=0.0)
    all_ok &= check(
        "Higher threshold returns fewer or equal results",
        len(high_threshold) <= len(low_threshold),
        f"0.6 -> {len(high_threshold)} results, 0.0 -> {len(low_threshold)} results"
    )

    # ---------- 7. Metadata filter ----------
    print("\n[7] Metadata filter — product=Laptop")
    filtered = store.search(q, k=5, threshold=0.0, filters={"product": "Laptop"})
    all_ok &= check(
        "All filtered results are Laptop",
        all(r["metadata"]["product"] == "Laptop" for r in filtered),
        f"got {len(filtered)} results"
    )
    all_ok &= check(
        "Filtered results exclude non-Laptop",
        len(filtered) <= 2,
        f"got {len(filtered)} (expected <= 2 Laptops)"
    )

    # ---------- 8. Empty filter returns nothing ----------
    print("\n[8] Filter matching nothing")
    nothing = store.search(q, k=5, threshold=0.0, filters={"product": "Microwave"})
    all_ok &= check("Returns 0 results for unknown product", len(nothing) == 0)

    # ---------- 9. Reset ----------
    print("\n[9] Reset store")
    store.reset()
    all_ok &= check("Store is empty after reset", len(store) == 0)

    # ---------- Summary ----------
    print("\n" + "=" * 60)
    if all_ok:
        print("[+] STEP B COMPLETE — all checks passed")
        print("=" * 60)
        print("\nNext: I'll deliver Step C (rag_engine.py).")
        print("Paste this output in your reply.\n")
        return 0
    else:
        print("[x] SOME CHECKS FAILED")
        print("=" * 60)
        print("\nPaste the full output so I can diagnose.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())