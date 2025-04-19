import unittest
from calculate_expected_stake import calculate_expected_stake

class TestCalculateExpectedStake(unittest.TestCase):
    def test_basic_calculation(self):
        """基本的な計算のテスト"""
        # bond = 1000 SOL, bid = 1000 CPMPE
        # bid_pmpe = 1000 / 1000 = 1
        # stake_cap = 1000 / (1 + 1) = 500
        result = calculate_expected_stake(bond=1000, bid=1000)
        self.assertAlmostEqual(result, 500, places=2)

    def test_zero_bid(self):
        """入札額が0の場合のテスト"""
        # bond = 1000 SOL, bid = 0 CPMPE
        # bid_pmpe = 0
        # stake_cap = 1000 / (0 + 0) = ∞
        with self.assertRaises(ZeroDivisionError):
            calculate_expected_stake(bond=1000, bid=0)

    def test_large_numbers(self):
        """大きな数値でのテスト"""
        # bond = 10000 SOL, bid = 5000 CPMPE
        # bid_pmpe = 5000 / 1000 = 5
        # stake_cap = 10000 / (5 + 5) = 1000
        result = calculate_expected_stake(bond=10000, bid=5000)
        self.assertAlmostEqual(result, 1000, places=2)

    def test_small_numbers(self):
        """小さな数値でのテスト"""
        # bond = 100 SOL, bid = 100 CPMPE
        # bid_pmpe = 100 / 1000 = 0.1
        # stake_cap = 100 / (0.1 + 0.1) = 500
        result = calculate_expected_stake(bond=100, bid=100)
        self.assertAlmostEqual(result, 500, places=2)

    def test_real_world_example(self):
        """実際のデータに近い値でのテスト"""
        # bond = 5000 SOL, bid = 2500 CPMPE
        # bid_pmpe = 2500 / 1000 = 2.5
        # stake_cap = 5000 / (2.5 + 2.5) = 1000
        result = calculate_expected_stake(bond=5000, bid=2500)
        self.assertAlmostEqual(result, 1000, places=2)

if __name__ == '__main__':
    unittest.main() 