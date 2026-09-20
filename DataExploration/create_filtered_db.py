
import duckdb

con = duckdb.connect("goodreads.duckdb")

# --- Step 1: load each genre file into its own staging table ---
genre_files = {
    "fantasy_paranormal": "goodreads_books_fantasy_paranormal.json.gz",
    "romance": "goodreads_books_romance.json.gz",
    "mystery_thriller_crime": "goodreads_books_mystery_thriller_crime.json.gz",
    "history_biography": "goodreads_books_history_biography.json.gz"
}




for name, path in genre_files.items():
    con.execute(f"""
        CREATE OR REPLACE TABLE staging_{name} AS
        SELECT *, '{name}' AS source_file
        FROM read_json_auto('data_source/{path}')
    """)

# --- Step 2: combine all genre staging tables into one ---
con.execute("""
    CREATE OR REPLACE TABLE books_raw_combined AS
    SELECT * FROM staging_fantasy_paranormal
    UNION ALL BY NAME
    SELECT * FROM staging_romance
    UNION ALL BY NAME
    SELECT * FROM staging_mystery_thriller_crime
    UNION ALL BY NAME
    SELECT * FROM staging_history_biography
""")

# --- Step 3: dedup on work_id, preferring rows with real descriptions ---
con.execute("""
    CREATE OR REPLACE TABLE books_deduped AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY work_id
                ORDER BY (description != '') DESC, CAST(ratings_count AS INT) DESC
            ) AS rn
        FROM books_raw_combined
    )
    WHERE rn = 1
""")

# --- Step 4: quality filter on description ---
con.execute("""
    CREATE OR REPLACE TABLE books_filtered AS
    SELECT * FROM books_deduped
    WHERE description != '' AND LENGTH(description) > 150
""")

# --- Step 5: load raw genres file (book_id -> {genre_name: count, ...}) ---
con.execute("""
    CREATE OR REPLACE TABLE genres_raw AS
    SELECT * FROM read_json_auto(
        'data_source/goodreads_book_genres_initial.json.gz',
        columns={'book_id': 'VARCHAR', 'genres': 'JSON'}
    )
""")

# --- Step 6: flatten the genres map into one row per (book_id, genre_name) ---
con.execute("""
    CREATE OR REPLACE TABLE genres_flat AS
    SELECT
        book_id,
        entry.key   AS genre_name,
        entry.value AS genre_count
    FROM (
        SELECT
            book_id,
            UNNEST(map_entries(CAST(genres AS MAP(VARCHAR, INTEGER)))) AS entry
        FROM genres_raw
    )
    WHERE entry.value > 0
""")

# --- Step 7: join genres onto filtered books (LEFT JOIN so no rows are dropped) ---
con.execute("""
    CREATE OR REPLACE TABLE books_with_genres AS
    SELECT
        b.*,
        STRING_AGG(g.genre_name, ', ') AS genres_text
    FROM books_filtered b
    LEFT JOIN genres_flat g
        ON b.book_id = g.book_id AND g.genre_count >= 3
    GROUP BY ALL
""")

# --- Step 8: export final table to Parquet ---
con.execute("""
    COPY books_with_genres TO 'books_final.parquet' (FORMAT PARQUET)
""")

# --- Step 9: print first 50 books to inspect ---
preview = con.execute("""
    SELECT title, description, genres_text, average_rating, ratings_count
    FROM books_with_genres
    LIMIT 50
""").fetchdf()

print(preview)
print("Script finished running")
con.close()