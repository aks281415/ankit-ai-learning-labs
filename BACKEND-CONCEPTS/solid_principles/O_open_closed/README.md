# O — Open / Closed Principle
## Project: Payment Gateway

---

### What is OCP?

> **Software entities should be open for extension but closed for modification.**

You should be able to add new behaviour to a system **without editing existing code**. Existing, tested code should remain untouched.

---

### The Problem (`bad.py`)

`PaymentProcessor.pay()` uses an `if/elif` chain:

```python
if method == "credit_card": ...
elif method == "upi": ...
elif method == "net_banking": ...
# Adding crypto? Must edit here -> OCP violated!
```

**Every new payment method requires opening and editing this file.** This risks breaking all the existing payment logic already in production.

---

### The Fix (`good.py`)

Define an abstract contract `PaymentMethod` with a `pay()` method.

Each payment type becomes its own class:

```
PaymentMethod (abstract)
    ├── CreditCardPayment
    ├── UPIPayment
    ├── NetBankingPayment
    ├── CryptoPayment      ← added later, zero old code touched
    └── WalletPayment      ← added later, zero old code touched
```

`PaymentProcessor` depends only on the abstraction — it **never changes**, no matter how many payment types are added.

---

### How to Run

```bash
python bad.py    # See the growing if/elif chain
python good.py   # See polymorphism — no if/elif at all
```

---

### Real-World Usage

- **Stripe SDK** — Each `PaymentIntent`, `Charge`, `SetupIntent` follows the same base interface. You add new payment types as classes, not as if/elif branches.
- **Django Authentication Backends** — Add custom auth (OAuth, LDAP) by writing a new backend class. Django's `authenticate()` function never changes.
- **Python `logging` module** — `FileHandler`, `StreamHandler`, `SocketHandler` all extend `logging.Handler`. Adding a new handler never modifies the `Logger` class.

---

### Key Rule

If you find yourself writing `if type == "X": ... elif type == "Y":` — that is almost always an OCP violation. Replace it with an abstract class and subclasses.
