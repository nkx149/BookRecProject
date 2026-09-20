import duckdb

con = duckdb.connect("goodreads.duckdb", read_only=True)
# con.sql("DESCRIBE genres_flat").show()
# con.sql("SUMMARIZE genres_flat").show()
# con.sql("SELECT * FROM genres_flat LIMIT 50").show()
# con.sql("SELECT book_id, title, genres_text FROM books_with_genres LIMIT 50").show()
con.sql("SELECT g.book_id, g.genre_name, g.genre_count, b.genres_text FROM genres_flat g JOIN books_with_genres b ON g.book_id = b.book_id WHERE g.genre_count < 0").show()
