"""
=============================================================
 S — Single Responsibility Principle
 Project : Library Book Management System
 File    : good.py  ← FOLLOWS SRP
=============================================================

SOLUTION:
  We split LibraryManager into 4 focused classes:

    1. Book            -> holds book data only
    2. BookRepository  -> handles file storage only
    3. EmailService    -> handles notifications only
    4. ReportService   -> handles report generation only
    5. LibraryService  -> orchestrates the above (thin layer)

  Now each class has EXACTLY ONE reason to change:
    - Book storage changes  -> only BookRepository changes
    - Email provider changes -> only EmailService changes
    - Report format changes  -> only ReportService changes
    - Book rules change      -> only Book/LibraryService changes

  You can also TEST each class in total isolation.
=============================================================
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


# -- 1. Book — pure data, no logic ---------------------------
@dataclass
class Book:
    """
    [OK] Responsibility: Hold book data.
    Nothing else. No file, no email, no report.
    """
    title: str
    author: str
    copies: int


# -- 2. BookRepository — storage only ------------------------
class BookRepository:
    """
    [OK] Responsibility: Save and load books from storage.
    If we switch from JSON -> SQLite -> PostgreSQL,
    ONLY this class changes. Book logic stays untouched.
    """

    def __init__(self, filepath: str = "books.json"):
        self.filepath = filepath

    def save_all(self, books: List[Book]) -> None:
        data = [{"title": b.title, "author": b.author, "copies": b.copies}
                for b in books]
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[BookRepository] Saved {len(books)} books to {self.filepath}")

    def load_all(self) -> List[Book]:
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath) as f:
            data = json.load(f)
        books = [Book(**item) for item in data]
        print(f"[BookRepository] Loaded {len(books)} books from {self.filepath}")
        return books


# -- 3. EmailService — notifications only --------------------
class EmailService:
    """
    [OK] Responsibility: Send email notifications.
    If we swap SMTP for SendGrid, only this class changes.
    BookRepository and Book are completely unaffected.
    """

    def send(self, to: str, subject: str, body: str) -> None:
        # In production this would call smtplib or an API
        print(f"[EmailService] EMAIL -> To: {to}")
        print(f"               Subject: {subject}")
        print(f"               Body: {body}")


# -- 4. ReportService — reporting only -----------------------
class ReportService:
    """
    [OK] Responsibility: Generate reports.
    If we want PDF output tomorrow, only this class changes.
    """

    def generate(self, books: List[Book]) -> None:
        print("\n[ReportService] -- Library Report ---------------")
        for book in books:
            print(f"  Title   : {book.title}")
            print(f"  Author  : {book.author}")
            print(f"  Copies  : {book.copies}")
            print("  " + "-" * 35)


# -- 5. LibraryService — thin orchestrator -------------------
class LibraryService:
    """
    [OK] Responsibility: Orchestrate the borrow workflow.
    It coordinates other classes but does NOT implement
    their logic itself. It delegates everything.
    """

    def __init__(
        self,
        repo: BookRepository,
        email: EmailService,
    ):
        self.repo = repo
        self.email = email
        self.books: List[Book] = []

    def load(self) -> None:
        self.books = self.repo.load_all()

    def add_book(self, title: str, author: str, copies: int) -> None:
        self.books.append(Book(title, author, copies))
        print(f"[LibraryService] Book added: '{title}'")

    def borrow_book(self, title: str, member_email: str) -> None:
        book = self._find(title)
        if not book:
            print(f"[LibraryService] Book '{title}' not found.")
            return
        if book.copies == 0:
            print(f"[LibraryService] No copies of '{title}' available.")
            return

        # Domain logic
        book.copies -= 1

        # Delegate storage -> only repo knows HOW to save
        self.repo.save_all(self.books)

        # Delegate notification -> only email service knows HOW to send
        self.email.send(
            to=member_email,
            subject="Book Borrowed",
            body=f"You borrowed '{title}'. Return in 14 days."
        )
        print(f"[LibraryService] '{title}' borrowed by {member_email}")

    def _find(self, title: str) -> Optional[Book]:
        return next((b for b in self.books if b.title == title), None)


# -- Demo -----------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  GOOD EXAMPLE — SRP Followed")
    print("=" * 55)

    # Each class is independently created and can be swapped
    repo    = BookRepository("books.json")
    email   = EmailService()
    reports = ReportService()

    library = LibraryService(repo=repo, email=email)
    library.add_book("Clean Code", "Robert Martin", 3)
    library.add_book("The Pragmatic Programmer", "Hunt & Thomas", 2)

    library.borrow_book("Clean Code", "alice@example.com")
    library.borrow_book("The Pragmatic Programmer", "bob@example.com")

    reports.generate(library.books)

    print("""
WHY THIS IS GOOD:
  - Book      -> only knows about book data
  - BookRepository -> only knows about file storage
  - EmailService   -> only knows about sending emails
  - ReportService  -> only knows about formatting reports
  - LibraryService -> only orchestrates the workflow

  Each class has EXACTLY ONE reason to change.
  You can test each one in isolation with zero side effects.
""")
