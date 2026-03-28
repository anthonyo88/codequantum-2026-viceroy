"""
Demo cache — pre-answered Q&A pairs for instant responses during demos.

On first use the cache embeds all pre-written questions once using the same
local sentence-transformers model already loaded by LLMClient.  Subsequent
lookups are a cosine-similarity scan in memory (< 1 ms).

Two caches are maintained:
  • driver  — questions about driver recruitment / performance
  • betting — questions about race betting predictions
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from app.rag.llm_client import _get_st_model

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_DRIVER_CACHE_FILE = _DATA_DIR / "demo_cache_drivers.json"
_BETTING_CACHE_FILE = _DATA_DIR / "demo_cache_betting.json"

# Minimum cosine similarity to count as a cache hit.
# 0.88 catches paraphrases; lower this if too many misses, raise if wrong answers surface.
_SIMILARITY_THRESHOLD = 0.88


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _encode_batch(texts: list[str]) -> np.ndarray:
    """Synchronous batch encode — called inside a thread pool executor."""
    model = _get_st_model()
    return model.encode(texts, show_progress_bar=False)


class DemoCache:
    """
    Singleton semantic cache.  Call ``await cache.check_driver(query)`` or
    ``await cache.check_betting(query)`` before hitting the LLM.
    """

    def __init__(self) -> None:
        self._driver_entries: list[dict] = []
        self._betting_entries: list[dict] = []
        self._ready = False
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Load JSON files and embed all questions.  Safe to call multiple times."""
        async with self._lock:
            if self._ready:
                return
            loop = asyncio.get_event_loop()

            self._driver_entries = await loop.run_in_executor(
                None, self._load_and_embed, _DRIVER_CACHE_FILE
            )
            self._betting_entries = await loop.run_in_executor(
                None, self._load_and_embed, _BETTING_CACHE_FILE
            )

            self._ready = True
            logger.info(
                "DemoCache ready — %d driver entries, %d betting entries",
                len(self._driver_entries),
                len(self._betting_entries),
            )

    @staticmethod
    def _load_and_embed(path: Path) -> list[dict]:
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)

        questions = [e["question"] for e in entries]
        embeddings = _encode_batch(questions)  # shape: (n, dim)

        result = []
        for entry, emb in zip(entries, embeddings):
            result.append({**entry, "_embedding": emb})
        return result

    # ------------------------------------------------------------------
    # Public lookup methods
    # ------------------------------------------------------------------

    async def check_driver(self, query: str) -> Optional[dict]:
        """
        Return the cached driver entry if a pre-written question is similar
        enough to *query*, otherwise return None.

        Returned dict contains: ``answer`` (str) and ``driver_names`` (list[str]).
        """
        return await self._lookup(query, self._driver_entries)

    async def check_betting(self, query: str) -> Optional[dict]:
        """
        Return the cached betting entry if a pre-written question is similar
        enough to *query*, otherwise return None.

        Returned dict contains: ``summary`` (str) and ``picks`` (list[dict]).
        """
        return await self._lookup(query, self._betting_entries)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _lookup(self, query: str, entries: list[dict]) -> Optional[dict]:
        await self.initialize()

        loop = asyncio.get_event_loop()
        query_emb: np.ndarray = await loop.run_in_executor(
            None, _get_st_model().encode, query
        )

        best_score = 0.0
        best_entry: Optional[dict] = None

        for entry in entries:
            score = _cosine_similarity(query_emb, entry["_embedding"])
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_score >= _SIMILARITY_THRESHOLD:
            logger.debug(
                "DemoCache hit (score=%.3f): '%s'", best_score, best_entry["question"]
            )
            return best_entry

        logger.debug("DemoCache miss (best=%.3f) for query: '%s'", best_score, query)
        return None


# Module-level singleton — imported by pipeline.py and betting.py
_demo_cache = DemoCache()


def get_demo_cache() -> DemoCache:
    return _demo_cache
