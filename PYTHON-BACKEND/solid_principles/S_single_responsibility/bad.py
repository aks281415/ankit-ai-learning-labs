"""
=============================================================
 S — Single Responsibility Principle
 Project : Library Book Management System
 File    : bad.py  ← VIOLATES SRP
=============================================================

PROBLEM:
  The class `LibraryManager` below does EVERYTHING:
    1. Manages book data          (book domain logic)
    2. Saves/loads from a file    (persistence/storage)
    3. Sends email notifications  (communication)
    4. Generates reports          (reporting)

  This means the class has 4 REASONS TO CHANGE:
    - Change how books are stored   -> edit LibraryManager
    - Change the email provider     -> edit LibraryManager
    - Change the report format      -> edit LibraryManager
    - Change book rules             -> edit LibraryManager

  Changing one thing can accidentally break everything else.
=============================================================
"""

import json
import os


class LibraryManager:
    """
    [X] This class violates SRP.
    It is responsible for book data, file storage,
    email notifications, AND report generation — all at once.
    """

    def __init__(self):
        self.books = []
        self.data_file = "books.json"

    # -- Responsibility 1: Book domain logic -----------------
    def add_book(self, title: str, author: str, copies: int):
        book = {"title": title, "author": author, "copies": copies}
        self.books.append(book)
        print(f"[LibraryManager] Book added: '{title}'")

    def borrow_book(self, title: str, member_email: str):
        for book in self.books:
            if book["title"] == title:
                if book["copies"] > 0:
                    book["copies"] -= 1
                    print(f"[LibraryManager] '{title}' borrowed by {member_email}")

                    # -- Responsibility 3 mixed in here! -----
                    # Sending email directly inside borrow logic
                    self._send_email(
                        to=member_email,
                        subject="Book Borrowed",
                        body=f"You borrowed '{title}'. Return in 14 days."
                    )

                    # -- Responsibility 2 mixed in here! -----
                    self._save_to_file()
                else:
                    print(f"[LibraryManager] No copies of '{title}' available.")
                return
        print(f"[LibraryManager] Book '{title}' not found.")

    # -- Responsibility 2: File storage ----------------------
    def _save_to_file(self):
        """
        [X] Storage logic is buried inside the same class.
        If we switch from JSON to a database, we edit HERE —
        which could break borrow_book, add_book, etc.
        """
        with open(self.data_file, "w") as f:
            json.dump(self.books, f, indent=2)
        print(f"[LibraryManager] Data saved to {self.data_file}")

    def load_from_file(self):
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                self.books = json.load(f)
            print(f"[LibraryManager] Data loaded from {self.data_file}")

    # -- Responsibility 3: Email notification ----------------
    def _send_email(self, to: str, subject: str, body: str):
        """
        [X] Email logic lives inside a class that is supposed
        to manage books. Changing the email provider (e.g.,
        from SMTP to SendGrid) forces us to touch book logic.
        """
        print(f"[LibraryManager] EMAIL -> To: {to} | Subject: {subject} | Body: {body}")

    # -- Responsibility 4: Report generation -----------------
    def generate_report(self):
        """
        [X] Reporting logic is here too. If we want PDF instead
        of plain text, we edit this already-crowded class.
        """
        print("\n[LibraryManager] -- Library Report --------------")
        for book in self.books:
            print(f"  Title   : {book['title']}")
            print(f"  Author  : {book['author']}")
            print(f"  Copies  : {book['copies']}")
            print("  " + "-" * 35)


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  BAD EXAMPLE — SRP Violation")
    print("=" * 55)

    manager = LibraryManager()

    manager.add_book("Clean Code", "Robert Martin", 3)
    manager.add_book("The Pragmatic Programmer", "Hunt & Thomas", 2)

    manager.borrow_book("Clean Code", "alice@example.com")
    manager.borrow_book("The Pragmatic Programmer", "bob@example.com")

    manager.generate_report()

    print("""
WHY THIS IS BAD:
  - LibraryManager has 4 reasons to change.
  - Email, storage, reporting, and domain logic are tangled.
  - You cannot test book logic without triggering file writes.
  - Swapping JSON -> DB means editing the same class as email.
""")
