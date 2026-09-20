
# con.sql("SHOW TABLES").show()
# con.sql("DESCRIBE books_with_genres").show()
# con.sql("SUMMARIZE books_with_genres").show(max_rows=35)
# con.sql("SUMMARIZE genres_flat").show()
# con.sql("""
#     COPY(SELECT
#             CASE
#                 WHEN language_code IS NULL THEN '<NULL>'
#                 WHEN language_code::VARCHAR = '' THEN '<EMPTY STRING>'
#                 ELSE language_code::VARCHAR
#             END AS value,
#             typeof(language_code) AS data_type,
#             COUNT(*) AS n
#         FROM books_with_genres
#         GROUP BY 1, 2
#         ORDER BY n DESC) TO 'language_code_counts.txt' (FORMAT CSV, DELIMITER '\t', HEADER)
    
# """)
# top_outliers = con.sql("""
#     SELECT g.book_id, g.genre_name, g.genre_count, b.title
#     FROM genres_flat g
#     JOIN books_with_genres b ON g.book_id = b.book_id
#     WHERE g.genre_count > 0
#     ORDER BY g.genre_count DESC
#     LIMIT 10
# """).df()

# print(top_outliers)

# con.sql("""
#     COPY (
#         SELECT
#             genre_name AS value,
#             COUNT(*) AS num_books,
#             SUM(genre_count) AS total_shelf_matches
#         FROM genres_flat
#         WHERE genre_count > 0
#         GROUP BY 1
#         ORDER BY num_books DESC
#     ) TO 'genre_names.txt' (FORMAT CSV, DELIMITER '\t', HEADER)
# """)
import duckdb

con = duckdb.connect("goodreads.duckdb")

# Step 1 (corrected): restrict to books actually in your corpus
# print("=== Books with genre matches, but all below old threshold of 3 ===\n")
# result = con.execute("""
#     SELECT COUNT(DISTINCT g.book_id) AS books_only_weak_matches
#     FROM genres_flat g
#     SEMI JOIN books_with_genres b ON g.book_id = b.book_id
#     WHERE g.book_id NOT IN (
#         SELECT book_id FROM genres_flat WHERE genre_count >= 3
#     )
#     AND g.genre_count > 0
# """).df()
# print(result)
con.sql("SELECT COUNT(*) FROM books_with_genres WHERE language_code NOT IN ('eng','en-US','en-GB','en-CA','en');").show()


con.close()


