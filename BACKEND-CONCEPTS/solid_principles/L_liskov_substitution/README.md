# L — Liskov Substitution Principle
## Project: Geometry & Shapes

---

### What is LSP?

> **Objects of a subclass should be replaceable with objects of the parent class without breaking the program.**

If you have a function that expects a base class (like `Rectangle`), you must be able to pass a subclass (like `Square`) into it without causing crashes, wrong results, or side effects.

---

### The Classic Problem (`bad.py`)

In mathematics, a **Square IS-A Rectangle**. 
So the natural instinct in Object-Oriented Programming is:

```python
class Square(Rectangle):
    ...
```

**But this violates LSP! Why?**
Because inheritance in programming is about **behavior**, not just definitions.

A `Rectangle` promises: *"If you change my width, my height stays the same."*
A `Square` must enforce: *"If you change my width, my height changes too."*

If a function trusts the `Rectangle` promise and tries to resize it, a `Square` will silently break the calculation:
```python
# The function expects area to be 20. 
# But the Square changed height when width was changed! Area becomes 25.
rect.set_width(5)
rect.set_height(4)
```

**This is a pure LSP violation.** No other principle (SRP or ISP) is broken here. 

---

### The Fix (`good.py`)

**Break the false inheritance.** 

A Square is NOT a Rectangle in terms of software behavior. They should not inherit from each other.

Instead, they should both inherit from a common abstraction that they **can both perfectly honor**:

```
Shape (abstract: get_area)
├── Rectangle (has set_width, set_height)
└── Square    (has set_side)
```

Now, any function expecting a `Shape` can call `get_area()` safely, without worrying about the dangerous resizing behaviors.

---

### How to Run

```bash
python bad.py    # See the Square silently break the area calculation
python good.py   # See safe, correct substitution using Shape
```
