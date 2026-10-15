import json
import os

class RevenueProtectionSystem:
    def __init__(self):
        print("[Initialization] Luxera Solutions: Supplier Dispute Audit Engine Active.")

    def analyze_ledger_leaks(self, expected_ledger, actual_ledger):
        """
        Audits incoming vendor transactions against expected wholesale data points to catch billing gaps.
        """
        discrepancies = []
        total_recovered_leakage = 0.0

        for tx_id, expected_data in expected_ledger.items():
            if tx_id not in actual_ledger:
                leak = expected_data["amount"]
                discrepancies.append({
                    "tx_id": tx_id,
                    "reason": "Missing transaction record completely",
                    "amount_leaked": leak
                })
                total_recovered_leakage += leak
            else:
                actual_amount = actual_ledger[tx_id]["amount"]
                if expected_data["amount"] != actual_amount:
                    leak = abs(expected_data["amount"] - actual_amount)
                    discrepancies.append({
                        "tx_id": tx_id,
                        "reason": f"Wholesale pricing mismatch. Expected: {expected_data['amount']}, Charged: {actual_amount}",
                        "amount_leaked": leak
                    })
                    total_recovered_leakage += leak

        print(f"[Audit Concluded] Identified {len(discrepancies)} operational leakage flags.")
        return {"total_leakage_recovered": total_recovered_leakage, "flags": discrepancies}

    def compile_dispute_dashboard(self, audit_results, output_path="dispute.html"):
        """
        Compiles structural JSON results into a beautiful, customer-ready HTML dashboard template.
        """
        rows_html = ""
        for flag in audit_results["flags"]:
            rows_html += f"""
            <tr>
                <td style='padding:12px; border-bottom:1px solid #eee;'>{flag['tx_id']}</td>
                <td style='padding:12px; border-bottom:1px solid #eee; color:#d9534f;'>{flag['reason']}</td>
                <td style='padding:12px; border-bottom:1px solid #eee; font-weight:bold;'>${flag['amount_leaked']:.2f}</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Luxera Solutions - Revenue Protection Audit</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color:#f9f9f9; margin:0; padding:40px; }}
                .card {{ max-width:800px; margin:0 auto; background:#fff; padding:30px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.05); }}
                .header {{ border-bottom:3px solid #FF1493; padding-bottom:15px; margin-bottom:20px; }}
                h2 {{ color:#111; margin:0; font-size:24px; }}
                .summary {{ font-size:18px; font-weight:bold; color:#FF1493; margin-bottom:20px; }}
                table {{ width:100%; border-collapse:collapse; text-align:left; }}
                th {{ padding:12px; background-color:#111; color:#fff; font-size:14px; text-transform:uppercase; }}
            </style>
        </head>
        <body>
            <div class='card'>
                <div class='header'>
                    <h2>LUXERA SOLUTIONS &bull; REVENUE PROTECTION</h2>
                </div>
                <div class='summary'>Total Recoverable Asset Leakage: ${audit_results['total_leakage_recovered']:.2f}</div>
                <table>
                    <thead>
                        <tr><th>Transaction ID</th><th>Audit Dispute Reason</th><th>Recoverable Amount</th></tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[File Engine Generated] Dashboard template saved locally to: {output_path}")


# Local verification execution loop
if __name__ == "__main__":
    expected = {
        "TXN_9901": {"amount": 450.00},
        "TXN_9902": {"amount": 1200.00}
    }
    actual = {
        "TXN_9901": {"amount": 450.00},
        "TXN_9902": {"amount": 1150.00}  # Leaking $50 on wholesale charge
    }
    
    system = RevenueProtectionSystem()
    results = system.analyze_ledger_leaks(expected, actual)
    system.compile_dispute_dashboard(results)
