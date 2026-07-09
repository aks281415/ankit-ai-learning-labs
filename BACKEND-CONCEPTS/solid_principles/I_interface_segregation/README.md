# I — Interface Segregation Principle
## Project: Employee Management System

---

### What is ISP?

> **Clients should not be forced to depend on interfaces they do not use.**

When an abstract class or interface has too many methods, classes that implement it are forced to provide stub/dummy implementations of methods that don't apply to them. This is a "fat interface."

---

### The Problem (`bad.py`)

One big `Employee` abstract class with 5 methods forces **all** employee types to implement **all** methods:

| Employee Type | Must Implement | Makes Sense? |
|---------------|---------------|--------------|
| `Intern` | `approve_leave()` | [X] Interns can't approve leaves |
| `Intern` | `get_salary()` | [X] Interns get a stipend, not salary |
| `Contractor` | `attend_training()` | [X] Contractors don't do internal training |
| `Manager` | `submit_timesheet()` | [X] Managers review, not submit |

Result: `NotImplementedError` crashes everywhere at runtime.

---

### The Fix (`good.py`)

Split into **5 small protocols**, each representing one capability:

```python
Workable       -> work()
Payable        -> get_salary()
LeaveApprover  -> approve_leave()
Trainable      -> attend_training()
TimesheetUser  -> submit_timesheet()
```

Each employee class implements **only what applies**:

| Employee | Workable | Payable | LeaveApprover | Trainable | TimesheetUser |
|----------|----------|---------|---------------|-----------|---------------|
| Intern | [OK] | [X] | [X] | [OK] | [X] |
| Contractor | [OK] | [OK] | [X] | [X] | [OK] |
| FullTime | [OK] | [OK] | [X] | [OK] | [OK] |
| Manager | [OK] | [OK] | [OK] | [OK] | [X] |

---

### How to Run

```bash
python bad.py    # See NotImplementedError crashes for irrelevant methods
python good.py   # See clean protocol-based segregation
```

---

### Python `typing.Protocol` — The Modern Way

Python 3.8+ introduced `Protocol` for **structural subtyping**:

```python
from typing import Protocol

class Payable(Protocol):
    def get_salary(self) -> float: ...

# Any class with get_salary() automatically satisfies Payable
# No need to explicitly inherit from it!
```

Add `@runtime_checkable` to use `isinstance()` checks at runtime.

---

### Real-World Usage

- **Python's `collections.abc`** — `Iterable`, `Sized`, `Callable`, `Hashable` are all tiny, focused ABCs. You never have one giant `PythonObject` ABC.
- **FastAPI** — Each dependency (`Depends`) does one job: auth, DB session, config. Not one fat dependency.
- **boto3 (AWS SDK)** — S3 client, DynamoDB client, SQS client each expose only the methods relevant to that service.
