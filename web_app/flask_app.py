from flask import Flask, request, render_template
import pandas as pd
import sys
sys.path.append('./')
from scripts.book_rec_user_input import get_recommendations

app = Flask(__name__)

# Load the recommendation model output or use the existing correlation logic
# For simplicity, assume we have a precomputed Pandas DataFrame 'recommendations_df'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    book_title = request.form['book_title'].lower()
    book_author = request.form['book_author'].lower()  # Get the user input
    # Fetch recommendations based on the favorite book from your model output
    recommendations = get_recommendations(book_title, book_author)
    recommendations = recommendations[['Book-Title', 'Book-Author', 'avg_rating']].to_dict(orient='records')
    return render_template('recommend.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
