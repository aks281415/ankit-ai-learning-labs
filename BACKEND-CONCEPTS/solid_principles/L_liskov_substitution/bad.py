"""
=============================================================
 L — Liskov Substitution Principle
 Project : Geometry & Shapes (Classic Pure LSP Example)
 File    : bad.py  ← VIOLATES LSP ONLY (No SRP/ISP overlap)
=============================================================

SETUP:
  SRP is fine -> Classes just handle geometry.
  ISP is fine -> Squares and Rectangles both have width, height, and area.

THE ONLY PROBLEM — LSP is violated:
  In mathematics, a Square IS-A Rectangle.
  But in programming, inheritance is about BEHAVIOUR, not just data.

  A Rectangle promises:
    "If you change my width, my height stays the same."
  
  A Square MUST enforce:
    "If you change my width, my height must also change."

  Because the Square's behaviour contradicts the Rectangle's
  promise, Square CANNOT safely inherit from Rectangle.
  Any code expecting a Rectangle will get wrong results
  when passed a Square.
=============================================================
"""

class Rectangle:
    """Base class promising independent width and height."""
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    def set_width(self, width: int) -> None:
        self._width = width

    def set_height(self, height: int) -> None:
        self._height = height

    def get_area(self) -> int:
        return self._width * self._height


class Square(Rectangle):
    """
    [X] LSP Violation!
    Inherits from Rectangle, but breaks its behavioral contract.
    To remain a valid square, changing one side MUST change the other.
    """
    def __init__(self, size: int):
        super().__init__(size, size)

    def set_width(self, width: int) -> None:
        self._width = width
        self._height = width  # [X] Side effect! Breaks Rectangle's contract

    def set_height(self, height: int) -> None:
        self._width = height  # [X] Side effect! Breaks Rectangle's contract
        self._height = height


# ── Client Code expecting a Rectangle ────────────────────────

def resize_and_check(rect: Rectangle) -> None:
    """
    This function trusts the Rectangle contract:
    Changing height should NOT affect width.
    """
    rect.set_width(5)
    rect.set_height(4)
    
    # We expect 5 * 4 = 20
    expected_area = 20
    actual_area = rect.get_area()
    
    print(f"  Expected Area : {expected_area}")
    print(f"  Actual Area   : {actual_area}")
    
    if actual_area != expected_area:
        print("  [X] FATAL: The object did not behave like a Rectangle!")
    else:
        print("  [OK] Behaving correctly.")


# ── Demo ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  BAD — Pure LSP Violation (Square/Rectangle)")
    print("=" * 55)

    print("\n--- Passing a Real Rectangle ---")
    real_rect = Rectangle(2, 3)
    resize_and_check(real_rect)

    print("\n--- Passing a Square (Subclass) ---")
    fake_rect = Square(2)
    # The function expects a Rectangle, so passing a Square 
    # should work perfectly according to Object Oriented rules.
    # But watch what happens:
    resize_and_check(fake_rect)

    print("""
WHY THIS IS BAD:
  - The Square IS-A Rectangle in math, but not in code.
  - The Square silently broke the expectations of the caller.
  - LSP states: You must be able to swap a parent for a subclass
    WITHOUT breaking the program. We broke the program.
""")
