import unittest

from playtime.core import Rewards


class PlaytimeTest(unittest.TestCase):
    def test_played_starts_at_zero(self):
        self.assertEqual(Rewards([(1, 100)]).played_ms("p"), 0)

    def test_unknown_player_has_nothing_claimable(self):
        self.assertEqual(Rewards([(1, 100)]).claimable("nobody"), [])

    def test_claim_records_tier(self):
        book = Rewards([(1, 100)])
        self.assertTrue(book.claim("p", 0))
        self.assertEqual(book.claimed("p"), [0])

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Rewards([(1, 100)]).scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
