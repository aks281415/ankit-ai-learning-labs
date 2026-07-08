"""
=============================================================
 I — Interface Segregation Principle
 Project : Employee Management System
 File    : good.py  ← FOLLOWS ISP
=============================================================

SOLUTION:
  Break the fat `Employee` interface into small, focused
  Protocols — one per capability:

    Workable      -> can work
    Payable       -> gets a salary
    LeaveApprover -> can approve others' leaves
    Trainable     -> attends training programs
    TimesheetUser -> submits timesheets

  Each employee class implements ONLY the protocols that
  apply to it — nothing more, nothing less.

WHY PYTHON PROTOCOLS (not ABCs)?
  - `typing.Protocol` uses STRUCTURAL subtyping.
  - No explicit `class Intern(Workable, Trainable):` needed.
  - If Intern has `work()` and `attend_training()` methods,
    it automatically satisfies those protocols.
  - This is called "duck typing with type safety".
  - Works with mypy and pyright for static checks.

You can use ABCs too — both approaches shown in comments.
=============================================================
"""

from typing import Protocol, runtime_checkable


# -- Small, focused Protocols ---------------------------------

@runtime_checkable
class Workable(Protocol):
    """Any entity that can perform work."""
    def work(self) -> str: ...


@runtime_checkable
class Payable(Protocol):
    """Any entity that receives a salary/payment."""
    def get_salary(self) -> float: ...


@runtime_checkable
class LeaveApprover(Protocol):
    """Any entity that can approve employee leaves."""
    def approve_leave(self, emp_id: int) -> bool: ...


@runtime_checkable
class Trainable(Protocol):
    """Any entity that attends training programs."""
    def attend_training(self, course: str) -> str: ...


@runtime_checkable
class TimesheetUser(Protocol):
    """Any entity that submits timesheets."""
    def submit_timesheet(self) -> str: ...


# -- Concrete employee classes --------------------------------

class Intern:
    """
    [OK] Intern implements ONLY what applies:
       - Workable     [OK] interns do work
       - Trainable    [OK] interns attend training

    Not Payable (stipend handled separately),
    Not LeaveApprover (can't approve anyone's leave),
    Not TimesheetUser (not required for interns).
    """

    def work(self) -> str:
        return "Intern: learning and completing assigned tasks"

    def attend_training(self, course: str) -> str:
        return f"Intern attending '{course}' training session"

    def receive_stipend(self) -> float:
        """Intern-specific — not in any shared protocol."""
        return 10000.0


class Contractor:
    """
    [OK] Contractor implements ONLY what applies:
       - Workable     [OK]
       - Payable      [OK] (per-project payment)
       - TimesheetUser [OK] (submits invoice/timesheet)

    Not LeaveApprover (external, not managing employees),
    Not Trainable (not attending internal programs).
    """

    def work(self) -> str:
        return "Contractor: delivering project milestones"

    def get_salary(self) -> float:
        return 50000.0  # per project

    def submit_timesheet(self) -> str:
        return "Contractor: submitted project invoice"


class FullTimeEmployee:
    """
    [OK] Full-time employees satisfy most protocols:
       - Workable     [OK]
       - Payable      [OK]
       - Trainable    [OK]
       - TimesheetUser [OK]
    Not a LeaveApprover (regular employees can't approve).
    """

    def work(self) -> str:
        return "Full-time employee: working regular hours"

    def get_salary(self) -> float:
        return 80000.0

    def attend_training(self, course: str) -> str:
        return f"Full-time employee attending '{course}'"

    def submit_timesheet(self) -> str:
        return "Full-time employee: monthly timesheet submitted"


class Manager:
    """
    [OK] Manager satisfies all protocols including LeaveApprover.
    They DO NOT submit timesheets (they approve them).
    Not forced to implement submit_timesheet().
    """

    def work(self) -> str:
        return "Manager: planning, delegating, and reviewing"

    def get_salary(self) -> float:
        return 150000.0

    def approve_leave(self, emp_id: int) -> bool:
        print(f"  [Manager] Leave approved for employee #{emp_id}")
        return True

    def attend_training(self, course: str) -> str:
        return f"Manager attending leadership course: '{course}'"


class HRManager(Manager):
    """
    [OK] HR Manager also reviews timesheets — extends Manager.
    Demonstrates composing protocols naturally.
    """

    def review_timesheets(self) -> str:
        return "HR Manager: reviewing all submitted timesheets"


# -- Functions typed against specific protocols ---------------

def process_payroll(employees: list) -> None:
    """
    [OK] Only calls get_salary() — only for Payable entities.
    runtime_checkable lets us filter at runtime safely.
    """
    print("\n[Payroll] Processing salaries:")
    for emp in employees:
        if isinstance(emp, Payable):
            print(f"  {emp.__class__.__name__}: Rs.{emp.get_salary()}/month")
        else:
            print(f"  {emp.__class__.__name__}: Not on payroll (stipend/other)")


def run_training(employees: list, course: str) -> None:
    """[OK] Only Trainable employees are enrolled."""
    print(f"\n[Training] Enrolling employees in '{course}':")
    for emp in employees:
        if isinstance(emp, Trainable):
            print(f"  {emp.__class__.__name__}: {emp.attend_training(course)}")
        else:
            print(f"  {emp.__class__.__name__}: Not eligible for this training")


def collect_timesheets(employees: list) -> None:
    """[OK] Only TimesheetUser employees submit timesheets."""
    print("\n[Timesheets] Collecting monthly timesheets:")
    for emp in employees:
        if isinstance(emp, TimesheetUser):
            print(f"  {emp.__class__.__name__}: {emp.submit_timesheet()}")
        else:
            print(f"  {emp.__class__.__name__}: Not required to submit")


def process_leave_request(approvers: list, emp_id: int) -> None:
    """[OK] Only LeaveApprover entities can approve."""
    print(f"\n[Leave] Processing leave request for employee #{emp_id}:")
    approved = False
    for approver in approvers:
        if isinstance(approver, LeaveApprover):
            result = approver.approve_leave(emp_id)
            approved = approved or result
    if not approved:
        print("  No approver available!")


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  GOOD EXAMPLE — ISP Followed (Employee System)")
    print("=" * 55)

    staff = [
        Intern(),
        Contractor(),
        FullTimeEmployee(),
        Manager(),
        HRManager(),
    ]

    # Each function only works with what it needs
    process_payroll(staff)
    run_training(staff, "Python Advanced Techniques")
    collect_timesheets(staff)
    process_leave_request(staff, emp_id=42)

    print("""
WHY THIS IS GOOD:
  - Intern only has work() and attend_training() — nothing forced
  - Contractor only has work(), get_salary(), submit_timesheet()
  - Manager only has what managers actually do
  - No NotImplementedError crashes anywhere
  - Type checker (mypy) correctly knows who can do what
  - Adding a new employee type: implement only relevant protocols
""")
