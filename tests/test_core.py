"""在线时长档位奖励。"""
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

    def test_same_instant_tick_not_double_counted(self):
        book = Rewards([(1, 100)])
        self.assertTrue(book.tick("p", 1000, True))
        self.assertTrue(book.tick("p", 1000, True))
        self.assertEqual(book.played_ms("p"), 1000)

    def test_tick_rejects_earlier_time(self):
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        self.assertFalse(book.tick("p", 1000, True))
        self.assertEqual(book.played_ms("p"), 60000)

    def test_offline_tick_not_counted(self):
        book = Rewards([(1, 100)])
        book.tick("p", 60000, False)
        self.assertEqual(book.played_ms("p"), 0)

    def test_exact_minute_counts_as_reached(self):
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        self.assertEqual(book.claimable("p"), [0])

    def test_daily_claim_quota(self):
        book = Rewards([(1, 100), (2, 200), (3, 300)], max_claims=2)
        book.tick("p", 180000, True)
        self.assertTrue(book.claim("p", 0))
        self.assertTrue(book.claim("p", 1))
        self.assertFalse(book.claim("p", 2))
        self.assertEqual(book.claimed("p"), [0, 1])

    def test_duplicate_claim_rejected(self):
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        self.assertTrue(book.claim("p", 0))
        self.assertFalse(book.claim("p", 0))
        self.assertEqual(book.claimed("p"), [0])

    def test_claimable_lists_all_reached_tiers(self):
        book = Rewards([(1, 100), (2, 200), (3, 300)], max_claims=2)
        book.tick("p", 180000, True)
        self.assertEqual(book.claimable("p"), [0, 1, 2])

    def test_claimed_tier_leaves_claimable(self):
        book = Rewards([(1, 100), (2, 200)], max_claims=2)
        book.tick("p", 120000, True)
        book.claim("p", 0)
        self.assertEqual(book.claimable("p"), [1])

    def test_reset_day_only_on_new_day(self):
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        book.claim("p", 0)
        self.assertTrue(book.reset_day("p", 2))
        self.assertFalse(book.reset_day("p", 2))
        self.assertEqual(book.claimed("p"), [])
        self.assertEqual(book.played_ms("p"), 0)

    def test_scanned_not_proportional_to_queries(self):
        book = Rewards([(1, 100)])
        for index in range(3000):
            book.tick("p-%d" % index, 60000, True)
        for _ in range(3000):
            book.claimable("p-0")
        self.assertLessEqual(book.scanned_count(), 3000)


if __name__ == "__main__":
    unittest.main()
