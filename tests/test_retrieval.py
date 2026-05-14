import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from prooflens.corpus import load_corpus
from prooflens.retrieval import EvidenceRetriever, index_corpus


class EvidenceRetrievalTests(unittest.TestCase):
    def test_retrieves_only_selected_university_evidence(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trusted_sources = root / "trusted_sources"
            trusted_sources.mkdir()

            (trusted_sources / "gibtu.md").write_text(
                """---
title: "GIBTU Duyuru"
source_owner: "GIBTU"
url: "https://www.gibtu.edu.tr/duyuru"
trust_level: "official"
retrieved_at: "2026-05-12"
scenario_family: "university_announcement"
selected_university: "GIBTU"
source_type: "official_announcement_archive"
source_category: "official_university"
synthetic: "false"
---

Final sinav takvimi burada yayinlanir.
""",
                encoding="utf-8",
            )
            (trusted_sources / "abc.md").write_text(
                """---
title: "ABCU Duyuru"
source_owner: "ABCU"
url: "https://www.abcu.edu/duyuru"
trust_level: "official"
retrieved_at: "2026-05-12"
scenario_family: "university_announcement"
selected_university: "ABCU"
source_type: "official_announcement_archive"
source_category: "official_university"
synthetic: "false"
---

Final sinavlarina ait duyuru.
""",
                encoding="utf-8",
            )

            corpus = load_corpus(trusted_sources)
            retriever = index_corpus(corpus)
            results = retriever.retrieve(
                query_text="Final sinav takvimi",
                scenario_family="university_announcement",
                selected_university="GIBTU",
                top_k=5,
            )

            self.assertTrue(results)
            self.assertTrue(
                all(
                    item.metadata.get("selected_university") == "GIBTU"
                    for item in results
                )
            )

    def test_filters_by_scenario_family(self):
        corpus = load_corpus(Path("trusted_sources"))
        retriever = index_corpus(corpus)

        results = retriever.retrieve(
            query_text="job scam",
            scenario_family="internship_job_scam",
            selected_university=None,
            top_k=5,
        )

        self.assertTrue(results)
        self.assertTrue(
            all(
                item.metadata.get("scenario_family") == "internship_job_scam"
                for item in results
            )
        )

    def test_returns_required_citation_metadata_and_source_badges(self):
        corpus = load_corpus(Path("trusted_sources"))
        retriever = index_corpus(corpus)

        result = retriever.retrieve(
            query_text="akademik takvim",
            scenario_family="university_announcement",
            selected_university="GIBTU",
            top_k=1,
        )[0]

        citation = result.citation
        self.assertIn("title", citation)
        self.assertIn("source_owner", citation)
        self.assertIn("url", citation)
        self.assertIn("trust_level", citation)
        self.assertIn("retrieved_at", citation)
        self.assertIn("source_badges", citation)
        self.assertTrue(citation["source_badges"])

    def test_uses_local_embeddings_and_does_not_call_web(self):
        corpus = load_corpus(Path("trusted_sources"))

        with patch("urllib.request.urlopen") as mocked_urlopen:
            retriever = index_corpus(corpus)
            self.assertIn("local", retriever.embedding_provider)

            retriever.retrieve(
                query_text="duyuru",
                scenario_family="university_announcement",
                selected_university="GIBTU",
                top_k=3,
            )

            mocked_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
