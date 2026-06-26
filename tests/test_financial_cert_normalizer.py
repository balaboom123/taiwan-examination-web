import unittest

from app.normalizer import _derive_canonical


class SfiCertCanonicalTests(unittest.TestCase):
    def _derive(self, source_exam_id: str) -> tuple[str, str, str, bool]:
        return _derive_canonical(source_exam_id, "", "", 2025, [])

    def test_securities_dealer(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-securities-dealer-2025-03")
        self.assertEqual(cid, "sfi-securities-dealer")
        self.assertEqual(cname, "證券商業務員")
        self.assertFalse(review)

    def test_senior_securities_dealer(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-senior-securities-dealer-2025-01")
        self.assertEqual(cid, "sfi-senior-securities-dealer")
        self.assertEqual(cname, "證券商高級業務員")
        self.assertFalse(review)

    def test_futures_dealer(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-futures-dealer-2025-06")
        self.assertEqual(cid, "sfi-futures-dealer")
        self.assertEqual(cname, "期貨商業務員")
        self.assertFalse(review)

    def test_securities_analyst(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-securities-analyst-2025-01")
        self.assertEqual(cid, "sfi-securities-analyst")
        self.assertEqual(cname, "證券投資分析人員")
        self.assertFalse(review)

    def test_sitca(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-sitca-2025-03")
        self.assertEqual(cid, "sfi-sitca")
        self.assertEqual(cname, "投信投顧業務員")
        self.assertFalse(review)

    def test_corporate_internal_control(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-corporate-internal-control-2025-01")
        self.assertEqual(cid, "sfi-corporate-internal-control")
        self.assertEqual(cname, "企業內部控制基本能力測驗")
        self.assertFalse(review)

    def test_bills_dealer(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-bills-dealer-2025-06")
        self.assertEqual(cid, "sfi-bills-dealer")
        self.assertEqual(cname, "票券商業務人員")
        self.assertFalse(review)

    def test_stock_affairs(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-stock-affairs-2025-03")
        self.assertEqual(cid, "sfi-stock-affairs")
        self.assertEqual(cname, "股務人員")
        self.assertFalse(review)

    def test_asset_securitization(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-asset-securitization-2025-01")
        self.assertEqual(cid, "sfi-asset-securitization")
        self.assertEqual(cname, "資產證券化基本能力測驗")
        self.assertFalse(review)

    def test_business_ethics(self) -> None:
        cid, cname, _, review = self._derive("sfi-cert-business-ethics-2025-06")
        self.assertEqual(cid, "sfi-business-ethics")
        self.assertEqual(cname, "工商倫理測驗")
        self.assertFalse(review)


class TabfCertCanonicalTests(unittest.TestCase):
    def _derive(self, source_exam_id: str) -> tuple[str, str, str, bool]:
        return _derive_canonical(source_exam_id, "", "", 2025, [])

    def test_bank_internal_control(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-bank-internal-control-2025-03")
        self.assertEqual(cid, "tabf-bank-internal-control")
        self.assertEqual(cname, "銀行內部控制與內部稽核")
        self.assertFalse(review)

    def test_trust_business(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-trust-business-2025-06")
        self.assertEqual(cid, "tabf-trust-business")
        self.assertEqual(cname, "信託業務人員")
        self.assertFalse(review)

    def test_financial_planning(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-financial-planning-2025-01")
        self.assertEqual(cid, "tabf-financial-planning")
        self.assertEqual(cname, "理財規劃人員")
        self.assertFalse(review)

    def test_fx_junior(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-fx-junior-2025-03")
        self.assertEqual(cid, "tabf-fx-junior")
        self.assertEqual(cname, "初階外匯人員")
        self.assertFalse(review)

    def test_fx_senior(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-fx-senior-2025-06")
        self.assertEqual(cid, "tabf-fx-senior")
        self.assertEqual(cname, "進階外匯人員")
        self.assertFalse(review)

    def test_credit(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-credit-2025-01")
        self.assertEqual(cid, "tabf-credit")
        self.assertEqual(cname, "授信人員")
        self.assertFalse(review)

    def test_risk_management(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-risk-management-2025-03")
        self.assertEqual(cid, "tabf-risk-management")
        self.assertEqual(cname, "風險管理基本能力")
        self.assertFalse(review)

    def test_debt_collection(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-debt-collection-2025-06")
        self.assertEqual(cid, "tabf-debt-collection")
        self.assertEqual(cname, "債權催收人員")
        self.assertFalse(review)

    def test_digital_finance(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-digital-finance-2025-01")
        self.assertEqual(cid, "tabf-digital-finance")
        self.assertEqual(cname, "數位金融知識與能力")
        self.assertFalse(review)

    def test_aml(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-aml-2025-03")
        self.assertEqual(cid, "tabf-aml")
        self.assertEqual(cname, "防制洗錢與打擊資恐")
        self.assertFalse(review)

    def test_fintech(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-fintech-2025-06")
        self.assertEqual(cid, "tabf-fintech")
        self.assertEqual(cname, "金融科技力知識")
        self.assertFalse(review)

    def test_asset_valuation(self) -> None:
        cid, cname, _, review = self._derive("tabf-cert-asset-valuation-2025-01")
        self.assertEqual(cid, "tabf-asset-valuation")
        self.assertEqual(cname, "資產評估人員")
        self.assertFalse(review)


class TiiCertCanonicalTests(unittest.TestCase):
    def _derive(self, source_exam_id: str) -> tuple[str, str, str, bool]:
        return _derive_canonical(source_exam_id, "", "", 2025, [])

    def test_life_insurance(self) -> None:
        cid, cname, _, review = self._derive("tii-cert-life-insurance-2025-03")
        self.assertEqual(cid, "tii-life-insurance")
        self.assertEqual(cname, "人身保險業務員")
        self.assertFalse(review)

    def test_property_insurance(self) -> None:
        cid, cname, _, review = self._derive("tii-cert-property-insurance-2025-06")
        self.assertEqual(cid, "tii-property-insurance")
        self.assertEqual(cname, "財產保險業務員")
        self.assertFalse(review)

    def test_investment_insurance(self) -> None:
        cid, cname, _, review = self._derive("tii-cert-investment-insurance-2025-01")
        self.assertEqual(cid, "tii-investment-insurance")
        self.assertEqual(cname, "投資型保險商品業務員")
        self.assertFalse(review)

    def test_health_insurance(self) -> None:
        cid, cname, _, review = self._derive("tii-cert-health-insurance-2025-03")
        self.assertEqual(cid, "tii-health-insurance")
        self.assertEqual(cname, "傷害保險及健康保險業務員")
        self.assertFalse(review)


if __name__ == "__main__":
    unittest.main()
