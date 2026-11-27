"""Offline ledger reconciliation; discrepancies are not recovered funds."""
import argparse
import csv
import html
from decimal import Decimal, InvalidOperation
from pathlib import Path

def money(value):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or n < 0 or n != n.quantize(Decimal("0.01")):
            raise ValueError("Amounts must be nonnegative finite cents")
        return n
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc

def load_ledger(path):
    result = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not {"tx_id", "amount"} <= set(reader.fieldnames or []):
            raise ValueError("CSV requires tx_id and amount")
        for row in reader:
            key = row["tx_id"].strip()
            if not key or key in result:
                raise ValueError("Blank or duplicate transaction ID")
            result[key] = {"amount": money(row["amount"])}
    return result

class RevenueProtectionSystem:
    def analyze_ledger_leaks(self, expected_ledger, actual_ledger):
        flags = []
        total = Decimal("0")
        for key in sorted(set(expected_ledger) | set(actual_ledger)):
            expected = money(expected_ledger[key]["amount"]) if key in expected_ledger else None
            actual = money(actual_ledger[key]["amount"]) if key in actual_ledger else None
            if expected == actual:
                continue
            if expected is None:
                reason, candidate = "Unmatched actual charge; verify authorization", Decimal("0")
            elif actual is None:
                reason, candidate = "Missing actual record; investigate", Decimal("0")
            elif actual > expected:
                reason, candidate = "Potential overcharge; verify contract", actual - expected
            else:
                reason, candidate = "Actual below expected; investigate", Decimal("0")
            total += candidate
            flags.append({"tx_id": key, "reason": reason, "expected": expected, "actual": actual, "potential_overcharge": candidate})
        return {"potential_overcharges": total, "flags": flags}

    def compile_dispute_dashboard(self, audit_results, output_path="dispute.html"):
        def cell(value):
            return "<td>" + html.escape("" if value is None else str(value)) + "</td>"
        rows = "".join("<tr>" + "".join(cell(f[k]) for k in ("tx_id","reason","expected","actual","potential_overcharge")) + "</tr>" for f in audit_results["flags"])
        total = audit_results["potential_overcharges"]
        page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Luxera Revenue Audit</title><style>body{{font:16px system-ui;color:#222;max-width:1100px;margin:auto;padding:24px}}h1{{color:#9b2860}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border-bottom:1px solid #c5a059;text-align:left}}.scroll{{overflow:auto}}</style><h1>Luxera Solutions | Revenue Audit</h1><p>Potential overcharges: {total:.2f}. Not recovered funds. Single-currency reconciliation; confirm contract terms and records before disputing.</p><div class="scroll"><table><thead><tr><th>Transaction</th><th>Finding</th><th>Expected</th><th>Actual</th><th>Potential overcharge</th></tr></thead><tbody>{rows}</tbody></table></div></html>"""
        Path(output_path).write_text(page, encoding="utf-8")

def self_check():
    expected = {"over":{"amount":"10"}, "under":{"amount":"20"}, "missing":{"amount":"30"}}
    actual = {"over":{"amount":"12.50"}, "under":{"amount":"15"}, "extra":{"amount":"9"}}
    result = RevenueProtectionSystem().analyze_ledger_leaks(expected, actual)
    if result["potential_overcharges"] != Decimal("2.50") or len(result["flags"]) != 4:
        raise SystemExit("Revenue audit self-check failed")
    print("Revenue audit self-check passed. Provide expected and actual CSV files to run a real audit.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("expected", nargs="?")
    p.add_argument("actual", nargs="?")
    p.add_argument("--output", default="dispute.html")
    a = p.parse_args()
    if not a.expected and not a.actual:
        self_check()
        return
    if not a.expected or not a.actual:
        p.error("expected and actual CSV files must be provided together")
    engine = RevenueProtectionSystem()
    engine.compile_dispute_dashboard(engine.analyze_ledger_leaks(load_ledger(a.expected), load_ledger(a.actual)), a.output)

if __name__ == "__main__":
    main()
