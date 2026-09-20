import duckdb

con = duckdb.connect("goodreads.duckdb")

con.execute(
    """
        CREATE OR REPLACE TABLE book_no_lang_code AS
        SELECT * FROM books_with_genres
        WHERE language_code = '';
    """
)

con.sql("SUMMARIZE book_no_lang_code").show()
con.sql("SELECT book_id, title, language_code, description FROM book_no_lang_code LIMIT 30").show()

con.close()