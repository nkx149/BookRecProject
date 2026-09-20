import duckdb

con = duckdb.connect("goodreads.duckdb")

null_genre_count = con.execute("""
    SELECT COUNT(*) FROM books_with_genres WHERE genres_text IS NULL
""").fetchdf()
print(null_genre_count)

counts = con.execute("""
    SELECT
        (SELECT COUNT(*) FROM books_raw_combined) AS raw_count,
        (SELECT COUNT(*) FROM books_deduped)      AS deduped_count,
        (SELECT COUNT(*) FROM books_filtered)      AS filtered_count
""").fetchdf()
print(counts)

check = con.execute("""
    SELECT work_id, COUNT(*) AS n, STRING_AGG(DISTINCT title, ' | ') AS titles
    FROM books_raw_combined
    GROUP BY work_id
    HAVING COUNT(*) > 5
    ORDER BY n DESC
    LIMIT 20
""").fetchdf()

print(check)

con.close()