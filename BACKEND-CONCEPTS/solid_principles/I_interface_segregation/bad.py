"""
=============================================================
 I — Interface Segregation Principle
 Project : Employee Management System
 File    : bad.py  ← VIOLATES ISP
=============================================================

PROBLEM:
  ISP states:
    "Clients should not be forced to depend on interfaces
     (methods) they do not use."

  Here, one giant abstract class `Employee` forces ALL
  employee types to implement ALL methods — even ones that
  make no sense for them:

    - Intern         must implement approve_leave()  -> nonsense
    - Contractor     must implement attend_training() -> nonsense
    - Manager        must implement submit_timesheet() -> they don't

  These classes are forced to provide stub/dummy implementations
  of methods that are completely irrelevant to them.
  This creates:
    - Confusion ("why does Intern have approve_leave?")
    - Runtime errors (NotImplementedError surprises)
    - False type safety (a type checker thinks Intern can
      approve leaves, but it crashes at runtime)
=============================================================
"""

from abc import ABC, abstractmethod


class Employee(ABC):
    """
    [X] Fat interface — forces EVERYONE to implement EVERYTHING.
    This is the ISP violation: one bloated abstract base class.
    """

    @abstractmethod
    def work(self) -> str:
        """All employees work."""
        ...

    @abstractmethod
    def get_salary(self) -> float:
        """All employees get paid... or do they?"""
        ...

    @abstractmethod
    def approve_leave(self, emp_id: int) -> bool:
        """Only managers can approve leaves — but forced on all!"""
        ...

    @abstractmethod
    def attend_training(self, course: str) -> str:
        """Contractors don't attend internal training."""
        ...

    @abstractmethod
    def submit_timesheet(self) -> str:
        """Managers don't submit timesheets — but forced to!"""
        ...


class FullTimeEmployee(Employee):
    """[OK] Full-time employees can do all of these — this one is fine."""

    def work(self) -> str:
        return "Full-time employee working 9-5"

    def get_salary(self) -> float:
        return 80000.0

    def approve_leave(self, emp_id: int) -> bool:
        return False  # Regular employees can't approve, only managers

    def attend_training(self, course: str) -> str:
        return f"Attending '{course}' training"

    def submit_timesheet(self) -> str:
        return "Timesheet submitted for the month"


class Intern(Employee):
    """
    [X] Intern forced to implement approve_leave and get_salary.
    Interns don't earn a salary (stipend != salary) and
    certainly cannot approve anyone's leave!
    """

    def work(self) -> str:
        return "Intern learning and doing assigned tasks"

    def get_salary(self) -> float:
        # [X] Interns get a stipend, not a salary
        # But forced to implement this by the fat interface
        raise NotImplementedError("Interns get stipend, not salary!")

    def approve_leave(self, emp_id: int) -> bool:
        # [X] Completely irrelevant — interns cannot approve leaves!
        raise NotImplementedError("Interns cannot approve leave!")

    def attend_training(self, course: str) -> str:
        return f"Intern attending '{course}' training"

    def submit_timesheet(self) -> str:
        return "Intern submitted timesheet"


class Contractor(Employee):
    """
    [X] Contractor forced to implement approve_leave and
    attend_training — contractors do neither!
    They work independently and are not on company training programs.
    """

    def work(self) -> str:
        return "Contractor working on assigned project"

    def get_salary(self) -> float:
        return 50000.0  # per project

    def approve_leave(self, emp_id: int) -> bool:
        # [X] Contractors don't manage other employees!
        raise NotImplementedError("Contractors cannot approve leave!")

    def attend_training(self, course: str) -> str:
        # [X] Contractors are external — no internal training!
        raise NotImplementedError("Contractors don't attend internal training!")

    def submit_timesheet(self) -> str:
        return "Contractor submitted invoice"


class Manager(Employee):
    """
    [X] Manager forced to implement submit_timesheet.
    Senior managers typically don't submit timesheets —
    they review them. But the fat interface forces this.
    """

    def work(self) -> str:
        return "Manager planning, delegating, and reviewing"

    def get_salary(self) -> float:
        return 150000.0

    def approve_leave(self, emp_id: int) -> bool:
        print(f"  [Manager] Approving leave for employee #{emp_id}")
        return True

    def attend_training(self, course: str) -> str:
        return f"Manager attending leadership training: '{course}'"

    def submit_timesheet(self) -> str:
        # [X] Forced to implement something that doesn't apply
        raise NotImplementedError("Managers review timesheets, not submit them!")


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  BAD EXAMPLE — ISP Violation (Employee System)")
    print("=" * 55)

    employees = [FullTimeEmployee(), Intern(), Contractor(), Manager()]

    for emp in employees:
        print(f"\n{emp.__class__.__name__}:")
        print(f"  work()        -> {emp.work()}")

        try:
            print(f"  get_salary()  -> Rs.{emp.get_salary()}")
        except NotImplementedError as e:
            print(f"  get_salary()  -> [X] CRASH: {e}")

        try:
            result = emp.approve_leave(42)
            print(f"  approve_leave() -> {result}")
        except NotImplementedError as e:
            print(f"  approve_leave() -> [X] CRASH: {e}")

        try:
            print(f"  submit_timesheet() -> {emp.submit_timesheet()}")
        except NotImplementedError as e:
            print(f"  submit_timesheet() -> [X] CRASH: {e}")

    print("""
WHY THIS IS BAD:
  - Intern, Contractor, Manager all crash on irrelevant methods
  - The type system lies: it says Intern can approve_leave()
    but it crashes at runtime
  - Fat interface forces unrelated behaviour on every class
  - Adding a new employee type means implementing 5 methods
    even if only 1 is relevant
""")
