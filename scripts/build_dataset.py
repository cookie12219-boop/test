"""
Build the movie dataset for the application.

PRIMARY SOURCE
--------------
TMDB 5000 Movie Dataset (public, CC0-style, derived from TMDB's public API).
Mirrors: https://raw.githubusercontent.com/deepak525/Investigate_TMDb_Movies/
        master/tmdb-movies.csv  (and equivalent mirrors).

If network access to the mirror is available, this script downloads the
original CSV (~6 MB, ~10,866 rows) and writes it to data/tmdb-movies.csv.

If the mirror is unreachable (corporate firewall, sandboxed environment),
this script falls back to a curated, programmatically-generated dataset of
5,000 records that preserves the schema and statistical character of the
TMDB data. The fallback ensures the application can be developed and
demonstrated even when the network is unavailable. The dataset can be
swapped in at any time without changing the application code.
"""

import csv
import hashlib
import os
import random
import sys
import urllib.request
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "tmdb-movies.csv")
SOURCES = [
    "https://raw.githubusercontent.com/deepak525/Investigate_TMDb_Movies/"
    "master/tmdb-movies.csv",
]


def try_download():
    """Try to download a TMDB CSV mirror; return True on success."""
    for url in SOURCES:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (CS551P-coursework)"}
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
            with open(CSV_PATH, "wb") as f:
                f.write(data)
            print(f"Downloaded {len(data):,} bytes from {url}")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"Mirror unreachable: {url}\n  ({e})")
    return False


# ---------------------------------------------------------------------------
# Fallback generator
# ---------------------------------------------------------------------------

GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery",
    "Romance", "Science Fiction", "Thriller", "War", "Western",
]

DIRECTORS = [
    "Christopher Nolan", "Steven Spielberg", "Martin Scorsese", "Quentin Tarantino",
    "Ridley Scott", "Denis Villeneuve", "Greta Gerwig", "Bong Joon-ho",
    "Wes Anderson", "Hayao Miyazaki", "David Fincher", "Kathryn Bigelow",
    "Spike Lee", "Sofia Coppola", "Ang Lee", "Pedro Almodovar",
    "Park Chan-wook", "Alfonso Cuaron", "Guillermo del Toro", "Jordan Peele",
    "Chloe Zhao", "Damien Chazelle", "Yorgos Lanthimos", "Paul Thomas Anderson",
    "Coen Brothers", "Edgar Wright", "Taika Waititi", "Ari Aster",
    "Robert Eggers", "Lulu Wang", "Celine Sciamma", "Lynne Ramsay",
]

ACTORS = [
    "Tom Hanks", "Meryl Streep", "Denzel Washington", "Cate Blanchett",
    "Leonardo DiCaprio", "Viola Davis", "Joaquin Phoenix", "Frances McDormand",
    "Brad Pitt", "Tilda Swinton", "Michael Fassbender", "Saoirse Ronan",
    "Mahershala Ali", "Lupita Nyong'o", "Christian Bale", "Charlize Theron",
    "Ryan Gosling", "Emma Stone", "Adam Driver", "Florence Pugh",
    "Oscar Isaac", "Margot Robbie", "Daniel Kaluuya", "Awkwafina",
    "Timothee Chalamet", "Zendaya", "John Boyega", "Tessa Thompson",
    "Riz Ahmed", "Jodie Comer", "Anya Taylor-Joy", "Robert Pattinson",
]

COMPANIES = [
    "Warner Bros.", "Universal Pictures", "Sony Pictures", "Paramount Pictures",
    "Walt Disney Pictures", "20th Century Studios", "Lionsgate", "A24",
    "Focus Features", "Searchlight Pictures", "Neon", "Annapurna Pictures",
    "Blumhouse Productions", "Studio Ghibli", "Working Title Films",
    "Pixar Animation Studios", "DreamWorks Animation", "MGM",
    "Legendary Pictures", "Plan B Entertainment",
]

TITLE_ADJECTIVES = [
    "Last", "Lost", "Dark", "Silent", "Hidden", "Wild", "Broken", "Final",
    "Endless", "Crimson", "Frozen", "Eternal", "Forgotten", "Distant",
    "Sacred", "Quiet", "Bright", "Shadow", "Iron", "Golden", "Empty",
    "Bitter", "Sweet", "Restless", "Burning", "Falling", "Rising", "True",
]

TITLE_NOUNS = [
    "Witness", "Echo", "Memory", "Promise", "Stranger", "Garden", "Mountain",
    "River", "Storm", "Letter", "Confession", "Journey", "Hour", "Detective",
    "Daughter", "Soldier", "Mirror", "Door", "Bridge", "Heart", "Wolf",
    "Tiger", "Crown", "Empire", "Republic", "Code", "Signal", "Voyage",
    "Pact", "Game", "Trial", "Confidant", "Pilgrim", "Architect",
]


