import unittest

import pandas as pd

from utils import prep

COLS = ["id", "code_commune", "commune", "code_epci", "epci", "code_dep", "dep", "code_reg", "ept", "petr",
        "code_pnr", "pnr", "type", "debut", "fin", "arrete"]


def row(i, commune="01001", typ="Inondations", debut="2020-01-01 00:00:00.000", fin="2020-01-02 00:00:00.000",
        arrete="2020-02-01 00:00:00.000", reg="84"):
    return [str(i), commune, "X", "e", "E", "01", "Ain", reg, None, None, None, None, typ, debut, fin, arrete]


class PrepTests(unittest.TestCase):
    def test_duplicates_removed(self):
        raw = pd.DataFrame([row(1), row(2), row(3, commune="01002")], columns=COLS)
        df, q = prep.clean(raw)
        self.assertEqual(q["duplicates"], 1)
        self.assertEqual(len(df), 2)

    def test_shifted_midnight_fixed(self):
        raw = pd.DataFrame([row(1, debut="2023-03-31 02:00:00.000", fin="2023-06-29 02:00:00.000",
                                arrete="2024-09-23 01:00:00.000")], columns=COLS)
        df, q = prep.clean(raw)
        self.assertEqual(df.loc[0, "debut"], pd.Timestamp("2023-04-01"))
        self.assertEqual(df.loc[0, "fin"], pd.Timestamp("2023-06-30"))
        self.assertEqual(df.loc[0, "arrete"], pd.Timestamp("2024-09-24"))
        self.assertEqual(q["shifted_timestamps"], 3)

    def test_region_padding_and_names(self):
        raw = pd.DataFrame([row(1, reg="1")], columns=COLS)
        df, _ = prep.clean(raw)
        self.assertEqual(str(df.loc[0, "region"]), "Guadeloupe")

    def test_rga_merge(self):
        raw = pd.DataFrame([row(1, typ="Retrait-gonflement des argiles")], columns=COLS)
        df, _ = prep.clean(raw)
        self.assertEqual(str(df.loc[0, "type"]), "Clay shrink-swell")
        self.assertEqual(str(df.loc[0, "type_merged"]), "Drought")

    def test_peril_translated(self):
        raw = pd.DataFrame([row(1)], columns=COLS)
        df, _ = prep.clean(raw)
        self.assertEqual(str(df.loc[0, "type"]), "Floods")

    def test_event_id_groups_communes(self):
        raw = pd.DataFrame([row(1), row(2, commune="01002")], columns=COLS)
        df, q = prep.clean(raw)
        self.assertEqual(q["n_events"], 1)


if __name__ == "__main__":
    unittest.main()
