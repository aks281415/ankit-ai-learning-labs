"""
=============================================================
 O — Open / Closed Principle
 Project : Payment Gateway
 File    : bad.py  ← VIOLATES OCP
=============================================================

PROBLEM:
  `PaymentProcessor.pay()` uses a giant if/elif chain to
  decide which payment method to use.

  Every time the business adds a new payment method
  (UPI, Crypto, BNPL, Wallet...) a developer MUST:
    1. Open this file
    2. Add another elif branch
    3. Re-test ALL existing payment methods (regression risk!)

  The class is NOT closed for modification.
  It is being modified every time we "extend" the system.

  Over time this method becomes hundreds of lines long,
  impossible to read, and a source of constant bugs.
=============================================================
"""


class PaymentProcessor:
    """
    [X] Violates OCP.
    Every new payment type requires editing this class.
    """

    def pay(self, method: str, amount: float, details: dict) -> str:
        """
        [X] This if/elif chain grows forever.
        Adding 'crypto' means opening and modifying tested code.
        """
        if method == "credit_card":
            # Credit card processing logic
            card_number = details.get("card_number", "****")
            print(f"[PaymentProcessor] Processing credit card: {card_number}")
            print(f"[PaymentProcessor] Charging Rs.{amount} to card...")
            return f"[OK] Credit Card payment of Rs.{amount} successful."

        elif method == "upi":
            # UPI processing logic
            upi_id = details.get("upi_id", "unknown@upi")
            print(f"[PaymentProcessor] Sending UPI request to {upi_id}")
            print(f"[PaymentProcessor] Awaiting UPI confirmation for Rs.{amount}...")
            return f"[OK] UPI payment of Rs.{amount} to {upi_id} successful."

        elif method == "net_banking":
            # Net banking logic
            bank = details.get("bank", "Unknown Bank")
            print(f"[PaymentProcessor] Redirecting to {bank} net banking portal")
            print(f"[PaymentProcessor] Processing Rs.{amount} via net banking...")
            return f"[OK] Net Banking payment of Rs.{amount} via {bank} successful."

        # [X] To add crypto, we MUST edit here — breaking OCP
        # elif method == "crypto":
        #     ...   ← this goes on forever

        else:
            raise ValueError(f"Unknown payment method: {method}")


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  BAD EXAMPLE — OCP Violation (Payment Gateway)")
    print("=" * 55)

    processor = PaymentProcessor()

    result1 = processor.pay("credit_card", 1500.0, {"card_number": "4111-1111-1111-1111"})
    print(result1, "\n")

    result2 = processor.pay("upi", 500.0, {"upi_id": "alice@okaxis"})
    print(result2, "\n")

    result3 = processor.pay("net_banking", 2000.0, {"bank": "HDFC"})
    print(result3, "\n")

    print("""
WHY THIS IS BAD:
  - Every new payment method = edit PaymentProcessor
  - The if/elif chain grows without limit
  - All existing methods are at risk every time you add one
  - You cannot add a payment method without touching
    already-deployed, tested code
  - Hard to unit test individual payment methods in isolation
""")
