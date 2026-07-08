"""
=============================================================
 L — Liskov Substitution Principle
 Project : Geometry & Shapes (Classic Pure LSP Example)
 File    : good.py  ← FIXES LSP
=============================================================

SOLUTION:
  Break the false inheritance!
  A Square should NOT inherit from a Rectangle because their
  behaviours (how they resize) are fundamentally different.

  Instead, both should inherit from a common abstraction
  that they CAN both honour perfectly — like `Shape`.

  The `Shape` contract only promises: "I can calculate an area."
  Both Rectangle and Square can honour this perfectly without
  lying to the caller.

  Rectangle handles its own 2-variable resizing.
  Square handles its own 1-variable resizing.
=============================================================
"""

from abc import ABC, abstractmethod


# ── The true common abstraction ──────────────────────────────

class Shape(ABC):
    """
    [OK] Contract: Any shape must be able to calculate its area.
    This is a contract both Square and Rectangle can honour.
    """
    @abstractmethod
    def get_area(self) -> int:
        pass


# ── Concrete Classes (No false inheritance between them) ─────

class Rectangle(Shape):
    """
    [OK] Rectangle manages independent width and height.
    It honours the Shape contract.
    """
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    def set_width(self, width: int) -> None:
        self._width = width

    def set_height(self, height: int) -> None:
        self._height = height

    def get_area(self) -> int:
        return self._width * self._height


class Square(Shape):
    """
    [OK] Square manages a single side size.
    It no longer inherits from Rectangle, so it doesn't have
    to pretend that width and height are independent.
    It honours the Shape contract perfectly.
    """
    def __init__(self, side: int):
        self._side = side

    def set_side(self, side: int) -> None:
        self._side = side

    def get_area(self) -> int:
        return self._side * self._side


# ── Client Code expecting a Shape ────────────────────────────

def print_area(shape: Shape) -> None:
    """
    [OK] This function trusts the Shape contract.
    It doesn't try to resize them, because resizing isn't
    a shared behavior that applies to all shapes equally.
    """
    print(f"  Area calculated: {shape.get_area()}")


# ── Demo ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  GOOD — Pure LSP Followed")
    print("=" * 55)

    rect = Rectangle(5, 4)
    sq = Square(5)

    print("\n--- Rectangle Area ---")
    print_area(rect)

    print("\n--- Square Area ---")
    print_area(sq)

    print("""
WHY THIS IS GOOD:
  - Square no longer pretends to be a Rectangle.
  - The false inheritance is broken.
  - Both inherit from Shape, and both perfectly satisfy the 
    Shape contract (get_area).
  - Code expecting a Shape can safely substitute a Rectangle 
    or a Square with zero unexpected side effects.
""")
