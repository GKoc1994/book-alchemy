from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """An author of one or more books."""
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        return f"<Author id={self.id} name={self.name!r}>"

    def __str__(self):
        return self.name


class Book(db.Model):
    """A book in the library, written by one author."""
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def __repr__(self):
        return f"<Book id={self.id} title={self.title!r}>"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"
