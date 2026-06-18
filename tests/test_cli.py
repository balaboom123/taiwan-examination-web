import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

from app.cli import _download_affected_bundles, build_parser, command_sync, main, run_probe_latest, run_sync_targeted
from app.crawler import DownloadedFile, ResponseMetadata, make_result_url
from app.lootlabs import LootLabsError, LootLabsSettings
from app.models import AliasRule, BundleAsset, ExamOption, NormalizedCatalog, NormalizedPaper, ParsedPaper, SourceExamPage
from app.paths import provider_paths, site_paths
from app.publisher import write_data_files, write_provider_state


def _paper(provider_id: str, canonical_id: str) -> NormalizedPaper:
    canonical_name = "Nurse" if canonical_id == "nurse" else "CEEC GSAT"
    source_exam_id = "115030" if canonical_id == "nurse" else "gsat-115-guozong"
    category_raw = "Nurse" if canonical_id == "nurse" else "GSAT"
    return NormalizedPaper(
        provider_id=provider_id,
        canonical_id=canonical_id,
        canonical_name=canonical_name,
        year_roc=115,
        exam_name_raw=f"115 {canonical_name} Exam",
        category_raw=category_raw,
        subject_name_raw="Subject",
        paper_code="101-0101-question",
        file_type="question",
        download_url_source=f"https://example.test/{provider_id}/{canonical_id}.pdf",
        category_code="101",
        source_exam_id=source_exam_id,
        subject_code="0101",
        storage_key=f"providers/{provider_id}/115/{source_exam_id}/101/0101/question.pdf",
        checksum=f"{provider_id}-{canonical_id}",
    )


