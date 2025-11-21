import sqlite3

def initialize_database():
    """Initialize the database - only run this manually when you want to reset"""
    conn = sqlite3.connect('Howls_DB.db')
    cur = conn.cursor()

    # TODO Create Tables
    # (1) Create Apothecary Inventory Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ApothecaryInventoryTable (
        Item_Id INTEGER PRIMARY KEY,
        Item_Name TEXT NOT NULL,
        Item_Price INTEGER,
        Item_Qoh INTEGER
    );""")

    # (2) Create Potions Pantry Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS PotionsPantryTable (
        Item_Id INTEGER PRIMARY KEY,
        Item_Name TEXT NOT NULL,
        Item_Description TEXT NOT NULL,
        Item_Recipe TEXT NOT NULL
    );""")

    # (3) RequestLedgerTable
    cur.execute("""
    CREATE TABLE IF NOT EXISTS RequestLedgerTable (
        Order_Id INTEGER PRIMARY KEY,
        Order_Customer_Name TEXT NOT NULL,
        Order_Apothecary TEXT NOT NULL,
        Order_PotionPantry TEXT NOT NULL,
        Activity_Status TEXT
    );""")

    # Clean Old Data
    cur.execute("DELETE FROM ApothecaryInventoryTable;")
    cur.execute("DELETE FROM PotionsPantryTable;")
    cur.execute("DELETE FROM RequestLedgerTable;")

    # TODO Insert Data
    # (1) Apothecary Inventory Table - Ingredients
    cur.executemany("""
    INSERT INTO ApothecaryInventoryTable (Item_Id, Item_Name, Item_Price, Item_Qoh)
    VALUES (?, ?, ?, ?);
    """, [
        (1, "Calcifer's Fallen Ember", 50, 10),
        (2, "Witch-of-the-Waste's Perfume Vapor", 48, 10),
        (3, "Moving Castle's Rust Flake", 23, 10),
        (4, "Tear of a Freed Scarecrow", 20, 10),
        (5, "Seven-League Boot Leather Scrap", 25, 10),
        (6, "Royal Dog Whisker", 35, 10),
        (7, "Pendant's Crystallized Starlight", 10, 10),
        (8, "Royal Intrigue Berry", 26, 10),
        (9, "Steam-Pipe Condensate", 29, 10),
        (10, "Mimic's Molted Feather", 21, 10),
        (11, "Turnip-Head's Nail", 18, 10),
        (12, "Royal Dog Loyalty Tear", 49, 10),
        (13, "Door-Knob's Whisper", 35, 10),
        (14, "Sulliman's Faded Sigil", 20, 10),
        (15, "Cursed Contract Ink", 5, 10)
    ])

    # (2) Potions Pantry Table - Potions
    cur.executemany("""
    INSERT INTO PotionsPantryTable (Item_Id, Item_Name, Item_Description, Item_Recipe)
    VALUES (?, ?, ?, ?);
    """, [
        (1, "Potion of Hearth's Homecoming", "When consumed, the next door you open will lead directly to the place you truly consider home", "1,3,7"),
        (2, "Elixir of the Unnoticed Journey", "Renders the drinker completely inconspicuous and unremarkable for several hours", "5,6,9"),
        (3, "Draught of Revealed Hearts", "Forces all who are under a glamour or emotional enchantment to reveal their true feelings and appearance", "2,7"),
        (4, "Vapour of Shifting Facades", "A smoke which causes a single inanimate object to cycle rapidly through a series of random appearances", "3,2,9"),
        (5, "Tincture of Loyal Retrieval", "When given to a creature, it will unerringly find a specific person or object", "6,4"),
        (6, "Potion of the Star's Bargain", "temporary, magical contract between two beings, binding them to a single, mutually agreed-upon task", "1,7"),
        (7, "Concoction of the Courtier's Clarity", "Allows the drinker to see the intricate web of loyalties, deceptions, and intentions of everyone in a room", "8,6,4"),
        (8, "Elixir of Winged Whispers", "Grants the drinker the ability to understand and speak the language of birds and minor spirits for one hour", "10,12"),
        (9, "Salve of the Stolen Face", "Allows the user to perfectly mimic another person's voice and appearance for a short time", "2,14,10"),
        (10, "Tonic of Unraveling Threads", "When poured on a magical construct or cursed object, it temporarily suspends its animation or enchantment", "11,9,3"),
        (11, "Philter of the Wandering Castle", "Causes a single building or vehicle to shift its location randomly every few minutes for one hour", "13,1,5"),
        (12, "Ink of Binding Vows", "Any contract written with this ink is magically binding; breaking it carries a severe, pre-defined consequence", "15,7")
    ])

    # (3) Request Ledger Table - Orders
    cur.executemany("""
    INSERT INTO RequestLedgerTable (Order_Id, Order_Customer_Name, Order_Apothecary, Order_PotionPantry, Activity_Status)
    VALUES (?, ?, ?, ?, ?);
    """, [
        (1, "Madame Suliman's Academy", "2,3", "104", "Requested"),
        (2, "The King's Royal Guard", "6,4,8", "105,107", "Ongoing"),
        (3, "The Witch of the Waste", "7,2", "103", "Completed"),
        (4, "Market Chipping Baker", "1,9", "101", "Requested"),
        (5, "Porthaven Fishermen's Guild", "5,6,9", "102", "Ongoing"),
        (6, "Royal Astrologer", "7,1", "106", "Completed"),
        (7, "Turnip-Head", "4,3", "101", "Requested"),
        (8, "Kingsbury Dressmaker", "10,2,14", "109", "Ongoing"),
        (9, "Royal Messenger Service", "15,7", "112", "Cannot Complete"),
        (10, "Calcifer", "1,9,3", "110", "Requested"),
        (11, "The Floating Market", "12,10", "108", "Ongoing"),
        (12, "Sophie Hatter", "13,1,5", "111", "Completed"),
        (13, "Royal Gardeners", "11,9,3", "110", "Requested"),
        (14, "Madame Suliman", "8,6,4", "107", "Ongoing"),
        (15, "The Moving Castle", "3,13,9", "104,111", "Completed"),
        (16, "Howl Jenkins Pendragon", "2,7,10", "103,109", "Requested"),
        (17, "Market Chipping Children's Home", "1,3,7", "101", "Ongoing"),
        (18, "Royal Library", "15,14", "112", "Cannot Complete"),
        (19, "The Waste Nomads", "5,6,4", "102,105", "Completed"),
        (20, "Kingsbury Clockmaker", "11,9", "110", "Requested")
    ])

    conn.commit()
    conn.close()
    print("Database initialized successfully with manual data!")

if __name__ == '__main__':
    initialize_database()
