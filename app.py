import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book

app = Flask(__name__)
app.secret_key = "book-alchemy-secret-key"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


def parse_date(value):
    """Convert a 'YYYY-MM-DD' string from a form into a date, or None if empty."""
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.route("/")
def home():
    """Show all books, optionally filtered by a search term and sorted."""
    sort = request.args.get("sort", "title")
    search = request.args.get("search", "").strip()

    query = Book.query.join(Author)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(pattern), Author.name.ilike(pattern)))

    if sort == "author":
        query = query.order_by(Author.name, Book.title)
    else:
        query = query.order_by(Book.title)

    books = query.all()
    return render_template("home.html", books=books, sort=sort, search=search)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Show the author form (GET) and save a new author (POST)."""
    message = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            message = "Please enter the author's name."
        else:
            author = Author(
                name=name,
                birth_date=parse_date(request.form.get("birthdate")),
                date_of_death=parse_date(request.form.get("date_of_death")),
            )
            db.session.add(author)
            db.session.commit()
            message = f"Author '{author.name}' was added successfully."
    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Show the book form (GET) and save a new book (POST)."""
    message = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        isbn = request.form.get("isbn", "").strip()
        year = request.form.get("publication_year", "").strip()
        author_id = request.form.get("author_id")

        if not title or not isbn or not author_id:
            message = "Please fill in title, ISBN and author."
        else:
            book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(year) if year else None,
                author_id=int(author_id),
            )
            db.session.add(book)
            try:
                db.session.commit()
                message = f"Book '{book.title}' was added successfully."
            except IntegrityError:
                db.session.rollback()
                message = f"A book with ISBN {isbn} already exists."

    authors = Author.query.order_by(Author.name).all()
    return render_template("add_book.html", authors=authors, message=message)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book, and its author too if they have no other books."""
    book = Book.query.get_or_404(book_id)
    author = book.author
    title = book.title

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f"Book '{title}' was deleted. {author.name} had no other books and was removed too.")
    else:
        flash(f"Book '{title}' was deleted successfully.")

    return redirect(url_for("home"))


# Run once to create the tables, then comment it out again.
# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
