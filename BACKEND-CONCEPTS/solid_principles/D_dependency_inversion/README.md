# D — Dependency Inversion Principle
## Project: Order Notification System

---

### What is DIP?

> **High-level modules should not depend on low-level modules. Both should depend on abstractions.**
> **Abstractions should not depend on details. Details should depend on abstractions.**

---

### The Problem (`bad.py`)

`OrderService` (business logic = high-level) creates `SMTPEmailSender` (email detail = low-level) directly inside its `__init__`:

```python
class OrderService:
    def __init__(self):
        self.notifier = SMTPEmailSender()  # [X] hardcoded!
```

**Dependency arrow (wrong direction):**
```
OrderService  ──────────▶  SMTPEmailSender
(high-level)               (low-level)
```

Consequences:
- Want SendGrid instead of SMTP? -> Rewrite `OrderService`
- Want SMS alerts? -> Rewrite `OrderService`
- Want to unit test without sending real emails? -> Impossible cleanly

---

### The Fix (`good.py`)

**Step 1 — Define an abstraction:**
```python
class Notifier(Protocol):
    def notify(self, recipient, subject, message) -> None: ...
```

**Step 2 — Each sender implements it independently:**
```
SMTPEmailSender   -> implements Notifier
SendGridSender    -> implements Notifier
SMSSender         -> implements Notifier
PushSender        -> implements Notifier
MockNotifier      -> implements Notifier (for tests)
```

**Step 3 — Inject the dependency from outside:**
```python
class OrderService:
    def __init__(self, notifier: Notifier):  # [OK] injected!
        self.notifier = notifier
```

**Dependency arrow (correct direction):**
```
OrderService  ──▶  Notifier  ◀──  SMTPEmailSender
(high-level)    (abstraction)     (low-level)
                               ◀──  SMSSender
                               ◀──  PushSender
```

---

### Three Injection Patterns Shown

| Pattern | How | When to use |
|---------|-----|-------------|
| **Constructor Injection** | `OrderService(notifier=SMTPSender())` | Most common — dependency lives for object's lifetime |
| **Method Injection** | `service.place_order(..., notifier=SMS())` | When each call needs a different implementation |
| **Multiple via Composite** | `MultiChannelNotifier([Email, SMS, Push])` | When you want all channels at once |

---

### How to Run

```bash
python bad.py    # See hardcoded SMTP coupling
python good.py   # See all 6 injection scenarios including MockNotifier
```

---

### Unit Testing Benefit

With DIP, testing `OrderService` requires **zero setup**:

```python
# In tests — no real emails, no SMTP server, no mocking frameworks
mock = MockNotifier()
service = OrderService(notifier=mock)
service.place_order("ORD-1", "test@test.com", "Item")

assert len(mock.sent) == 1
assert mock.sent[0]["subject"] == "Order Confirmed: #ORD-1"
```

Without DIP, you'd need `unittest.mock.patch` to intercept the hardcoded `SMTPEmailSender` — a code smell that signals tight coupling.

---

### Real-World Usage

- **FastAPI `Depends()`** — DB sessions, auth, config are all injected. Routes don't create their own DB connections.
- **Django `settings.EMAIL_BACKEND`** — set `'django.core.mail.backends.smtp.EmailBackend'` in prod, `'django.core.mail.backends.console.EmailBackend'` in dev. `send_mail()` never changes.
- **pytest fixtures** — inject DB, HTTP client, mock services into tests. Tests never create their own infrastructure.
- **SQLAlchemy** — inject `Session` into repositories. Swap SQLite (tests) with PostgreSQL (production) by changing the injected session only.
