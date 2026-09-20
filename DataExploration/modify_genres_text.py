import duckdb

con = duckdb.connect("goodreads.duckdb")

# ------------------------------------------------------------------
# Step 1: update books_with_genres with the corrected genres_text_v2
# ------------------------------------------------------------------
# con.execute("""
#     UPDATE books_with_genres
#     SET genres_text = v2.genres_text
#     FROM genres_text_v2 v2
#     WHERE books_with_genres.book_id = v2.book_id
# """)

# # books with zero qualifying genre rows -> explicitly NULL
# con.execute("""
#     UPDATE books_with_genres
#     SET genres_text = NULL
#     WHERE book_id NOT IN (SELECT book_id FROM genres_text_v2)
# """)

# ------------------------------------------------------------------
# Step 2: spot check known titles, using partial match
# ------------------------------------------------------------------
print("=== Spot check: Dune ===\n")
print(con.execute("""
    SELECT title, genres_text, description FROM books_with_genres WHERE title LIKE '%Dune%'
""").df())

# print("\n=== Spot check: Foundation ===\n")
# print(con.execute("""
#     SELECT title, genres_text FROM books_with_genres WHERE title LIKE '%Foundation%'
# """).df())

# print("\n=== Spot check: Me Before You ===\n")
# print(con.execute("""
#     SELECT title, genres_text FROM books_with_genres WHERE title LIKE '%Me Before You%'
# """).df())

# ------------------------------------------------------------------
# Step 3: coverage check
# ------------------------------------------------------------------
print("\n=== Coverage: genres_text null vs non-null ===\n")
print(con.execute("""
    SELECT
        COUNT(*) AS total,
        COUNT(genres_text) AS with_genre,
        COUNT(*) - COUNT(genres_text) AS without_genre,
        ROUND(COUNT(genres_text) * 100.0 / COUNT(*), 1) AS pct_with_genre
    FROM books_with_genres
""").df())

con.close()