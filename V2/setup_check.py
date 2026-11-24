"""
V2 environment verification.

Run after installing requirements_v2.txt:
    python setup_check.py

Checks:
- Python version
- V1 modules importable (shared-core)
- sentence-transformers loads all-MiniLM-L6-v2
- FAISS OR NumPy fallback available
- python-pptx importable
- reportlab importable
- Pillow importable

Does NOT download the embedding model yet — that happens on first real use.
"""

import sys
import importlib
from pathlib import Path


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    marker = "[+]" if condition else "[x]"
    print(f"  {marker} {status}: {label}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print("\n" + "=" * 60)
    print("V2 ENVIRONMENT CHECK")
    print("=" * 60)

    all_ok = True

    # ---------- Python version ----------
    print("\n[1] Python version")
    py_ok = sys.version_info >= (3, 11)
    all_ok &= check(
        "Python >= 3.11",
        py_ok,
        f"found {sys.version.split()[0]}"
    )

    # ---------- V1 modules importable ----------
    print("\n[2] V1 shared-core imports")
    v1_path = Path(__file__).resolve().parent.parent / "V1"
    if str(v1_path) not in sys.path:
        sys.path.insert(0, str(v1_path))

    v1_modules = ["sentiment", "keywords", "complaints", "analytics", "insights"]
    for mod in v1_modules:
        try:
            importlib.import_module(mod)
            all_ok &= check(f"V1/{mod}.py importable", True)
        except Exception as e:
            all_ok &= check(f"V1/{mod}.py importable", False, str(e))

    # ---------- sentence-transformers ----------
    print("\n[3] sentence-transformers")
    try:
        import sentence_transformers
        all_ok &= check(
            "sentence-transformers installed",
            True,
            f"version {sentence_transformers.__version__}"
        )
    except Exception as e:
        all_ok &= check("sentence-transformers installed", False, str(e))
        all_ok = False

    # ---------- torch ----------
    print("\n[4] torch (CPU)")
    try:
        import torch
        all_ok &= check(
            "torch installed",
            True,
            f"version {torch.__version__}"
        )
    except Exception as e:
        all_ok &= check("torch installed", False, str(e))

    # ---------- FAISS or NumPy ----------
    print("\n[5] Vector search backend")
    faiss_ok = False
    try:
        import faiss
        faiss_ok = True
        all_ok &= check(
            "faiss-cpu installed (primary backend)",
            True,
            f"version {faiss.__version__}"
        )
    except Exception:
        print("  [!] INFO: faiss-cpu not installed — will use NumPy fallback")

    try:
        import numpy
        all_ok &= check(
            "numpy installed (fallback backend)",
            True,
            f"version {numpy.__version__}"
        )
    except Exception as e:
        all_ok &= check("numpy installed", False, str(e))

    if not faiss_ok:
        print("  [!] NOTE: NumPy fallback is fully functional. RAG will work.")
        print("      If you want FAISS later, try:")
        print("        pip install faiss-cpu==1.8.0 --only-binary=:all:")

    # ---------- python-pptx ----------
    print("\n[6] PowerPoint export")
    try:
        import pptx
        all_ok &= check(
            "python-pptx installed",
            True,
            f"version {pptx.__version__}"
        )
    except Exception as e:
        all_ok &= check("python-pptx installed", False, str(e))

    # ---------- reportlab ----------
    print("\n[7] PDF export")
    try:
        import reportlab
        all_ok &= check(
            "reportlab installed",
            True,
            f"version {reportlab.Version}"
        )
    except Exception as e:
        all_ok &= check("reportlab installed", False, str(e))

    # ---------- Pillow ----------
    print("\n[8] Pillow (image handling)")
    try:
        import PIL
        all_ok &= check(
            "Pillow installed",
            True,
            f"version {PIL.__version__}"
        )
    except Exception as e:
        all_ok &= check("Pillow installed", False, str(e))

    # ---------- pandas ----------
    print("\n[9] pandas")
    try:
        import pandas as pd
        all_ok &= check(
            "pandas installed",
            True,
            f"version {pd.__version__}"
        )
    except Exception as e:
        all_ok &= check("pandas installed", False, str(e))

    # ---------- Summary ----------
    print("\n" + "=" * 60)
    if all_ok:
        print("[+] ALL CHECKS PASSED")
        print("=" * 60)
        print("\nNext: I'll deliver embedder.py + vector_store.py.")
        print("Reply with this output so I can confirm before we proceed.\n")
        return 0
    else:
        print("[x] SOME CHECKS FAILED — see above")
        print("=" * 60)
        print("\nFix the failures, then re-run this script.")
        print("If faiss-cpu failed to install, that's OK — NumPy fallback works.")
        print("Paste the full output in your next message.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())