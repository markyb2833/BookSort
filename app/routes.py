from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.book import Book
from app import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            publication_year=int(request.form['publication_year']) if request.form['publication_year'] else None,
            genre=request.form['genre'],
            description=request.form['description'],
            cover_url=request.form['cover_url'],
            rating=float(request.form['rating']) if request.form['rating'] else None
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('main.index'))
        
    books = Book.query.order_by(Book.date_added.desc()).all()
    return render_template('index.html', books=books)

@main.route('/edit_book', methods=['POST'])
def edit_book():
    try:
        book_id = request.form.get('book_id')
        book = Book.query.get_or_404(book_id)
        
        book.personal_rating = float(request.form['personal_rating']) if request.form['personal_rating'] else None
        book.box_location = request.form['box_location']
        book.notes = request.form['notes']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 