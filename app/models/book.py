from app import db
from datetime import datetime

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    publication_year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    cover_url = db.Column(db.String(500))
    rating = db.Column(db.Float)  # Google Books rating
    personal_rating = db.Column(db.Float)  # Personal rating out of 5
    box_location = db.Column(db.String(100))  # Physical location of the book
    notes = db.Column(db.Text)  # Personal notes 