from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
import uuid
from typing import Protocol

from prooflens.demo_cases import DemoCase, load_demo_cases


class ScreenshotExtractionUnsupported(ValueError):
    """Raised when screenshot extraction parameters are unsupported."""


@dataclass(frozen=True)
class ExtractedTextReview:
    input_type: str
    scenario_family: str
    selected_university: str | None
    extracted_text: str
    extraction_source: str
    demo_case_id: str | None = None


class OcrExtractor(Protocol):
    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> str:
        ...


class DeterministicStubOcrExtractor:
    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> str:
        preview = image_bytes[:64].decode("utf-8", errors="ignore").strip()
        normalized_preview = " ".join(preview.split()) or "goruntu icerigi"
        return (
            f"OCR (deterministic stub) {filename}: "
            f"{normalized_preview}"
        )


class LocalTemporaryUploadStore:
    def __init__(self, base_dir: Path | str | None = None) -> None:
        self._base_dir = Path(base_dir) if base_dir is not None else Path(
            tempfile.gettempdir()
        ) / "prooflens-temp-uploads"

    def save(self, *, image_bytes: bytes, filename: str) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(filename or "upload.bin").name
        upload_path = self._base_dir / f"{uuid.uuid4().hex}-{safe_name}"
        upload_path.write_bytes(image_bytes)
        return upload_path

    def cleanup(self, upload_path: Path) -> None:
        if upload_path.exists():
            upload_path.unlink()
        if self._base_dir.exists() and not any(self._base_dir.iterdir()):
            self._base_dir.rmdir()


class ScreenshotExtractionService:
    def __init__(
        self,
        *,
        ocr_extractor: OcrExtractor,
        upload_store: LocalTemporaryUploadStore,
        demo_cases: tuple[DemoCase, ...],
    ) -> None:
        self._ocr_extractor = ocr_extractor
        self._upload_store = upload_store
        self._demo_cases_by_id = {case.case_id: case for case in demo_cases}

    def extract_from_upload(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> ExtractedTextReview:
        upload_path = self._upload_store.save(image_bytes=image_bytes, filename=filename)
        try:
            extracted_text = self._ocr_extractor.extract_text(
                image_bytes=image_bytes,
                filename=filename or upload_path.name,
                scenario_family=scenario_family,
                selected_university=selected_university,
            )
        finally:
            self._upload_store.cleanup(upload_path)

        return ExtractedTextReview(
            input_type="image",
            scenario_family=scenario_family,
            selected_university=selected_university,
            extracted_text=extracted_text,
            extraction_source="upload",
        )

    def extract_from_demo_case(self, demo_case_id: str) -> ExtractedTextReview:
        demo_case = self._demo_cases_by_id.get(demo_case_id)
        if demo_case is None:
            raise ScreenshotExtractionUnsupported(
                f"Unknown demo_case_id: {demo_case_id}"
            )

        if demo_case.screenshot_contract != "placeholder_ocr_fixture":
            raise ScreenshotExtractionUnsupported(
                f"Unsupported screenshot_contract: {demo_case.screenshot_contract}"
            )

        return ExtractedTextReview(
            input_type="image",
            scenario_family=demo_case.scenario_family,
            selected_university=demo_case.selected_university,
            extracted_text=demo_case.plain_text_input,
            extraction_source="demo_case",
            demo_case_id=demo_case.case_id,
        )


def build_default_screenshot_service() -> ScreenshotExtractionService:
    fixtures_path = Path("fixtures/demo_cases.json")
    demo_cases = load_demo_cases(fixtures_path) if fixtures_path.exists() else ()
    return ScreenshotExtractionService(
        ocr_extractor=DeterministicStubOcrExtractor(),
        upload_store=LocalTemporaryUploadStore(),
        demo_cases=demo_cases,
    )
