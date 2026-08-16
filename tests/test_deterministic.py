"""Tests for every path that must work without API keys: period math, the
statistical estimator, guidance arithmetic, quote grounding, combination and
the workbook writer. Run: .venv/bin/python -m unittest discover -s tests"""

import unittest

from agent import periods
from agent.config import get_company, load_companies
from agent.engine import combine_methods, weighted_mean, weighted_median
from agent.estimators import statistical, guidance, _fy_catchup_money
from agent.extract import Fact, _value_in_quote, _quote_in_doc
from agent.workbook import write_workbook, WorkbookError

SERIES = {"FY2024Q1": 39900, "FY2024Q2": 43200, "FY2024Q3": 40200, "FY2024Q4": 34800,
          "FY2025Q1": 39856, "FY2025Q2": 45300, "FY2025Q3": 41352, "FY2025Q4": 39704,
          "FY2026Q1": 41765}


class TestPeriods(unittest.TestCase):
    def test_parse_and_shift(self):
        self.assertEqual(periods.parse("FY2026Q2"), (2026, "Q", 2))
        self.assertEqual(periods.parse("FY2026"), (2026, "Y", None))
        self.assertEqual(periods.parse("FY2026H1"), (2026, "H", 1))
        self.assertEqual(periods.prior_year("FY2026Q2"), "FY2025Q2")
        self.assertEqual(periods.shift_quarters("FY2026Q1", -1), "FY2025Q4")
        self.assertEqual(periods.shift_quarters("FY2025Q4", 1), "FY2026Q1")

    def test_bad_period(self):
        with self.assertRaises(ValueError):
            periods.parse("Q1 2026")


class TestEstimators(unittest.TestCase):
    def setUp(self):
        hd = get_company("HD")
        self.net_sales, self.eps, self.comp = hd.metrics

    def test_statistical_money(self):
        e = statistical(self.net_sales, SERIES, "FY2026Q2")
        self.assertTrue(45000 < e.value < 49500)
        self.assertEqual(e.inputs["base_period"], "FY2025Q2")

    def test_statistical_abstains_without_base(self):
        self.assertIsNone(statistical(self.net_sales, {"FY2023Q2": 1.0}, "FY2026Q2"))

    def test_fy_catchup(self):
        got = _fy_catchup_money(SERIES, "FY2026Q2", 3.5)
        # implied FY total spread over remaining quarters, scaled by prior Q2
        self.assertAlmostEqual(got["value"], 46701, delta=2)

    def test_guidance_growth_range(self):
        f = Fact(metric="net_sales", fact_type="guidance", period="FY2026",
                 value=None, low=2.5, high=4.5, units="% growth",
                 doc_id="d", published="2026-05-19",
                 quote="Total sales growth of approximately 2.5% to 4.5%")
        g = guidance(self.net_sales, SERIES, [f], "FY2026Q2")
        self.assertIsNotNone(g)
        self.assertTrue(45000 < g.value < 49000)

    def test_guidance_direct_period(self):
        f = Fact(metric="net_sales", fact_type="preannounce", period="FY2026Q2",
                 value=46000, low=None, high=None, units="USDm",
                 doc_id="d", published="2026-07-10", quote="net sales of $46,000 million")
        g = guidance(self.net_sales, SERIES, [f], "FY2026Q2")
        self.assertEqual(g.value, 46000)


class TestGrounding(unittest.TestCase):
    def test_value_matching(self):
        self.assertTrue(_value_in_quote(41800, "sales of $41.8 billion"))
        self.assertTrue(_value_in_quote(41765, "| Net sales | $ 41,765 |"))
        self.assertTrue(_value_in_quote(0.6, "comparable sales increased 0.6%"))
        self.assertTrue(_value_in_quote(6.2, "basic earnings per share of 6.2p"))
        self.assertFalse(_value_in_quote(9999, "sales of $41.8 billion"))

    def test_quote_in_doc(self):
        doc = "Some text.  Net sales   were $41.8 billion.\nMore."
        self.assertTrue(_quote_in_doc("Net sales were $41.8 billion.", doc))
        self.assertFalse(_quote_in_doc("Invented quote entirely.", doc))


class TestEngine(unittest.TestCase):
    def test_weighted_median(self):
        self.assertEqual(weighted_median([(1, .2), (2, .5), (10, .3)]), 2)
        self.assertEqual(weighted_median([(5, 1.0)]), 5)

    def test_weighted_mean(self):
        self.assertAlmostEqual(weighted_mean([(100, .5), (200, .3), (300, .2)]), 170)
        # weights renormalise over the methods present
        self.assertAlmostEqual(weighted_mean([(100, .5), (200, .3)]), 137.5)

    def test_combine_methods_by_kind(self):
        # money/eps blend continuously: a shifted input moves the answer
        base, _ = combine_methods("money", [(4009.2, .5), (3900, .3), (3691, .2)])
        raw, _ = combine_methods("money", [(3900.0, .5), (3900, .3), (3691, .2)])
        self.assertGreater(base, raw)   # the bias correction is reachable
        # percent still selects by weighted median
        v, how = combine_methods("percent", [(1.13, .4), (1.0, .3), (2.2, .3)])
        self.assertEqual(v, 1.13)
        self.assertIn("median", how)

    def test_two_estimator_mean_not_winner_take_all(self):
        # the old median handed a 2-way tie to the heavier weight verbatim
        v, _ = combine_methods("money", [(323.1, .2), (330.0, .3)])
        self.assertTrue(323.1 < v < 330.0)


class TestWorkbook(unittest.TestCase):
    def test_writes_all_templates(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            for c in load_companies():
                out = write_workbook(c, {m.label: 1.23 for m in c.metrics},
                                     out_dir=Path(td))
                self.assertTrue(out.exists())

    def test_rejects_missing_metric(self):
        c = get_company("HD")
        with self.assertRaises(WorkbookError):
            write_workbook(c, {"Net sales": 1.0})


if __name__ == "__main__":
    unittest.main()
