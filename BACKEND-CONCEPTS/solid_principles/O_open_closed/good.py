"""
=============================================================
 O — Open / Closed Principle
 Project : Payment Gateway
 File    : good.py  ← FOLLOWS OCP
=============================================================

SOLUTION:
  Define an abstract base class `PaymentMethod` that declares
  the contract (the `pay()` method).

  Each payment type becomes its OWN class that extends
  `PaymentMethod`. To add a new method (e.g., Crypto),
  you simply ADD a new class — you never touch existing code.

  `PaymentProcessor` (the orchestrator / checkout) is
  CLOSED for modification — it never changes.
  The system is OPEN for extension — new payment types
  are added as new classes.

HOW PYTHON ACHIEVES THIS:
  - Abstract Base Classes (abc.ABC + @abstractmethod)
  - Alternatively: typing.Protocol (duck-typed, no inheritance)
  Both are shown here.
=============================================================
"""

from abc import ABC, abstractmethod
from typing import Dict


# -- Abstract contract ----------------------------------------
class PaymentMethod(ABC):
    """
    [OK] This is the abstraction — the closed, stable interface.
    PaymentProcessor depends ONLY on this, never on
    concrete payment classes.
    """

    @abstractmethod
    def pay(self, amount: float, details: Dict) -> str:
        """
        Every payment method MUST implement this.
        Returns a result message.
        """
        ...


# -- Concrete implementations — each is a separate class -----

class CreditCardPayment(PaymentMethod):
    """
    [OK] Closed: This class only changes if credit card
    processing logic changes — nothing else.
    """

    def pay(self, amount: float, details: Dict) -> str:
        card_number = details.get("card_number", "****")
        print(f"  [CreditCard] Processing card: {card_number}")
        print(f"  [CreditCard] Charging Rs.{amount}...")
        return f"[OK] Credit Card payment of Rs.{amount} successful."


class UPIPayment(PaymentMethod):
    """
    [OK] Closed: Only changes if UPI logic changes.
    Adding UPI did NOT require touching CreditCardPayment.
    """

    def pay(self, amount: float, details: Dict) -> str:
        upi_id = details.get("upi_id", "unknown@upi")
        print(f"  [UPI] Sending request to {upi_id}")
        print(f"  [UPI] Awaiting confirmation for Rs.{amount}...")
        return f"[OK] UPI payment of Rs.{amount} to {upi_id} successful."


class NetBankingPayment(PaymentMethod):
    """[OK] Only changes if net banking logic changes."""

    def pay(self, amount: float, details: Dict) -> str:
        bank = details.get("bank", "Unknown Bank")
        print(f"  [NetBanking] Redirecting to {bank} portal")
        print(f"  [NetBanking] Processing Rs.{amount}...")
        return f"[OK] Net Banking payment of Rs.{amount} via {bank} successful."


# [OK] NEW method added LATER — zero existing code was changed!
class CryptoPayment(PaymentMethod):
    """
    [OK] Added months after launch.
    PaymentProcessor, CreditCardPayment, UPIPayment —
    NONE of them were touched. System extended, not modified.
    """

    def pay(self, amount: float, details: Dict) -> str:
        wallet = details.get("wallet", "unknown_wallet")
        coin   = details.get("coin", "BTC")
        print(f"  [Crypto] Sending {coin} from wallet: {wallet}")
        print(f"  [Crypto] Processing Rs.{amount} equivalent in {coin}...")
        return f"[OK] Crypto payment of Rs.{amount} in {coin} successful."


# [OK] Another new method — still no old code touched!
class WalletPayment(PaymentMethod):
    """Paytm / PhonePe style wallet payment."""

    def pay(self, amount: float, details: Dict) -> str:
        wallet_id = details.get("wallet_id", "unknown")
        print(f"  [Wallet] Deducting from wallet: {wallet_id}")
        return f"[OK] Wallet payment of Rs.{amount} from {wallet_id} successful."


# -- Orchestrator — NEVER changes ----------------------------
class PaymentProcessor:
    """
    [OK] This class is CLOSED for modification.
    It works with ANY PaymentMethod — present or future —
    because it depends only on the abstraction.

    When Crypto or Wallet were added, this class was
    NOT touched at all.
    """

    def process(self, method: PaymentMethod, amount: float, details: Dict) -> str:
        print(f"\n[PaymentProcessor] Starting payment of Rs.{amount}...")
        result = method.pay(amount, details)       # polymorphism at work
        print(f"[PaymentProcessor] {result}")
        return result


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  GOOD EXAMPLE — OCP Followed (Payment Gateway)")
    print("=" * 55)

    processor = PaymentProcessor()

    # Original payment methods
    processor.process(
        CreditCardPayment(), 1500.0,
        {"card_number": "4111-1111-1111-1111"}
    )
    processor.process(
        UPIPayment(), 500.0,
        {"upi_id": "alice@okaxis"}
    )
    processor.process(
        NetBankingPayment(), 2000.0,
        {"bank": "HDFC"}
    )

    # New methods — PaymentProcessor was NOT changed!
    processor.process(
        CryptoPayment(), 3000.0,
        {"wallet": "1A2B3C4D", "coin": "ETH"}
    )
    processor.process(
        WalletPayment(), 800.0,
        {"wallet_id": "paytm_alice123"}
    )

    print("""
WHY THIS IS GOOD:
  - PaymentProcessor never changes, no matter how many
    payment methods are added.
  - Each payment method is an isolated, testable class.
  - Adding Crypto or Wallet = writing a NEW class only.
  - No regression risk on existing, deployed code.
  - PaymentProcessor is OPEN for extension via new classes,
    CLOSED for modification of its own logic.
""")
