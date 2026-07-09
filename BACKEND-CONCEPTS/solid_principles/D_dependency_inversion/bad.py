"""
=============================================================
 D — Dependency Inversion Principle
 Project : Order Notification System
 File    : bad.py  ← VIOLATES DIP (only DIP, not SRP)
=============================================================

SETUP — SRP is already respected here:
  - EmailService    -> its own class, sends emails (one job)
  - OrderService    -> its own class, handles orders (one job)

  SRP is NOT the issue in this file.

THE ONLY PROBLEM — DIP is violated:
  OrderService HARDCODES its dependency on EmailService
  inside its own __init__.

  This means OrderService DECIDES for itself what to use.
  It is in control of its own dependency.

  Consequences:
    1. Want to notify via SMS instead?
       -> You MUST open OrderService and change it.

    2. Want to write a unit test without sending real emails?
       -> You CANNOT. Every test sends a real email.

    3. Want Email in production but SMS in staging?
       -> Impossible without editing OrderService.

  The problem is NOT that they are separate classes.
  The problem is HOW they are connected — hardcoded.
=============================================================
"""


# ── EmailService — SRP is fine, this class has one job ──────
class EmailService:
    """
    Responsible for sending emails only.
    One job. SRP is fine here.
    """
    def send(self, to: str, subject: str, message: str) -> None:
        print(f"  [EmailService] To      : {to}")
        print(f"  [EmailService] Subject : {subject}")
        print(f"  [EmailService] Message : {message}")


# ── OrderService — SRP is fine, but DIP is broken ───────────
class OrderService:
    """
    Responsible for order logic only.
    SRP is fine — it is not doing email work itself.

    BUT — DIP is violated.
    It hardcodes EmailService() inside __init__.
    OrderService CONTROLS its own dependency.
    It has decided: "I will always use email. No choice given."
    """

    def __init__(self):
        # ❌ THIS is the DIP violation.
        # OrderService is creating its own dependency.
        # The choice of EmailService is locked in here.
        # Nothing from outside can change this.
        self.notifier = EmailService()

    def place_order(self, customer: str, item: str) -> None:
        print(f"\n[OrderService] Placing order for '{item}'...")
        # OrderService delegates sending to EmailService — that's fine.
        # The problem is it had no choice in picking EmailService.
        self.notifier.send(
            to=customer,
            subject="Order Confirmed",
            message=f"Your order for '{item}' is placed!"
        )
        print(f"[OrderService] Order placed.")

    def cancel_order(self, customer: str, item: str) -> None:
        print(f"\n[OrderService] Cancelling order for '{item}'...")
        self.notifier.send(
            to=customer,
            subject="Order Cancelled",
            message=f"Your order for '{item}' has been cancelled."
        )
        print(f"[OrderService] Order cancelled.")


# ── Demo — showing what you CANNOT do ───────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  BAD — DIP Violated (SRP is already fine here)")
    print("=" * 55)

    # Works fine with email
    service = OrderService()
    service.place_order("alice@example.com", "iPhone 15")

    print()
    print("PROBLEM 1: Can you switch to SMS?")
    print("  -> No. You must open OrderService and change __init__.")
    print("  -> That means touching business logic to change infra.")

    print()
    print("PROBLEM 2: Can you test without real email being sent?")
    print("  -> No. Every time you call place_order, EmailService runs.")
    print("  -> There is no way to inject a fake/mock from outside.")

    print()
    print("PROBLEM 3: Different channels for prod vs staging?")
    print("  -> No. EmailService is hardcoded. No flexibility at all.")

    print()
    print("Root cause: OrderService controls its own dependency.")
    print("It was never GIVEN a notifier. It CREATED one itself.")
