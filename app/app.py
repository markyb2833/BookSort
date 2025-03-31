import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Use DATABASE_URL from environment or default to local SQLite database
DATABASE_URL = os.environ.get('DATABASE_URL', 'books.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

# ... rest of your existing code ...

if __name__ == '__main__':
    # Only use debug mode when running locally
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=debug) 