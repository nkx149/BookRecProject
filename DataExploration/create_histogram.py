import duckdb

con = duckdb.connect("goodreads.duckdb")

# ------------------------------------------------------------------
# Confirm scale of the negative-count problem before discarding
# ------------------------------------------------------------------
print("=== Row counts: total vs negative/zero genre_count ===\n")
counts = con.execute("""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) FILTER (WHERE genre_count <= 0) AS invalid_rows
    FROM genres_flat;
""").fetchdf()
print(counts)

# ------------------------------------------------------------------
# Histogram, filtered to valid (positive) counts only
# ------------------------------------------------------------------
print("\n=== Genre Count Histogram (valid rows only) ===\n")
genre_count_hist = con.execute("""
    SELECT entry.key AS bucket, entry.value AS n
    FROM (
        SELECT histogram(genre_count) AS h
        FROM genres_flat
        WHERE genre_count > 0
    ) t,
    UNNEST(map_entries(t.h)) AS u(entry)
    ORDER BY bucket;
""").fetchdf()
print(genre_count_hist)

# ------------------------------------------------------------------
# Quantiles, filtered
# ------------------------------------------------------------------
print("\n=== Genre Count Quantiles (valid rows only) ===\n")
genre_count_quartiles = con.execute("""
    SELECT approx_quantile(genre_count, [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    FROM genres_flat
    WHERE genre_count > 0;
""").fetchdf()
print(genre_count_quartiles)

# ------------------------------------------------------------------
# Bucketed counts, filtered AND restricted to books_with_genres
# ------------------------------------------------------------------
print("\n=== Bucketed genre_count, valid rows, final corpus only ===\n")
filtered_books_genres = con.execute("""
    SELECT
        CASE
            WHEN g.genre_count = 1 THEN '1'
            WHEN g.genre_count = 2 THEN '2'
            WHEN g.genre_count BETWEEN 3 AND 5 THEN '3-5'
            WHEN g.genre_count BETWEEN 6 AND 10 THEN '6-10'
            WHEN g.genre_count BETWEEN 11 AND 20 THEN '11-20'
            ELSE '20+'
        END AS bucket,
        COUNT(*) AS n
    FROM genres_flat g
    JOIN books_with_genres b ON g.book_id = b.book_id
    WHERE g.genre_count > 0
    GROUP BY bucket
    ORDER BY MIN(g.genre_count);
""").fetchdf()
print(filtered_books_genres)

con.close()