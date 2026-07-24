import unittest

from app.publication_metadata import derive_public_metadata


class PublicationMetadataTests(unittest.TestCase):
    def test_generic_skill_bundle_exposes_clean_subject_label_and_codes(self) -> None:
        aliases, labels = derive_public_metadata(
            [
                {
                    "subject_name_raw": "冷凍空調裝修 丙級 學科",
                    "category_raw": "全國技術士技能檢定",
                    "exam_name_raw": "115年度全國技術士技能檢定第1梯次學科試題暨答案",
                    "category_code": "09501",
                    "subject_code": "09501-class_c-question",
                }
            ],
            bundle_id="wdasec-skill-skill-certification-class-c-example",
            canonical_name="全國技術士技能檢定｜丙級",
        )

        self.assertEqual(labels, ["冷凍空調裝修"])
        self.assertIn("冷凍空調裝修", aliases)
        self.assertIn("09501", aliases)

    def test_admission_labels_split_source_subjects_and_strip_file_descriptors(self) -> None:
        aliases, labels = derive_public_metadata(
            [
                {
                    "subject_name_raw": "數學A 試題內容",
                    "category_raw": "學科能力測驗",
                    "exam_name_raw": "115學年度學科能力測驗",
                    "category_code": "",
                    "subject_code": "math-a",
                }
            ],
            bundle_id="ceec-gsat-admission-gsat-not-applicable-a",
            canonical_name="學科能力測驗",
        )

        self.assertEqual(labels, ["數學A"])
        self.assertIn("數學A", aliases)

    def test_non_generic_bundle_keeps_aliases_searchable_without_row_labels(self) -> None:
        aliases, labels = derive_public_metadata(
            [{"subject_name_raw": "行政法", "category_raw": "一般行政", "exam_name_raw": "高等考試"}],
            bundle_id="moex-civil-high-grade-3-general-administration",
            canonical_name="高等考試｜三等／高考三級｜一般行政",
        )

        self.assertIn("行政法", aliases)
        self.assertEqual(labels, [])


if __name__ == "__main__":
    unittest.main()