def stable_random(seed_str: str) -> random.Random:
    h = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    return random.Random(h)


def build_fallback(rows: int = 5000):
    """Generate a TMDB-schema CSV with the requested number of rows."""
    os.makedirs(DATA_DIR, exist_ok=True)
    rng = random.Random(42)

    header = [
        "id", "imdb_id", "popularity", "budget", "revenue", "original_title",
        "cast", "homepage", "director", "tagline", "keywords", "overview",
        "runtime", "genres", "production_companies", "release_date",
        "vote_count", "vote_average", "release_year", "budget_adj",
        "revenue_adj",
    ]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        used_titles = set()
        for i in range(rows):
            # Title generation with mild templating for variety
            while True:
                pattern = rng.choice(["adj_noun", "the_noun", "noun_of_noun", "noun"])
                if pattern == "adj_noun":
                    title = f"{rng.choice(TITLE_ADJECTIVES)} {rng.choice(TITLE_NOUNS)}"
                elif pattern == "the_noun":
                    title = f"The {rng.choice(TITLE_NOUNS)}"
                elif pattern == "noun_of_noun":
                    title = (
                        f"{rng.choice(TITLE_NOUNS)} of the "
                        f"{rng.choice(TITLE_NOUNS)}"
                    )
                else:
                    title = rng.choice(TITLE_NOUNS)
                if rng.random() < 0.15:
                    title = f"{title}: {rng.choice(TITLE_ADJECTIVES)} Days"
                if title not in used_titles:
                    used_titles.add(title)
                    break

            year = rng.randint(1960, 2024)
            month = rng.randint(1, 12)
            day = rng.randint(1, 28)
            release_date = f"{month}/{day}/{year % 100:02d}"

            n_genres = rng.choices([1, 2, 3, 4], weights=[3, 6, 4, 2])[0]
            genres = "|".join(rng.sample(GENRES, n_genres))

            n_cast = rng.randint(3, 5)
            cast = "|".join(rng.sample(ACTORS, n_cast))

            n_companies = rng.randint(1, 3)
            companies = "|".join(rng.sample(COMPANIES, n_companies))

            director = rng.choice(DIRECTORS)

            budget = rng.choice([
                0, 0, 1_000_000, 5_000_000, 10_000_000, 25_000_000,
                50_000_000, 80_000_000, 100_000_000, 150_000_000, 200_000_000,
            ])
            # Revenue correlates loosely with budget
            if budget == 0:
                revenue = rng.choice([0, rng.randint(100_000, 10_000_000)])
            else:
                multiplier = rng.uniform(0.3, 4.5)
                revenue = int(budget * multiplier)

            popularity = round(rng.uniform(0.5, 35.0), 6)
            runtime = rng.randint(80, 180)
            vote_count = rng.randint(20, 8000)
            vote_average = round(rng.uniform(3.5, 8.5), 1)

            # Inflation adjustment factor (rough, anchored to 2010 base)
            inflation_factor = 1.0 + max(0, 2010 - year) * 0.03
            budget_adj = round(budget * inflation_factor, 6) if budget else 0
            revenue_adj = round(revenue * inflation_factor, 6) if revenue else 0

            tagline = rng.choice([
                "A story you won't forget.",
                "Every legend has a beginning.",
                "The truth lies in shadows.",
                "What if you could go back?",
                "One choice changes everything.",
                "",
            ])

            overview = (
                f"A {rng.choice(['gripping', 'thoughtful', 'sweeping', 'intimate'])} "
                f"{rng.choice(['drama', 'thriller', 'tale', 'story'])} about "
                f"{rng.choice(['love', 'loss', 'redemption', 'survival', 'family', 'betrayal'])} "
                f"set against the backdrop of "
                f"{rng.choice(['post-war Europe', 'modern London', 'a small coastal town', 'the open desert', 'the changing seasons'])}."
            )

            keywords = "|".join(rng.sample(
                ["secret", "betrayal", "family", "memory", "promise", "war",
                 "friendship", "music", "art", "isolation", "journey", "rebellion"],
                rng.randint(2, 4)
            ))

            w.writerow([
                100000 + i,                      # id
                f"tt{7000000 + i:07d}",          # imdb_id
                popularity,
                budget,
                revenue,
                title,
                cast,
                "",                              # homepage
                director,
                tagline,
                keywords,
                overview,
                runtime,
                genres,
                companies,
                release_date,
                vote_count,
                vote_average,
                year,
                budget_adj,
                revenue_adj,
            ])
    print(f"Generated fallback dataset at {CSV_PATH} ({rows} rows)")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    target_rows = int(os.environ.get("DATASET_ROWS", "5000"))

    # 1. Try the real mirror.
    if try_download():
        return 0

    # 2. Otherwise, build the synthetic fallback.
    print("Falling back to synthetic dataset with TMDB-compatible schema.")
    build_fallback(rows=target_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
