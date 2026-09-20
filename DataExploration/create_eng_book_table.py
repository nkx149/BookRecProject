import duckdb

con = duckdb.connect("goodreads.duckdb")

# con.execute(
#     """
#         CREATE OR REPLACE TABLE book_confirm_eng AS
#         SELECT * FROM books_with_genres
#         WHERE language_code IN ('eng', 'en-US', 'en-GB', 'en-CA', 'en');
#     """
# )
con.sql("DESCRIBE book_confirm_eng").show()
con.sql("SELECT book_id, title, language_code, description FROM book_confirm_eng LIMIT 30").show()

con.close()