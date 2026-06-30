import unittest

from app.models import AliasRule, ParsedPaper, NormalizedPaper
from app.normalizer import normalize_papers


class NormalizePapersTests(unittest.TestCase):
    def test_alias_rules_override_general_canonicalization(self) -> None:
        papers = [
            ParsedPaper(
                category_raw="高等考試_護理師",
                category_code="101",
                subject_code="0101",
                subject_name_raw="基礎醫學",
                files={
                    "question": "https://example.test/q.pdf",
                    "answer": "https://example.test/a.pdf",
                },
            ),
        ]
        aliases = [
            AliasRule(
                match_type="exact",
                raw_pattern="高等考試_護理師",
                canonical_id="nurse",
                canonical_name="護理師",
            )
        ]

        normalized = normalize_papers(
            source_exam_id="115030",
            year_ad=2026,
            exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
            papers=papers,
            alias_rules=aliases,
            mirror_base_url="https://mirror.example/releases/download/moex",
            mirror_metadata={
                ("101", "0101", "question"): {"checksum": "abc123", "storage_key": "115/115030/101/0101/question.pdf"},
                ("101", "0101", "answer"): {"checksum": "def456", "storage_key": "115/115030/101/0101/answer.pdf"},
            },
        )

        self.assertEqual(len(normalized.papers), 2)
        self.assertEqual(normalized.review_queue, [])
        self.assertEqual(normalized.papers[0].canonical_id, "nurse")
        self.assertEqual(normalized.papers[0].canonical_name, "護理師")
        self.assertTrue(normalized.papers[0].download_url_mirror.endswith("/115/115030/101/0101/question.pdf"))

    def test_general_rules_reduce_known_exam_prefixes_without_aliases(self) -> None:
        papers = [
            ParsedPaper(
                category_raw="專技高考_社會工作師",
                category_code="103",
                subject_code="0301",
                subject_name_raw="社會工作",
                files={"question": "https://example.test/q.pdf"},
            )
        ]

        normalized = normalize_papers(
            source_exam_id="115030",
            year_ad=2026,
            exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
            papers=papers,
            alias_rules=[],
            mirror_base_url="",
            mirror_metadata={("103", "0301", "question"): {"checksum": "abc123", "storage_key": "115/115030/103/0301/question.pdf"}},
        )

        self.assertEqual(normalized.papers[0].canonical_name, "社會工作師")
        self.assertEqual(normalized.papers[0].canonical_id, "social-worker")
        self.assertEqual(normalized.review_queue, [])

    def test_ambiguous_categories_are_queued_for_review(self) -> None:
        papers = [
            ParsedPaper(
                category_raw="專門職業及技術人員高等考試護理師、心理師考試",
                category_code="999",
                subject_code="0001",
                subject_name_raw="綜合科目",
                files={"question": "https://example.test/q.pdf"},
            )
        ]

        normalized = normalize_papers(
            source_exam_id="114170",
            year_ad=2025,
            exam_name_raw="114年專門職業及技術人員高等考試護理師、心理師考試",
            papers=papers,
            alias_rules=[],
            mirror_base_url="",
            mirror_metadata={("999", "0001", "question"): {"checksum": "abc123", "storage_key": "114/114170/999/0001/question.pdf"}},
        )

        self.assertEqual(normalized.papers[0].canonical_name, "專門職業及技術人員高等考試護理師、心理師考試")
        self.assertEqual(len(normalized.review_queue), 1)
        self.assertEqual(normalized.review_queue[0]["raw_category"], "專門職業及技術人員高等考試護理師、心理師考試")


    def test_fallback_canonical_ids_use_full_string_hashes_instead_of_prefixes(self) -> None:
        papers = [
            ParsedPaper(
                category_raw="abcdefghX",
                category_code="101",
                subject_code="0101",
                subject_name_raw="Subject A",
                files={"question": "https://example.test/a.pdf"},
            ),
            ParsedPaper(
                category_raw="abcdefghY",
                category_code="102",
                subject_code="0101",
                subject_name_raw="Subject B",
                files={"question": "https://example.test/b.pdf"},
            ),
        ]

        normalized = normalize_papers(
            source_exam_id="115999",
            year_ad=2026,
            exam_name_raw="115 demo exam",
            papers=papers,
            alias_rules=[],
            mirror_base_url="",
            mirror_metadata={
                ("101", "0101", "question"): {"checksum": "aaa", "storage_key": "115/115999/101/0101/question.pdf"},
                ("102", "0101", "question"): {"checksum": "bbb", "storage_key": "115/115999/102/0101/question.pdf"},
            },
        )

        self.assertEqual(len(normalized.papers), 2)
        self.assertTrue(all(paper.canonical_id.startswith("canonical-") for paper in normalized.papers))
        self.assertNotEqual(normalized.papers[0].canonical_id, normalized.papers[1].canonical_id)

    def test_requested_topic_providers_use_stable_canonical_ids(self) -> None:
        cases = [
            ("teacher-qual-115", "教師資格考試", "teacher-qual", "教師資格考試"),
            ("teacher-recruit-newtaipei-115-junior", "新北市教師甄試", "teacher-recruit-newtaipei", "新北市教師甄試"),
            (
                "teacher-recruit-taoyuan-elementary-115",
                "桃園市國小教師甄試",
                "teacher-recruit-taoyuan-elementary",
                "桃園市國小教師甄試",
            ),
            ("teacher-recruit-kaohsiung-115-elementary", "高雄市教師甄試", "teacher-recruit-kaohsiung", "高雄市教師甄試"),
            (
                "teacher-recruit-central-alliance-115-elementary",
                "中區策略聯盟教師甄試",
                "teacher-recruit-central-alliance",
                "中區策略聯盟教師甄試",
            ),
            ("teacher-recruit-tainan-115", "臺南市國小教師甄試", "teacher-recruit-tainan", "臺南市國小教師甄試"),
            ("teacher-recruit-taipei-junior-114", "臺北市國中教師甄試", "teacher-recruit-taipei-junior", "臺北市國中教師甄試"),
            (
                "teacher-recruit-taipei-elementary-114",
                "臺北市國小教師甄試",
                "teacher-recruit-taipei-elementary",
                "臺北市國小教師甄試",
            ),
            ("gept-cert-materials", "GEPT全民英檢官方練習資料_初級", "gept-cert", "GEPT全民英檢"),
            ("tocfl-cert-materials", "TOCFL華語文能力測驗官方參考資料", "tocfl-cert", "TOCFL華語文能力測驗"),
            ("hakka-cert-materials", "客語能力認證官方教材及試題_四縣", "hakka-cert", "客語能力認證"),
            ("taigi-cert-materials", "臺灣台語語言能力認證官方試題範例", "taigi-cert", "臺灣台語語言能力認證"),
            ("tqc-cert-samples", "TQC範例試卷_專業知識領域類", "tqc-cert", "TQC電腦技能基金會認證"),
            ("ipas-cert-downloads", "iPAS產業人才能力鑑定官方下載_ISE", "ipas-cert", "iPAS產業人才能力鑑定"),
        ]
        for source_exam_id, category_raw, expected_id, expected_name in cases:
            with self.subTest(source_exam_id=source_exam_id):
                normalized = normalize_papers(
                    source_exam_id=source_exam_id,
                    year_ad=2026,
                    exam_name_raw=category_raw,
                    papers=[
                        ParsedPaper(
                            category_raw=category_raw,
                            category_code="topic",
                            subject_code="download",
                            subject_name_raw="download",
                            files={"question": "https://example.test/file.pdf"},
                        )
                    ],
                    alias_rules=[],
                    mirror_base_url="",
                    mirror_metadata={("topic", "download", "question"): {"checksum": "abc", "storage_key": "topic/download/question.pdf"}},
                )

                self.assertEqual(normalized.papers[0].canonical_id, expected_id)
                self.assertEqual(normalized.papers[0].canonical_name, expected_name)
                self.assertEqual(normalized.review_queue, [])


if __name__ == "__main__":
    unittest.main()
