# S — Single Responsibility Principle
## Project: Library Book Management System

---

### What is SRP?

> **A class should have one, and only one, reason to change.**

If a class does multiple unrelated things, a change in any one of those things forces you to touch that class — even if the other things haven't changed. This increases the risk of introducing bugs.

---

### The Problem (`bad.py`)

`LibraryManager` does **4 completely different jobs**:

| Method | Responsibility |
|--------|---------------|
| `add_book`, `borrow_book` | Book domain logic |
| `_save_to_file`, `load_from_file` | File storage (persistence) |
| `_send_email` | Email notification |
| `generate_report` | Report formatting |

**Consequence:** If you want to change the email provider from SMTP to SendGrid, you must open `LibraryManager` — the same file that contains book borrowing logic. You risk breaking it accidentally.

---

### The Fix (`good.py`)

Split into 5 focused classes:

```
Book              -> holds book data only
BookRepository    -> saves/loads from storage only
EmailService      -> sends emails only
ReportService     -> generates reports only
LibraryService    -> orchestrates the workflow
```

Each class now has **exactly one reason to change**.

---

### How to Run

```bash
python bad.py    # See the tangled, all-in-one version
python good.py   # See the clean, separated version
```

---

### Real-World Usage

- **Django** uses this everywhere: `Model` (data), `View` (logic), `Serializer` (formatting), `Signal` (notifications) are all separate classes.
- **Django REST Framework**: `Serializer`, `Permission`, `Throttle`, `Renderer` — each handles one concern.

---

### Quick Test to Spot SRP Violations

Ask yourself: *"How many reasons does this class have to change?"*
- If the answer is more than **1** -> it violates SRP.
- Common red flags: classes named `Manager`, `Handler`, `Processor`, `Helper` that do everything.
