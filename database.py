import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def dict_row(cur, row):
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def dict_rows(cur, rows):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id              SERIAL PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            rarity          TEXT NOT NULL,
            value           TEXT NOT NULL DEFAULT '0',
            shiny_value     TEXT,
            image_url       TEXT,
            shiny_image_url TEXT,
            note            TEXT,
            exists_normal   INTEGER DEFAULT 0,
            exists_shiny    INTEGER DEFAULT 0,
            demand          INTEGER DEFAULT 0,
            trend           TEXT DEFAULT 'stable',
            created_at      TEXT NOT NULL DEFAULT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'),
            updated_at      TEXT NOT NULL DEFAULT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS value_history (
            id          SERIAL PRIMARY KEY,
            pet_id      INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            pet_name    TEXT NOT NULL,
            old_value   TEXT NOT NULL,
            new_value   TEXT NOT NULL,
            old_shiny   TEXT,
            new_shiny   TEXT,
            changed_by  TEXT NOT NULL DEFAULT 'admin',
            reason      TEXT,
            changed_at  TEXT NOT NULL DEFAULT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id            SERIAL PRIMARY KEY,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
        )
    """)

    safe_columns = [
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS image_url TEXT",
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS shiny_image_url TEXT",
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS exists_normal INTEGER DEFAULT 0",
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS exists_shiny INTEGER DEFAULT 0",
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS demand INTEGER DEFAULT 0",
        "ALTER TABLE pets ADD COLUMN IF NOT EXISTS trend TEXT DEFAULT 'stable'",
    ]
    for sql in safe_columns:
        try:
            cur.execute(sql)
        except Exception:
            conn.rollback()

    conn.commit()
    cur.close()
    conn.close()


SEED_PETS = [
    ("Giant Robot",       "Limited",   "0", "0",  "Only 7 in existence"),
    ("Leviathan",         "Limited",   "0", None, None),
    ("Sinister Lord",     "Limited",   "0", "0",  None),
    ("Robot 2.0",         "Limited",   "0", "0",  None),
    ("Radiance",          "Limited",   "0", "0",  None),
    ("Easter Basket",     "Limited",   "0", "0",  None),
    ("Trophy",            "Limited",   "0", "0",  None),
    ("Lord Shock",        "Limited",   "0", "0",  None),
    ("Pot O' Gold",       "Limited",   "0", "0",  None),
    ("Kraken",            "Limited",   "0", "0",  None),
    ("Soul Heart",        "Limited",   "0", "0",  None),
    ("Immortal One",      "Limited",   "0", "0",  None),
    ("Patriotic Robot",   "Limited",   "0", "0",  None),
    ("Holy Bell",         "Limited",   "0", "0",  None),
    ("Frost Sentinel",    "Limited",   "0", "0",  None),
    ("Ultimate Clover",   "Limited",   "0", "0",  None),
    ("Ultimate Trophy",   "Limited",   "0", "0",  None),
    ("Dark Guardian",     "Limited",   "0", "0",  None),
    ("Eternal Heart",     "Limited",   "0", "0",  None),
    ("Tophat A",          "Limited",   "0", "0",  None),
    ("Tophat B",          "Limited",   "0", "0",  None),
    ("Tophat C",          "Limited",   "0", "0",  None),
    ("Tophat D",          "Limited",   "0", "0",  None),
    ("Tophat E",          "Limited",   "0", "0",  None),
    ("Tophat F",          "Limited",   "0", "0",  None),
    ("King Doggy",        "Secret",    "0", "0",  None),
    ("Giant Pearl",       "Secret",    "0", "0",  None),
    ("Gryphon",           "Secret",    "0", "0",  None),
    ("Fallen Angel",      "Secret",    "0", "0",  None),
    ("Sea Star",          "Secret",    "0", "0",  None),
    ("OwOLord",           "Secret",    "0", "0",  None),
    ("Dogcat",            "Secret",    "0", "0",  None),
    ("OG Overlord",       "Secret",    "0", "0",  None),
    ("Rainbow Gryphon",   "Secret",    "0", "0",  None),
    ("Rainbow DogCat",    "Secret",    "0", "0",  None),
    ("2018 Overlord",     "Legendary", "0", "0",  None),
    ("Diamond Overlord",  "Legendary", "0", "0",  None),
    ("Valentium",         "Legendary", "0", "0",  None),
    ("Patriotic Penguin", "Legendary", "0", "0",  None),
    ("Chocolate Bunny",   "Legendary", "0", "0",  None),
    ("Super Hexarium",    "Legendary", "0", "0",  None),
    ("Platinum Overlord", "Legendary", "0", "0",  None),
    ("Queen Overlord",    "Legendary", "0", "0",  None),
    ("Radiant Protector", "Legendary", "0", "0",  None),
    ("Lucky Overlord",    "Legendary", "0", "0",  None),
    ("Summer Cerberus",   "Legendary", "0", "0",  None),
    ("Diamond Tamer",     "Legendary", "0", "0",  None),
    ("King Snowman",      "Legendary", "0", "0",  None),
    ("Dark Omen",         "Legendary", "0", "0",  None),
    ("Valentine Shock",   "Legendary", "0", "0",  None),
]


def seed_db():
    conn = get_conn()
    cur = conn.cursor()
    for name, rarity, value, shiny, note in SEED_PETS:
        cur.execute(
            """
            INSERT INTO pets (name, rarity, value, shiny_value, note)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            """,
            (name, rarity, value, shiny, note),
        )
    conn.commit()
    cur.close()
    conn.close()


def cleanup_db():
    approved = {name for name, *_ in SEED_PETS}
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM pets")
    all_pets = cur.fetchall()
    for pet_id, pet_name in all_pets:
        if pet_name not in approved:
            cur.execute("DELETE FROM pets WHERE id = %s", (pet_id,))

    for name, rarity, *_ in SEED_PETS:
        cur.execute(
            "UPDATE pets SET rarity = %s WHERE name = %s AND rarity != %s",
            (rarity, name, rarity)
        )

    conn.commit()
    cur.close()
    conn.close()