class CliBuildSiteTests(unittest.TestCase):
    def test_build_site_command_renders_existing_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            site_dir = root / "site"
            data_dir.mkdir()
            site_dir.mkdir()
            papers_dir = data_dir / "papers"
            papers_dir.mkdir()
            (papers_dir / "2026.json").write_text(
                json.dumps(
                    [
                        {
                            "canonical_id": "nurse",
                            "canonical_name": "護理師",
                            "year_roc": 115,
                            "exam_name_raw": "115年專技高考護理師",
                            "category_raw": "護理師",
                            "category_code": "101",
                            "source_exam_id": "115030",
                            "subject_code": "0101",
                            "subject_name_raw": "基礎醫學",
                            "paper_code": "101-0101-question",
                            "file_type": "question",
                            "download_url_source": "https://source.example/question.pdf",
                            "download_url_mirror": "",
                            "download_url_bundle": f"https://bundles.example/{quote('護理師__nurse.zip')}",
                            "storage_key": "115/115030/101/0101/question.pdf",
                            "checksum": "abc123",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (data_dir / "bundles.json").write_text(
                json.dumps(
                    [
                        {
                            "canonical_id": "nurse",
                            "canonical_name": "護理師",
                            "years": [115],
                            "file_count": 1,
                            "storage_key": "bundles/護理師__nurse.zip",
                            "asset_name": "護理師__nurse.zip",
                            "download_url": f"https://bundles.example/{quote('護理師__nurse.zip')}",
                            "legacy_asset_names": ["nurse.zip"],
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            exit_code = main(["build-site", "--data-dir", str(data_dir), "--site-dir", str(site_dir)])

            self.assertEqual(exit_code, 0)
            html = (site_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("護理師", html)
            self.assertIn("考選部歷屆試題下載", html)
            self.assertIn("下載整理好的中文壓縮檔", html)
            self.assertIn("<th>考試名稱</th>", html)
            self.assertIn("下載壓縮檔", html)
            self.assertNotIn("${paper.canonical_id}", html)
            self.assertNotIn("${paper.file_type}", html)

    def test_sync_incremental_years_flag_is_a_window_size(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["sync-incremental", "--years", "3"])
        self.assertEqual(args.year_window, 3)

    def test_parser_accepts_provider_and_site_for_sync_commands(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["sync-full", "--provider", "moex", "--site-id", "default"])

        self.assertEqual(args.provider, "moex")
        self.assertEqual(args.site_id, "default")

    def test_parser_accepts_publish_site_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["publish-site", "--site-id", "default"])

        self.assertEqual(args.site_id, "default")
        self.assertEqual(args.repository, "example/repo")

    def test_publish_site_command_aggregates_provider_outputs_for_default_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            moex_provider = provider_paths(root, "moex")
            ceec_provider = provider_paths(root, "ceec_gsat")
            moex_paper = _paper("moex", "nurse")
            ceec_paper = _paper("ceec_gsat", "ceec-gsat")

            for paper in (moex_paper, ceec_paper):
                mirror_path = root / "mirror" / paper.storage_key
                mirror_path.parent.mkdir(parents=True, exist_ok=True)
                mirror_path.write_bytes(b"%PDF-1.7 demo")

            write_provider_state(
                moex_provider,
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[moex_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            write_provider_state(
                ceec_provider,
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[ceec_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            exit_code = main(
                [
                    "publish-site",
                    "--repo-root",
                    str(root),
                    "--site-id",
                    "default",
                    "--repository",
                    "example/repo",
                ]
            )

            self.assertEqual(exit_code, 0)
            bundles_payload = json.loads(site_paths(root, "default").bundles_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {bundle["canonical_id"] for bundle in bundles_payload["bundles"]},
                {"nurse", "ceec-gsat"},
            )
            self.assertEqual(
                {bundle["storage_key"] for bundle in bundles_payload["bundles"]},
                {
                    "bundles/sites/default/nurse.zip",
                    "bundles/sites/default/ceec-gsat.zip",
                },
            )

    def test_publish_site_command_returns_non_zero_when_bundle_build_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            broken_paper = _paper("moex", "nurse")
            write_provider_state(
                provider_paths(root, "moex"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[broken_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            write_provider_state(
                provider_paths(root, "ceec_gsat"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "publish-site",
                        "--repo-root",
                        str(root),
                        "--site-id",
                        "default",
                        "--repository",
                        "example/repo",
                    ]
                )

            self.assertEqual(exit_code, 1)
            self.assertIn("Missing mirrored file for bundle entry", output.getvalue())
            self.assertFalse(site_paths(root, "default").bundles_path.exists())
            self.assertFalse((root / "site" / "index.html").exists())

    def test_sync_attachment_defaults_match_command_risk(self) -> None:
        parser = build_parser()

        full_args = parser.parse_args(["sync-full"])
        incremental_args = parser.parse_args(["sync-incremental"])

        self.assertFalse(full_args.download_attachments)
        self.assertFalse(incremental_args.download_attachments)

    def test_removed_pdf_optimization_flags_are_rejected(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["sync-full", "--optimize-pdfs"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["optimize-mirror-pdfs"])

    def test_sync_incremental_can_download_attachments_explicitly(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["sync-incremental", "--download-attachments"])
        self.assertTrue(args.download_attachments)

    def test_sync_incremental_can_write_source_manifest_for_audits(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["sync-incremental", "--write-manifest", "--manifest", "data/source-manifest.json"])
        self.assertTrue(args.write_manifest)
        self.assertEqual(args.manifest, Path("data/source-manifest.json"))

    def test_command_sync_rejects_write_manifest_for_provider_without_probe_support(self) -> None:
        class UnsupportedManifestClient:
            provider_id = "ceec_gsat"

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            args = build_parser().parse_args(
                [
                    "sync-incremental",
                    "--provider",
                    "ceec_gsat",
                    "--write-manifest",
                    "--data-dir",
                    str(root / "data"),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = command_sync(args, client=UnsupportedManifestClient())

        self.assertEqual(exit_code, 1)
        self.assertIn("--write-manifest", output.getvalue())
        self.assertIn("ceec_gsat", output.getvalue())

    def test_probe_latest_parser_accepts_manifest_and_output_paths(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["probe-latest", "--years", "2", "--manifest", "data/source-manifest.json", "--output", ".tmp/source-probe.json"])
        self.assertEqual(args.years, 2)
        self.assertEqual(args.manifest, Path("data/source-manifest.json"))
        self.assertEqual(args.output, Path(".tmp/source-probe.json"))
        self.assertFalse(args.write_manifest)

    def test_run_probe_latest_writes_probe_output_and_manifest_when_requested(self) -> None:
        class ProbeClient:
            def discover_available_years(self) -> list[int]:
                return [2026]

            def discover_exams(self, year_ad: int) -> list[ExamOption]:
                return [ExamOption(code="115040", year_ad=year_ad, year_roc=115, label="Exam 115040")]

            def head(self, url: str) -> ResponseMetadata:
                lengths = {
                    "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2026": 800,
                    make_result_url("115040", 2026): 500,
                }
                return ResponseMetadata(url=url, status=200, content_length=lengths[url])

            def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
                return SourceExamPage(
                    source_exam_id=exam_code,
                    year_ad=year_ad,
                    year_roc=115,
                    exam_name_raw="Exam 115040",
                    attachments=[],
                    papers=[
                        ParsedPaper(
                            category_raw="Category",
                            category_code="101",
                            subject_code="0101",
                            subject_name_raw="Subject",
                            files={"question": "https://example.test/question.pdf"},
                        )
                    ],
                )

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            args = build_parser().parse_args(
                [
                    "probe-latest",
                    "--years",
                    "1",
                    "--manifest",
                    str(root / "source-manifest.json"),
                    "--output",
                    str(root / ".tmp" / "source-probe.json"),
                    "--write-manifest",
                ]
            )

            exit_code = run_probe_latest(args, client=ProbeClient(), now="2026-05-20T00:00:00+08:00")

            probe = json.loads((root / ".tmp" / "source-probe.json").read_text(encoding="utf-8"))
            manifest = json.loads((root / "source-manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertTrue(probe["should_sync"])
        self.assertEqual(probe["changed_exam_codes"], ["115040"])
        self.assertEqual(probe["exam_years"], {"115040": 2026})
        self.assertEqual(probe["updated_manifest"]["years"]["2026"]["exam_codes"], ["115040"])
        self.assertEqual(manifest["years"]["2026"]["exam_codes"], ["115040"])

    def test_run_probe_latest_returns_non_zero_for_provider_without_probe_support(self) -> None:
        class UnsupportedProbeClient:
            provider_id = "ceec_gsat"

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            args = build_parser().parse_args(
                [
                    "probe-latest",
                    "--provider",
                    "ceec_gsat",
                    "--manifest",
                    str(root / "source-manifest.json"),
                    "--output",
                    str(root / ".tmp" / "source-probe.json"),
                    "--write-manifest",
                ]
            )
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = run_probe_latest(args, client=UnsupportedProbeClient(), now="2026-05-20T00:00:00+08:00")

        self.assertEqual(exit_code, 1)
        self.assertIn("ceec_gsat", output.getvalue())
        self.assertFalse((root / ".tmp" / "source-probe.json").exists())
        self.assertFalse((root / "source-manifest.json").exists())

    def test_sync_targeted_parser_accepts_probe_path(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "sync-targeted",
                "--probe",
                ".tmp/source-probe.json",
                "--download-affected-bundles",
                "--release-tag",
                "moex-bundles",
            ]
        )

        self.assertEqual(args.probe, Path(".tmp/source-probe.json"))
        self.assertFalse(args.download_attachments)
        self.assertTrue(args.download_affected_bundles)
        self.assertIsNone(args.provider)
        self.assertEqual(args.release_tag, "moex-bundles")

    @patch("app.cli.subprocess.run")
    def test_download_affected_bundles_checks_primary_and_legacy_asset_names(self, run) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            bundle_dir = Path(tmp_dir) / "bundles"
            _download_affected_bundles(
                bundle_dir,
                [
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        years=[115],
                        file_count=1,
                        storage_key="bundles/護理師__nurse.zip",
                        asset_name="護理師__nurse.zip",
                        legacy_asset_names=["nurse.zip"],
                    )
                ],
                {"nurse"},
                "moex-bundles",
            )

        patterns = [call.args[0][5] for call in run.call_args_list]
        self.assertEqual(patterns, ["nurse.zip", "護理師__nurse.zip"])

    def test_run_sync_targeted_exits_without_writes_when_probe_has_no_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(json.dumps({"should_sync": False}), encoding="utf-8")
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(root / "data"),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )

            exit_code = run_sync_targeted(args, client=None)

            self.assertEqual(exit_code, 0)
            self.assertFalse((root / "data").exists())
            self.assertFalse((root / "site").exists())

    def test_run_sync_targeted_fails_closed_when_refreshed_exam_has_download_failure(self) -> None:
        class FailingTargetedClient:
            def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
                return SourceExamPage(
                    source_exam_id=exam_code,
                    year_ad=year_ad,
                    year_roc=year_ad - 1911,
                    exam_name_raw="Exam 115030",
                    attachments=[],
                    papers=[
                        ParsedPaper(
                            category_raw="nurse raw",
                            category_code="101",
                            subject_code="0101",
                            subject_name_raw="Subject",
                            files={
                                "question": "https://example.test/question.pdf",
                                "answer": "https://example.test/answer.pdf",
                            },
                        )
                    ],
                )

            def download_file(self, url: str) -> DownloadedFile:
                if url.endswith("answer.pdf"):
                    raise RuntimeError("temporary download failure")
                return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            aliases = [AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")]
            existing_papers = [
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="Nurse",
                    year_roc=115,
                    exam_name_raw="Exam 115030",
                    category_raw="nurse raw",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="Subject",
                    paper_code=f"101-0101-{file_type}",
                    file_type=file_type,
                    download_url_source=f"https://example.test/old-{file_type}.pdf",
                    storage_key=f"115/115030/101/0101/{file_type}.pdf",
                    checksum=f"old-{file_type}",
                )
                for file_type in ("question", "answer")
            ]
            write_data_files(
                data_dir=data_dir,
                raw_pages=[
                    SourceExamPage(
                        source_exam_id="115030",
                        year_ad=2026,
                        year_roc=115,
                        exam_name_raw="Exam 115030",
                        attachments=[],
                        papers=[],
                    )
                ],
                normalized=NormalizedCatalog(papers=existing_papers, review_queue=[]),
                aliases=aliases,
                bundles=[
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        years=[115],
                        file_count=2,
                        storage_key="bundles/nurse.zip",
                        asset_name="nurse.zip",
                    )
                ],
                failures=[],
            )
            original_papers = (data_dir / "papers" / "2026.json").read_text(encoding="utf-8")
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(
                json.dumps(
                    {
                        "should_sync": True,
                        "changed_exam_codes": ["115030"],
                        "removed_exam_codes": [],
                        "exam_years": {"115030": 2026},
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(data_dir),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_sync_targeted(args, client=FailingTargetedClient())

            self.assertEqual(exit_code, 1)
            self.assertIn("115030", output.getvalue())
            self.assertIn("101-0101-answer", output.getvalue())
            self.assertIn("temporary download failure", output.getvalue())
            self.assertEqual((data_dir / "papers" / "2026.json").read_text(encoding="utf-8"), original_papers)
            self.assertFalse((root / "site").exists())

    def test_run_sync_targeted_writes_probe_manifest_after_successful_sync(self) -> None:
        class SuccessfulTargetedClient:
            def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
                return SourceExamPage(
                    source_exam_id=exam_code,
                    year_ad=year_ad,
                    year_roc=year_ad - 1911,
                    exam_name_raw="Exam 115040",
                    attachments=[],
                    papers=[
                        ParsedPaper(
                            category_raw="nurse raw",
                            category_code="101",
                            subject_code="0101",
                            subject_name_raw="Subject",
                            files={"question": "https://example.test/question.pdf"},
                        )
                    ],
                )

            def download_file(self, url: str) -> DownloadedFile:
                return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "aliases.json").write_text(
                json.dumps(
                    {
                        "rules": [
                            {
                                "match_type": "exact",
                                "raw_pattern": "nurse raw",
                                "canonical_id": "nurse",
                                "canonical_name": "Nurse",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            manifest_payload = {
                "schema_version": 1,
                "provider_id": "moex",
                "probe_policy": {},
                "years": {"2026": {"year_ad": 2026, "exam_codes": ["115040"]}},
                "exams": {"115040": {"source_exam_id": "115040", "head_content_length": 500}},
                "files": {},
            }
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(
                json.dumps(
                    {
                        "should_sync": True,
                        "changed_exam_codes": ["115040"],
                        "removed_exam_codes": [],
                        "exam_years": {"115040": 2026},
                        "updated_manifest": manifest_payload,
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(data_dir),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                    "--manifest",
                    str(root / "data" / "source-manifest.json"),
                ]
            )

            exit_code = run_sync_targeted(args, client=SuccessfulTargetedClient())

            self.assertEqual(exit_code, 0)
            manifest = json.loads((data_dir / "source-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest, manifest_payload)

    def test_run_sync_targeted_requires_explicit_exam_years_for_non_moex_probe(self) -> None:
        class CeecTargetedClient:
            provider_id = "ceec_gsat"

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(
                json.dumps(
                    {
                        "should_sync": True,
                        "provider_id": "ceec_gsat",
                        "changed_exam_codes": ["gsat-115-guozong"],
                        "removed_exam_codes": [],
                        "exam_years": {},
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--provider",
                    "ceec_gsat",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(root / "data"),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = run_sync_targeted(args, client=CeecTargetedClient())

        self.assertEqual(exit_code, 1)
        self.assertIn("exam_years", output.getvalue())
        self.assertIn("ceec_gsat", output.getvalue())

    @patch("app.cli.build_site")
    @patch("app.cli.write_data_files")
    @patch("app.cli.build_bundles")
    @patch("app.cli.merge_targeted_state")
    @patch("app.cli.load_existing_state")
    @patch("app.cli.sync_exam_pages")
    @patch("app.cli.get_provider")
    def test_run_sync_targeted_uses_probe_provider_when_args_default_to_moex(
        self,
        get_provider_mock,
        sync_exam_pages_mock,
        load_existing_state_mock,
        merge_targeted_state_mock,
        build_bundles_mock,
        _write_data_files_mock,
        _build_site_mock,
    ) -> None:
        class CeecProvider:
            provider_id = "ceec_gsat"

        class WrongProvider:
            provider_id = "moex"

        def provider_factory(provider_id: str):
            if provider_id == "ceec_gsat":
                return CeecProvider()
            if provider_id == "moex":
                return WrongProvider()
            raise AssertionError(provider_id)

        def sync_side_effect(*, client, exam_codes, **_kwargs):
            self.assertEqual(client.provider_id, "ceec_gsat")
            self.assertEqual(exam_codes, [("gsat-115-guozong", 2026)])
            return [], NormalizedCatalog(papers=[], review_queue=[]), []

        get_provider_mock.side_effect = provider_factory
        sync_exam_pages_mock.side_effect = sync_side_effect
        load_existing_state_mock.return_value = ([], NormalizedCatalog(papers=[], review_queue=[]), [], [])
        merge_targeted_state_mock.return_value = ([], NormalizedCatalog(papers=[], review_queue=[]), [], set(), {})
        build_bundles_mock.return_value = type("BuildResult", (), {"bundles": [], "failures": []})()

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(
                json.dumps(
                    {
                        "should_sync": True,
                        "provider_id": "ceec_gsat",
                        "changed_exam_codes": ["gsat-115-guozong"],
                        "removed_exam_codes": [],
                        "exam_years": {"gsat-115-guozong": 2026},
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(root / "data"),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )

            exit_code = run_sync_targeted(args, client=None)

        self.assertEqual(exit_code, 0)
        get_provider_mock.assert_called_with("ceec_gsat")

    @patch("app.cli.sync_exam_pages")
    @patch("app.cli.get_provider")
    def test_run_sync_targeted_fails_when_explicit_provider_mismatches_probe(
        self,
        get_provider_mock,
        sync_exam_pages_mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            probe_path = root / ".tmp" / "source-probe.json"
            probe_path.parent.mkdir()
            probe_path.write_text(
                json.dumps(
                    {
                        "should_sync": True,
                        "provider_id": "ceec_gsat",
                        "changed_exam_codes": ["gsat-115-guozong"],
                        "removed_exam_codes": [],
                        "exam_years": {"gsat-115-guozong": 2026},
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "sync-targeted",
                    "--provider",
                    "moex",
                    "--probe",
                    str(probe_path),
                    "--data-dir",
                    str(root / "data"),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                ]
            )
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = run_sync_targeted(args, client=None)

        self.assertEqual(exit_code, 1)
        self.assertIn("Probe provider mismatch", output.getvalue())
        self.assertIn("ceec_gsat", output.getvalue())
        self.assertIn("moex", output.getvalue())
        get_provider_mock.assert_not_called()
        sync_exam_pages_mock.assert_not_called()


    def test_command_sync_incremental_preserves_existing_data_on_download_failure(self) -> None:
        class PartialFailureClient:
            def discover_available_years(self) -> list[int]:
                return [2026]

            def discover_exams(self, year_ad: int) -> list[ExamOption]:
                return [ExamOption(code="115030", year_ad=2026, year_roc=115, label="Exam")]

            def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
                return SourceExamPage(
                    source_exam_id="115030",
                    year_ad=2026,
                    year_roc=115,
                    exam_name_raw="115年護理師考試",
                    attachments=[],
                    papers=[
                        ParsedPaper(
                            category_raw="護理師",
                            category_code="101",
                            subject_code="0101",
                            subject_name_raw="基礎醫學",
                            files={
                                "question": "https://example.test/question.pdf",
                                "answer": "https://example.test/answer.pdf",
                            },
                        )
                    ],
                )

            def download_file(self, url: str) -> DownloadedFile:
                if url.endswith("answer.pdf"):
                    raise RuntimeError("transient network failure")
                return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            aliases = [AliasRule(match_type="exact", raw_pattern="護理師", canonical_id="nurse", canonical_name="護理師")]
            existing_papers = [
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="護理師",
                    year_roc=115,
                    exam_name_raw="115年護理師考試",
                    category_raw="護理師",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code=f"101-0101-{file_type}",
                    file_type=file_type,
                    download_url_source=f"https://example.test/old-{file_type}.pdf",
                    storage_key=f"115/115030/101/0101/{file_type}.pdf",
                    checksum=f"old-{file_type}",
                )
                for file_type in ("question", "answer")
            ]
            write_data_files(
                data_dir=data_dir,
                raw_pages=[
                    SourceExamPage(
                        source_exam_id="115030",
                        year_ad=2026,
                        year_roc=115,
                        exam_name_raw="115年護理師考試",
                        attachments=[],
                        papers=[],
                    )
                ],
                normalized=NormalizedCatalog(papers=existing_papers, review_queue=[]),
                aliases=aliases,
                bundles=[
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        years=[115],
                        file_count=2,
                        storage_key="bundles/nurse.zip",
                        asset_name="nurse.zip",
                    )
                ],
                failures=[],
            )
            original_papers = json.loads((data_dir / "papers" / "2026.json").read_text(encoding="utf-8"))
            args = build_parser().parse_args(
                [
                    "sync-incremental",
                    "--years",
                    "1",
                    "--data-dir",
                    str(data_dir),
                    "--site-dir",
                    str(root / "site"),
                    "--mirror-dir",
                    str(root / "mirror"),
                    "--bundle-dir",
                    str(root / "bundles"),
                    "--aliases",
                    str(data_dir / "aliases.json"),
                ]
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = command_sync(args, client=PartialFailureClient())

            self.assertEqual(exit_code, 1)
            self.assertIn("failure", output.getvalue().lower())
            papers = json.loads((data_dir / "papers" / "2026.json").read_text(encoding="utf-8"))
            nurse_papers = [p for p in papers if p["source_exam_id"] == "115030"]
            self.assertEqual(len(nurse_papers), 2)
            self.assertEqual({p["file_type"] for p in nurse_papers}, {"question", "answer"})
            self.assertEqual({p["checksum"] for p in nurse_papers}, {"old-question", "old-answer"})

    def test_sync_lootlabs_parser_accepts_data_and_manifest_paths(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "sync-lootlabs",
                "--data-dir",
                "data",
                "--manifest",
                "data/lootlabs-links.json",
            ]
        )

        self.assertEqual(args.data_dir, Path("data"))
        self.assertEqual(args.manifest, Path("data/lootlabs-links.json"))

    @patch("app.cli.sync_lootlabs_manifest", side_effect=LootLabsError("provider down"))
    @patch(
        "app.cli.load_lootlabs_settings_from_env",
        return_value=("token", LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1)),
    )
    def test_sync_lootlabs_returns_non_zero_when_provider_fails(self, _settings, _sync) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "bundles.json").write_text("[]", encoding="utf-8")

            exit_code = main(
                [
                    "sync-lootlabs",
                    "--data-dir",
                    str(data_dir),
                    "--manifest",
                    str(data_dir / "lootlabs-links.json"),
                ]
            )

        self.assertEqual(exit_code, 1)

    @patch("app.cli.sync_lootlabs_manifest")
    def test_sync_lootlabs_returns_non_zero_when_env_numbers_are_invalid(self, sync_mock) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "bundles.json").write_text("[]", encoding="utf-8")
            output = io.StringIO()

            with patch.dict(
                "os.environ",
                {
                    "LOOTLABS_API_KEY": "token",
                    "LOOTLABS_TIER_ID": "abc",
                },
                clear=False,
            ):
                with redirect_stdout(output):
                    exit_code = main(
                        [
                            "sync-lootlabs",
                            "--data-dir",
                            str(data_dir),
                            "--manifest",
                            str(data_dir / "lootlabs-links.json"),
                        ]
                    )

        self.assertEqual(exit_code, 1)
        self.assertIn("LOOTLABS_TIER_ID", output.getvalue())
        sync_mock.assert_not_called()

    @patch("app.cli.sync_lootlabs_manifest")
    @patch("app.cli.load_lootlabs_settings_from_env")
    def test_sync_lootlabs_returns_non_zero_when_bundles_file_is_missing(self, settings_mock, sync_mock) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "sync-lootlabs",
                        "--data-dir",
                        str(data_dir),
                        "--manifest",
                        str(data_dir / "lootlabs-links.json"),
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("bundles.json", output.getvalue())
        settings_mock.assert_not_called()
        sync_mock.assert_not_called()

    @patch("app.cli.sync_lootlabs_manifest")
    @patch("app.cli.load_lootlabs_settings_from_env")
    def test_sync_lootlabs_returns_non_zero_when_bundles_file_is_malformed(self, settings_mock, sync_mock) -> None:
        test_cases = [
            "{not-json",
            json.dumps({"not": "a-list"}),
        ]

        for payload in test_cases:
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    root = Path(tmp_dir)
                    data_dir = root / "data"
                    data_dir.mkdir()
                    (data_dir / "bundles.json").write_text(payload, encoding="utf-8")
                    output = io.StringIO()

                    with redirect_stdout(output):
                        exit_code = main(
                            [
                                "sync-lootlabs",
                                "--data-dir",
                                str(data_dir),
                                "--manifest",
                                str(data_dir / "lootlabs-links.json"),
                            ]
                        )

                self.assertEqual(exit_code, 1)
                self.assertIn("bundles.json", output.getvalue())

        settings_mock.assert_not_called()
        sync_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
