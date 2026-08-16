"""Tests for the external-consensus gate.

These encode the failure modes we actually hit on the day: a single
unreproducible source, a figure dated after the release, the company's own
guidance sold as consensus, and last quarter's actual scraped as an estimate.
"""

import datetime as dt
import unittest

from agent.consensus import _usable

TODAY = dt.date(2026, 8, 16)
REPORTED = {"FY2026Q1": 3160.063, "FY2026Q2": 3623.465}


def src(value, source="X", as_of="2026-07-20", basis="quarterly adjusted"):
    return {"source": source, "value": value, "basis": basis, "as_of": as_of}


class TestConsensusGate(unittest.TestCase):
    def test_two_agreeing_sources_anchor(self):
        v, acc, rej = _usable([src(4.71, "Zacks"), src(4.73, "Barchart")],
                              "eps", TODAY, "quarterly")
        self.assertAlmostEqual(v, 4.72)
        # real HD data: four providers, one low outlier
        v4, _, _ = _usable([src(4.62), src(4.71), src(4.71), src(4.73)],
                           "eps", TODAY, "quarterly")
        self.assertAlmostEqual(v4, 4.71)
        self.assertEqual(len(acc), 2)

    def test_single_source_never_anchors(self):
        v, acc, rej = _usable([src(4.87, "ChartMill")], "eps", TODAY, "quarterly")
        self.assertIsNone(v)
        self.assertEqual(len(acc), 1)   # recorded, just not used

    def test_outlier_excluded_from_median(self):
        v, _, _ = _usable([src(4.71, "Zacks"), src(4.73, "Barchart"),
                           src(4.87, "ChartMill")], "eps", TODAY, "quarterly")
        # the lone 4.87 must not drag the anchor out of the tight cluster
        self.assertLessEqual(v, 4.75)

    def test_future_dated_rejected(self):
        v, acc, rej = _usable([src(4.71), src(9.99, as_of="2026-08-19")],
                              "eps", TODAY, "quarterly")
        self.assertIsNone(v)
        self.assertEqual(len(acc), 1)
        self.assertIn("future", rej[0]["reason"])

    def test_company_guidance_rejected(self):
        v, acc, rej = _usable(
            [src(3.30, "ADI", basis="company guidance, not Street consensus"),
             src(3.28, "Investing.com")], "eps", TODAY, "quarterly")
        self.assertIsNone(v)
        self.assertIn("guidance", rej[0]["reason"])

    def test_already_reported_actual_rejected(self):
        v, acc, rej = _usable([src(3620.0, "Investing.com"), src(3625.0, "Argus")],
                              "money", TODAY, "quarterly", REPORTED)
        self.assertIsNone(v)
        self.assertEqual(len(rej), 2)
        self.assertIn("already-reported", rej[0]["reason"])

    def test_full_year_against_quarter_rejected(self):
        v, acc, rej = _usable([src(15.01, basis="full-year"), src(4.71)],
                              "eps", TODAY, "quarterly")
        self.assertIsNone(v)
        self.assertIn("full-year", rej[0]["reason"])

    def test_company_compiled_consensus_stands_alone(self):
        v, acc, rej = _usable(
            [src(43.5, "Hays plc", basis="company-compiled consensus")],
            "money", TODAY, "full-year")
        self.assertEqual(v, 43.5)


if __name__ == "__main__":
    unittest.main()
