"""
Run this once to import all values into the PostgreSQL database.
Usage: python migrate_values.py
"""
import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "")

VALUES = [
    # (name, value, shiny_value, demand, trend)
    # ===== LIMITED =====
    ("Radiance",        "600000",  "N/A",    10, "up"),
    ("Sinister Lord",   "550000",  "N/A",    10, "up"),
    ("Leviathan",       "350000",  "N/A",    10, "up"),
    ("Giant Robot",     "275000",  "N/A",    10, "up"),
    ("King Doggy",      "100000",  "N/A",    5,  "down"),
    ("Lord Shock",      "90000",   "525000", 10, "up"),
    ("Pot O' Gold",     "70000",   "445000", 10, "stable"),
    ("Patriotic Robot", "68000",   "435000", 10, "up"),
    ("Soul Heart",      "62000",   "400000", 10, "stable"),
    ("Ultimate Trophy", "60000",   "385000", 10, "stable"),
    ("Holy Bell",       "57500",   "365000", 10, "stable"),
    ("Tophat D",        "50000",   "225000", 7,  "up"),
    ("Tophat F",        "45000",   "215000", 7,  "up"),
    ("Kraken",          "42500",   "270000", 7,  "up"),
    ("Easter Basket",   "40000",   "255000", 7,  "stable"),
    ("Trophy",          "37500",   "240000", 7,  "stable"),
    ("Tophat E",        "32500",   "205000", 7,  "stable"),
    ("Tophat B",        "30000",   "N/A",    7,  "stable"),
    ("Tophat C",        "27500",   "175000", 7,  "stable"),
    ("Tophat A",        "25000",   "N/A",    5,  "stable"),
    ("Immortal One",    "20000",   "160000", 5,  "down"),
    ("Eternal Heart",   "15000",   "75000",  5,  "stable"),
    ("Dark Guardian",   "6500",    "44000",  5,  "down"),
    ("Frost Sentinel",  "0",       "N/A",    0,  "stable"),
    ("Robot 2.0",       "0",       "N/A",    0,  "stable"),
    ("Ultimate Clover", "0",       "N/A",    0,  "stable"),
    # ===== PERMANENT SECRET =====
    ("Fallen Angel",    "8500",    "N/A",    5,  "down"),
    ("Dogcat",          "8000",    "N/A",    5,  "down"),
    ("Rainbow Gryphon", "7250",    "36250",  5,  "down"),
    ("Rainbow DogCat",  "7000",    "N/A",    5,  "down"),
    ("Gryphon",         "6750",    "N/A",    5,  "down"),
    ("Giant Pearl",     "6250",    "31250",  5,  "down"),
    ("Sea Star",        "6000",    "30000",  5,  "down"),
    ("OwOLord",         "5000",    "25000",  5,  "down"),
    ("OG Overlord",     "3000",    "15000",  5,  "down"),
    # ===== PERMANENT LEGENDARY =====
    ("2018 Overlord",     "4500",  "25000",  7,  "up"),
    ("Ice Winged Hydra",  "2500",  "10000",  7,  "stable"),
    ("Diamond Overlord",  "1200",  "7000",   5,  "stable"),
    ("Valentium",         "850",   "6150",   5,  "stable"),
    ("Super Hexarium",    "800",   "6000",   5,  "stable"),
    ("Patriotic Penguin", "475",   "4000",   5,  "stable"),
    ("Platinum Overlord", "450",   "3500",   5,  "stable"),
    ("Chocolate Bunny",   "350",   "2500",   5,  "stable"),
    ("Queen Overlord",    "300",   "2750",   5,  "stable"),
    ("Summer Cerberus",   "275",   "2250",   5,  "stable"),
    ("Valentine Shock",   "225",   "1500",   5,  "stable"),
    ("Lucky Overlord",    "200",   "1450",   3,  "stable"),
    ("Radiant Protector", "175",   "1350",   3,  "stable"),
    ("Diamond Tamer",     "150",   "1200",   3,  "stable"),
    ("King Snowman",      "125",   "1100",   3,  "stable"),
    ("Dark Omen",         "100",   "800",    3,  "stable"),
]

def run():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    updated = 0
    skipped = 0
    for name, value, shiny, demand, trend in VALUES:
        cur.execute("SELECT id FROM pets WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            cur.execute(
                """UPDATE pets SET value = %s, shiny_value = %s, demand = %s, trend = %s,
                   updated_at = to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
                   WHERE name = %s""",
                (value, shiny, demand, trend, name)
            )
            updated += 1
        else:
            skipped += 1
            print(f"  SKIPPED (not found): {name}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"Done! Updated {updated} pets, skipped {skipped}.")

if __name__ == "__main__":
    run()


def fix_rarities():
    """Migrate old rarity names to new ones."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Limited -> Limited Secret
    cur.execute("UPDATE pets SET rarity = 'Limited Secret' WHERE rarity = 'Limited'")
    # Legendary -> Limited Legendary  
    cur.execute("UPDATE pets SET rarity = 'Limited Legendary' WHERE rarity = 'Legendary'")
    # Secret -> Permanent Secret
    cur.execute("UPDATE pets SET rarity = 'Permanent Secret' WHERE rarity = 'Secret'")
    conn.commit()
    rows = cur.rowcount
    cur.close()
    conn.close()
    print(f"Rarities fixed!")

if __name__ == "__main__":
    run()
    fix_rarities()
