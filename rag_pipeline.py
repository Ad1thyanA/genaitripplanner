# rag_pipeline.py

from typing import List, Dict, Any

import pandas as pd
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class TourismRAGPipeline:
    """
    RAG pipeline for Indian tourism data.

    - Loads data/tourism_data.csv
    - Builds vector store over the "description" field
    - Keeps useful metadata (city, state, region, tags, rating, etc.)
    - Provides strict destination-based semantic search:
        * "Mumbai" -> only Mumbai / Maharashtra region
        * "Goa" -> only Goa
        * "Mumbai, Goa" -> both Mumbai & Goa
        * If nothing matches, falls back to pan-India results (so app doesn't crash)
    """

    def __init__(self, data_path: str = "data/tourism_data.csv") -> None:
        self.data_path = data_path
        self.df = pd.read_csv(self.data_path)
        self.vectorstore: FAISS | None = None
        self._build_vectorstore()

    def _build_vectorstore(self) -> None:
        """
        Build FAISS vector store from tourism_data.csv using HuggingFace embeddings.
        """
        df = self.df.fillna("")

        docs: list[Document] = []

        for _, row in df.iterrows():
            description = str(row.get("description", ""))

            metadata: Dict[str, Any] = {
                "name": str(row.get("name", "")),
                "city": str(row.get("city", "")),
                "state": str(row.get("state", "")),
                "region": str(row.get("region", "")),
                "tags": str(row.get("tags", "")),
                "best_season": str(row.get("best_season", "")),
                "cost_level": str(row.get("cost_level", "medium")).lower(),
            }

            try:
                metadata["typical_duration_hours"] = int(row.get("typical_duration_hours", 3))
            except Exception:
                metadata["typical_duration_hours"] = 3

            try:
                metadata["rating"] = float(row.get("rating", 0.0))
            except Exception:
                metadata["rating"] = 0.0

            try:
                metadata["review_count_lakhs"] = float(row.get("review_count_lakhs", 0.0))
            except Exception:
                metadata["review_count_lakhs"] = 0.0

            docs.append(Document(page_content=description, metadata=metadata))

        embeddings = HuggingFaceEmbeddings()
        self.vectorstore = FAISS.from_documents(docs, embeddings)

    def search_attractions(
        self,
        destination: str,
        interests: List[str],
        k: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for attractions matching destination + interests.

        STRICT city/state/region filtering:
        - If user gives "Mumbai", only Mumbai / Maharashtra / region matches are kept.
        - If user gives "Mumbai, Goa", both Mumbai & Goa regions are used.
        - If no match is found for the destination at all, we fall back to the raw semantic results.
        """

        if self.vectorstore is None:
            self._build_vectorstore()

        destination = (destination or "").strip()
        interests = interests or []

        query = f"Tourist attractions in {destination} for interests: {', '.join(interests)}"
        raw_results = self.vectorstore.similarity_search(query, k=k)

        dest_tokens = [
            d.strip().lower()
            for d in destination.split(",")
            if d.strip()
        ]

        filtered_docs = []
        if dest_tokens:
            for doc in raw_results:
                city = str(doc.metadata.get("city", "")).lower()
                state = str(doc.metadata.get("state", "")).lower()
                region = str(doc.metadata.get("region", "")).lower()

                if any(
                    dt in city
                    or dt in state
                    or dt in region
                    for dt in dest_tokens
                ):
                    filtered_docs.append(doc)

        results = filtered_docs if filtered_docs else raw_results

        attractions: List[Dict[str, Any]] = []
        for doc in results:
            data = dict(doc.metadata)
            data["summary"] = doc.page_content
            attractions.append(data)

        return attractions
