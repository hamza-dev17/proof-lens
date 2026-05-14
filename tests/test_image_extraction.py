import tempfile
import unittest
from pathlib import Path

from prooflens.demo_cases import DemoCase
from prooflens.image_extraction import (
    LocalTemporaryUploadStore,
    ScreenshotExtractionService,
    ScreenshotExtractionUnsupported,
)


class _EchoExtractor:
    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> str:
        return f"OCR:{filename}:{len(image_bytes)}"


class _ExplodingExtractor:
    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> str:
        raise RuntimeError("OCR crashed")


class ScreenshotExtractionServiceTests(unittest.TestCase):
    def test_uploaded_screenshot_is_cleaned_after_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = LocalTemporaryUploadStore(Path(tmp_dir))
            service = ScreenshotExtractionService(
                ocr_extractor=_EchoExtractor(),
                upload_store=store,
                demo_cases=(),
            )

            result = service.extract_from_upload(
                image_bytes=b"image-data",
                filename="claim.png",
                scenario_family="university_announcement",
                selected_university="GIBTU",
            )

            self.assertEqual(result.extracted_text, "OCR:claim.png:10")
            self.assertEqual(result.extraction_source, "upload")
            self.assertEqual(tuple(Path(tmp_dir).rglob("*")), ())

    def test_uploaded_screenshot_is_cleaned_when_ocr_fails(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = LocalTemporaryUploadStore(Path(tmp_dir))
            service = ScreenshotExtractionService(
                ocr_extractor=_ExplodingExtractor(),
                upload_store=store,
                demo_cases=(),
            )

            with self.assertRaises(RuntimeError):
                service.extract_from_upload(
                    image_bytes=b"image-data",
                    filename="claim.png",
                    scenario_family="university_announcement",
                    selected_university="GIBTU",
                )

            self.assertEqual(tuple(Path(tmp_dir).rglob("*")), ())

    def test_demo_case_extraction_uses_contract_without_persisting_raw_screenshot(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = LocalTemporaryUploadStore(Path(tmp_dir))
            demo_case = DemoCase(
                case_id="case-a",
                title="Demo",
                scenario_family="university_announcement",
                plain_text_input="GIBTU final sinavlari iptal edildi deniyor.",
                screenshot_fixture_path="fixtures/screenshots/case-a.png",
                screenshot_contract="placeholder_ocr_fixture",
                selected_university="GIBTU",
                synthetic_demo_only=True,
                synthetic_material_note=(
                    "This screenshot/text pair is synthetic demo material and not an "
                    "Official University Source."
                ),
            )
            service = ScreenshotExtractionService(
                ocr_extractor=_EchoExtractor(),
                upload_store=store,
                demo_cases=(demo_case,),
            )

            result = service.extract_from_demo_case("case-a")

            self.assertEqual(result.extracted_text, demo_case.plain_text_input)
            self.assertEqual(result.extraction_source, "demo_case")
            self.assertEqual(result.demo_case_id, "case-a")
            self.assertEqual(tuple(Path(tmp_dir).rglob("*")), ())

    def test_demo_case_requires_supported_contract(self):
        bad_case = DemoCase(
            case_id="case-b",
            title="Demo",
            scenario_family="university_announcement",
            plain_text_input="Test",
            screenshot_fixture_path="fixtures/screenshots/case-b.png",
            screenshot_contract="unsupported",
            selected_university="GIBTU",
            synthetic_demo_only=True,
            synthetic_material_note=(
                "This screenshot/text pair is synthetic demo material and not an "
                "Official University Source."
            ),
        )
        service = ScreenshotExtractionService(
            ocr_extractor=_EchoExtractor(),
            upload_store=LocalTemporaryUploadStore(Path(tempfile.gettempdir()) / "prooflens-test"),
            demo_cases=(bad_case,),
        )

        with self.assertRaises(ScreenshotExtractionUnsupported):
            service.extract_from_demo_case("case-b")


if __name__ == "__main__":
    unittest.main()
