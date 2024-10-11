def get_recommendations(user_input_title, user_input_author):
    # Import necessary libraries
    import pandas as pd
    import numpy as np
    import sys
    sys.path.append('./')
    from scripts.etl import string_normalize
    # Load ratings (with on_bad_lines to handle malformed rows)
    books = pd.read_csv('data/books_cleaned.csv', encoding='utf-8',  on_bad_lines='skip', dtype={'ISBN': str,'Book-Title': str,'Book-Author': str,'Book-Title-Clean': str,'Book-Author-Clean': str})

    # Load books
    ratings = pd.read_csv('data/ratings_cleaned.csv', encoding='utf-8', dtype={'User-ID': int, 'ISBN': str, 'Book-Rating': int})

    # Store original book title and author for later use
    original_books = books[['Book-Title', 'Book-Author', 'Book-Title-Cleaned', 'Book-Author-Cleaned']].drop_duplicates()

    # Merge ratings and books on ISBN
    merged_dataset = pd.merge(ratings, books, on='ISBN')
    # Convert all string columns to lowercase to ensure consistency for matching

    # Convert user input to lowercase for matching
    user_input_title = string_normalize(user_input_title)
    user_input_author = string_normalize(user_input_author)

    # Find users who read the input book (by both title and author)
    input_book_readers = merged_dataset['User-ID'][
        (merged_dataset['Book-Title-Cleaned'] == user_input_title) & 
        (merged_dataset['Book-Author-Cleaned'] == user_input_author)
    ]

    if input_book_readers.empty:
        print(f"No ratings found for the book '{user_input_title}' by {user_input_author}. Please try another book.")
        return
    else:
        # Remove duplicates and extract unique users
        input_book_readers = np.unique(input_book_readers)

        # Create a dataset of books read by the users who also read the input book
        books_of_input_readers = merged_dataset[merged_dataset['User-ID'].isin(input_book_readers)]

        # Count the number of ratings per book by users who read the input book
        number_of_rating_per_book = books_of_input_readers.groupby(['Book-Title-Cleaned', 'Book-Author-Cleaned']).agg('count').reset_index()

        # Select only books with a sufficient number of ratings (threshold: 8 ratings)
        books_to_compare = number_of_rating_per_book[['Book-Title-Cleaned', 'Book-Author-Cleaned']][number_of_rating_per_book['User-ID'] >= 8]
        books_to_compare = books_to_compare.apply(lambda x: tuple(x), axis=1).tolist()  # List of tuples (Book-Title, Book-Author)

        # Filter the dataset to include only those books
        ratings_data_raw = books_of_input_readers[
            books_of_input_readers[['Book-Title-Cleaned', 'Book-Author-Cleaned']].apply(tuple, axis=1).isin(books_to_compare)
        ]

        # Group by User, Book and Author and compute the mean rating
        ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title-Cleaned', 'Book-Author-Cleaned'])['Book-Rating'].mean()

        # Reset the index to make User-ID visible in every row
        ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

        # Pivot the dataset for correlation analysis (group by both title and author)
        dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns=['Book-Title-Cleaned', 'Book-Author-Cleaned'], values='Book-Rating')

        # Compute correlation for the input book (title and author)
        input_book = (user_input_title, user_input_author)
        if input_book in dataset_for_corr.columns:
            dataset_of_other_books = dataset_for_corr.copy(deep=False)
            dataset_of_other_books.drop([input_book], axis=1, inplace=True)

            book_titles = []
            correlations = []
            avgrating = []

            # Calculate correlations and average ratings for other books
            for book in dataset_of_other_books.columns:
                book_titles.append(book)  # This is a tuple (Book-Title, Book-Author)
                correlations.append(dataset_for_corr[input_book].corr(dataset_of_other_books[book]))

                # Get the average rating for the current book
                avg_rating = ratings_data_raw[
                    (ratings_data_raw['Book-Title-Cleaned'] == book[0]) & 
                    (ratings_data_raw['Book-Author-Cleaned'] == book[1])
                ].groupby(['Book-Title-Cleaned', 'Book-Author-Cleaned'])['Book-Rating'].mean().values[0]
                avgrating.append(round(avg_rating, 2))

            # Create a DataFrame of correlations and average ratings
            corr_result = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book', 'corr', 'avg_rating'])

            # Merge using both book title and author for matching
            corr_result['Book-Title-Cleaned'] = corr_result['book'].apply(lambda x: x[0])
            corr_result['Book-Author-Cleaned'] = corr_result['book'].apply(lambda x: x[1])

            # Merge with the original_books DataFrame to get the proper case formatting
            corr_result = corr_result.merge(original_books, left_on=['Book-Title-Cleaned', 'Book-Author-Cleaned'], right_on=['Book-Title-Cleaned', 'Book-Author-Cleaned'] ,how='left')
            corr_result.drop_duplicates(subset=['Book-Title-Cleaned', 'Book-Author-Cleaned'], inplace=True)

            # Display the top 10 recommended books with the original titles and authors
            top_10_books = corr_result.sort_values('corr', ascending=False).head(10)[['Book-Title', 'Book-Author', 'corr', 'avg_rating']]
            print(f"Top 10 books similar to '{user_input_title}' by {user_input_author}:")
            print(top_10_books)
            return top_10_books

        else:
            print(f"The book '{user_input_title}' by {user_input_author} does not have enough ratings to compute correlations with other books.")
            return None

#print(get_recommendations('Misery', 'Stephen King'))
