import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prooflens.corpus import SourceMetadataError, load_corpus


class CuratedCorpusTests(unittest.TestCase):
    def test_loads_seeded_gibtu_official_sources_as_indexable_chunks(self):
        corpus = load_corpus(Path("trusted_sources"))

        gibtu_chunks = [
            chunk
            for chunk in corpus.chunks
            if chunk.metadata.get("selected_university") == "GIBTU"
        ]

        self.assertGreaterEqual(len(gibtu_chunks), 2)
        self.assertTrue(
            all(chunk.metadata["trust_level"] == "official" for chunk in gibtu_chunks)
        )
        self.assertTrue(
            all(
                chunk.metadata["scenario_family"] == "university_announcement"
                for chunk in gibtu_chunks
            )
        )
        self.assertTrue(all(chunk.text.strip() for chunk in gibtu_chunks))
        self.assertTrue(all(chunk.source_path for chunk in gibtu_chunks))

    def test_rejects_sources_missing_required_metadata(self):
        with TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "invalid.md"
            source_path.write_text(
                """---
title: "Eksik Kaynak"
scenario_family: "university_announcement"
---

Eksik metadata ile kanit kaynagi kabul edilmemeli.
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                SourceMetadataError,
                "(?s)(?=.*source_owner)(?=.*trust_level)(?=.*url)(?=.*retrieved_at)",
            ):
                load_corpus(Path(temp_dir))

    def test_distinguishes_official_guidance_and_synthetic_sources(self):
        corpus = load_corpus(Path("trusted_sources"))

        categories = {
            source.metadata["source_category"]: source.metadata["trust_level"]
            for source in corpus.sources
        }

        self.assertEqual(categories["official_university"], "official")
        self.assertEqual(categories["trusted_guidance"], "trusted_guidance")
        self.assertEqual(categories["synthetic_demo"], "synthetic_demo")

        official_gibtu_sources = [
            source
            for source in corpus.sources
            if source.metadata.get("selected_university") == "GIBTU"
        ]

        self.assertTrue(official_gibtu_sources)
        self.assertTrue(
            all(
                source.metadata["source_category"] == "official_university"
                and source.metadata["synthetic"] == "false"
                for source in official_gibtu_sources
            )
        )

    def test_rejects_synthetic_or_official_looking_gibtu_sources(self):
        with TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "fake-gibtu.md"
            source_path.write_text(
                """---
title: "Sahte GIBTU Duyurusu"
source_owner: "ProofLens Demo Team"
url: "https://example.invalid/fake-gibtu"
trust_level: "synthetic_demo"
retrieved_at: "2026-05-12"
scenario_family: "university_announcement"
selected_university: "GIBTU"
source_category: "synthetic_demo"
synthetic: "true"
---

Bu kaynak GIBTU icin kanit olarak kabul edilmemeli.
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SourceMetadataError, "GIBTU"):
                load_corpus(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
