import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Render PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Local SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'

db = SQLAlchemy(app)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    isbn = db.Column(db.String(13))
    publication_year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    rating = db.Column(db.Float)
    personal_rating = db.Column(db.Float, default=0)
    box_location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'description': self.description,
            'rating': self.rating,
            'personal_rating': self.personal_rating,
            'box_location': self.box_location,
            'notes': self.notes,
            'cover_url': self.cover_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create tables
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables with the updated schema

@app.route('/')
def index():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('index.html', books=books)

@app.route('/search_book')
def search_book():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    # Google Books API search
    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(api_url)
    books_data = response.json()

    results = []
    if 'items' in books_data:
        for item in books_data['items']:
            volume_info = item.get('volumeInfo', {})
            results.append({
                'title': volume_info.get('title', ''),
                'author': ', '.join(volume_info.get('authors', [])),
                'isbn': next((id for id in volume_info.get('industryIdentifiers', []) 
                            if id.get('type') in ['ISBN_13', 'ISBN_10']), {}).get('identifier', ''),
                'publication_year': volume_info.get('publishedDate', '')[:4] if volume_info.get('publishedDate') else '',
                'genre': ', '.join(volume_info.get('categories', [])),
                'description': volume_info.get('description', ''),
                'rating': volume_info.get('averageRating', 0),
                'cover_url': volume_info.get('imageLinks', {}).get('thumbnail', '')
            })
    return jsonify(results)

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        data = request.json
        book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            publication_year=int(data['publication_year']) if data['publication_year'] else None,
            genre=data['genre'],
            description=data['description'],
            rating=float(data['rating']) if data['rating'] else 0,
            personal_rating=0,
            box_location='',
            notes='',
            cover_url=data.get('cover_url', '')
        )
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/update_book/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        data = request.json
        book.personal_rating = float(data['personal_rating']) if data['personal_rating'] else 0
        book.box_location = data['box_location']
        book.notes = data['notes']
        db.session.commit()
        return jsonify(book.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=debug) 