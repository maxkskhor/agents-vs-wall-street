"""Validation-gate tests (deterministic gates only, red_team disabled)."""

import unittest

from agent.config import get_company
from agent.runlog import RunLog, new_run_id
from agent.validate import validate


def _log():
    return RunLog(new_run_id() + "-test")


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.hd = get_company("HD")
        self.series = {
            "net_sales": {"FY2025Q2": 45300},
            "adj_eps": {"FY2025Q2": 4.67},
            "comp_sales": {"FY2025Q2": 0.8},
        }

    def test_sane_forecast_passes(self):
        finals = {"net_sales": 46700, "adj_eps": 4.7, "comp_sales": 1.2}
        rep = validate(self.hd, "FY2026Q2", finals, self.series, {}, _log(),
                       red_team=False)
        self.assertTrue(rep.ok, [c for c in rep.checks if c.status == "fail"])

    def test_billions_vs_millions_blocks(self):
        finals = {"net_sales": 46.7, "adj_eps": 4.7, "comp_sales": 1.2}
        rep = validate(self.hd, "FY2026Q2", finals, self.series, {}, _log(),
                       red_team=False)
        self.assertFalse(rep.ok)

    def test_percent_as_fraction_blocks(self):
        # comps forecast 8pp above prior year is implausible for HD
        finals = {"net_sales": 46700, "adj_eps": 4.7, "comp_sales": 9.0}
        rep = validate(self.hd, "FY2026Q2", finals, self.series, {}, _log(),
                       red_team=False)
        self.assertFalse(rep.ok)

    def test_comp_vs_sales_growth_consistency(self):
        # 20% sales growth with -1% comps: inconsistent
        finals = {"net_sales": 54400, "adj_eps": 4.7, "comp_sales": -1.0}
        rep = validate(self.hd, "FY2026Q2", finals, self.series, {}, _log(),
                       red_team=False)
        self.assertFalse(rep.ok)

    def test_hays_conversion_ratio(self):
        has = get_company("HAS")
        series = {"net_fees": {"FY2025": 1050}, "preex_eps": {"FY2025": 6.4},
                  "preex_op": {"FY2025": 105}}
        # operating profit of 60% of net fees is impossible for a recruiter
        finals = {"net_fees": 1000, "preex_eps": 6.0, "preex_op": 600}
        rep = validate(has, "FY2026", finals, series, {}, _log(), red_team=False)
        self.assertFalse(rep.ok)

    def test_missing_prior_year_fails_closed(self):
        finals = {"net_sales": 46700, "adj_eps": 4.7, "comp_sales": 1.2}
        rep = validate(self.hd, "FY2026Q2", finals,
                       {"net_sales": {}, "adj_eps": {}, "comp_sales": {}},
                       {}, _log(), red_team=False)
        self.assertFalse(rep.ok)


if __name__ == "__main__":
    unittest.main()
