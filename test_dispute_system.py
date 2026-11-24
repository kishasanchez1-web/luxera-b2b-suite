import unittest
from decimal import Decimal
from dispute_system import RevenueProtectionSystem, money

class AuditTests(unittest.TestCase):
    def test_direction_and_missing(self):
        e = {"over":{"amount":"10"}, "under":{"amount":"20"}, "missing":{"amount":"30"}}
        a = {"over":{"amount":"12.50"}, "under":{"amount":"15"}, "extra":{"amount":"9"}}
        r = RevenueProtectionSystem().analyze_ledger_leaks(e,a)
        self.assertEqual(r["potential_overcharges"], Decimal("2.50"))
        self.assertEqual(len(r["flags"]),4)
    def test_invalid(self):
        for x in ("NaN","-1","1.001"):
            with self.assertRaises(ValueError):
                money(x)
    def test_equal(self):
        self.assertEqual(RevenueProtectionSystem().analyze_ledger_leaks({"a":{"amount":"1"}},{"a":{"amount":"1.00"}})["flags"], [])

if __name__ == "__main__":
    unittest.main()
