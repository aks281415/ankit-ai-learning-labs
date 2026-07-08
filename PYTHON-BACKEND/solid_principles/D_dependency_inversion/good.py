"""
=============================================================
 D — Dependency Inversion Principle
 Project : Order Notification System
 File    : good.py  ← FIXES ONLY the DIP problem
=============================================================

WHAT CHANGED FROM bad.py:
  Only ONE thing changed in OrderService:

    BEFORE:
        def __init__(self):
            self.notifier = EmailService()   # hardcoded

    AFTER:
        def __init__(self, notifier):        # received from outside
            self.notifier = notifier

  That single change is Dependency Injection.
  OrderService no longer controls what it uses.
  The caller decides and passes it in.

WHAT DID NOT CHANGE:
  - EmailService is still its own class (SRP was already fine)
  - OrderService still has only one job (SRP still fine)
  - No extra layers, no over-engineering

THE BENEFIT:
  Now the caller can pass in ANY notifier:
    - EmailService   -> for production
    - SMSService     -> for mobile users
    - MockNotifier   -> for unit tests (no real sends)
  OrderService does not care which one it gets.
  It just calls .send() on whatever it receives.

This is called Dependency INVERSION because:
  Before: OrderService ---controls---> EmailService
  After:  Both depend on the same interface (abstraction)
          Caller decides what flows in
=============================================================
"""

from typing import Protocol


# ══════════════════════════════════════════════════════════════
#  The Abstraction — what OrderService depends on
#  (instead of depending on a concrete class)
# ══════════════════════════════════════════════════════════════

class Notifier(Protocol):
    """
    A simple contract.
    Any class that has a .send() method satisfies this.
    OrderService only knows about this — nothing else.
    """
    def send(self, to: str, subject: str, message: str) -> None: ...


# ══════════════════════════════════════════════════════════════
#  Concrete implementations — each is its own class (SRP fine)
#  All of them honour the Notifier contract above.
# ══════════════════════════════════════════════════════════════

class EmailService:
    """Sends email notifications. One job."""
    def send(self, to: str, subject: str, message: str) -> None:
        print(f"  [EmailService] To      : {to}")
        print(f"  [EmailService] Subject : {subject}")
        print(f"  [EmailService] Message : {message}")


class SMSService:
    """Sends SMS notifications. One job."""
    def send(self, to: str, subject: str, message: str) -> None:
        print(f"  [SMSService] Phone   : {to}")
        print(f"  [SMSService] Message : [{subject}] {message}")


class MockNotifier:
    """
    Used in unit tests.
    Does NOT send anything real.
    Just records what was sent so you can assert on it.
    """
    def __init__(self):
        self.calls = []   # stores every send() call made

    def send(self, to: str, subject: str, message: str) -> None:
        self.calls.append({"to": to, "subject": subject, "message": message})
        print(f"  [MockNotifier] Recorded (no real send): subject='{subject}'")


# ══════════════════════════════════════════════════════════════
#  OrderService — the ONLY change from bad.py is in __init__
# ══════════════════════════════════════════════════════════════

class OrderService:
    """
    Handles order logic. One job. SRP fine.

    The only difference from bad.py:
      __init__ now RECEIVES a notifier instead of CREATING one.
      This is constructor injection — the most common DIP pattern.
    """

    def __init__(self, notifier: Notifier):
        # notifier is passed in from outside.
        # OrderService has no idea if it's Email, SMS, or Mock.
        # It just uses whatever it receives.
        self.notifier = notifier

    def place_order(self, customer: str, item: str) -> None:
        print(f"\n[OrderService] Placing order for '{item}'...")
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


# ── Demo — showing what you CAN do now ──────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  GOOD — DIP Fixed (only DIP, one change in __init__)")
    print("=" * 55)

    # ── Scenario 1: Use Email in production ─────────────────
    print("\n--- Scenario 1: Production (Email) ---")
    service = OrderService(notifier=EmailService())
    service.place_order("alice@example.com", "iPhone 15")

    # ── Scenario 2: Swap to SMS — OrderService NOT touched ──
    print("\n--- Scenario 2: Swap to SMS (OrderService unchanged) ---")
    service = OrderService(notifier=SMSService())
    service.place_order("+91-9876543210", "MacBook Pro")

    # ── Scenario 3: Unit test — zero real emails/SMS sent ───
    print("\n--- Scenario 3: Unit Test (MockNotifier) ---")
    mock = MockNotifier()
    service = OrderService(notifier=mock)
    service.place_order("test@example.com", "AirPods")
    service.cancel_order("test@example.com", "AirPods")

    # Now you can assert on what was sent — no real side effects
    print(f"\n  Total notifications recorded : {len(mock.calls)}")
    print(f"  First subject                : '{mock.calls[0]['subject']}'")
    print(f"  Second subject               : '{mock.calls[1]['subject']}'")

    print()
    print("What changed from bad.py?")
    print("  ONE LINE in __init__:")
    print("    BEFORE: self.notifier = EmailService()  # hardcoded")
    print("    AFTER : self.notifier = notifier        # injected")
    print()
    print("That is Dependency Injection.")
