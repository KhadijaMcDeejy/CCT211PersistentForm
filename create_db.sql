-- 1. Apothecary Table
-- (1) Potion Pantry Table (Apothecary)
-- [ingredient_id (int)][ingredient_name (str)][price (int)][quantity_on_hand (int)]
CREATE TABLE Apothecary (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name VARCHAR(100) UNIQUE NOT NULL,
    ingredient_price INTEGER NOT NULL,
    ingredient_qoh INTEGER NOT NULL,
    CHECK (ingredient_qoh BETWEEN 0 AND 1000)
);

-- 2. Potions Table
-- [potion_id (int)][potion_name (str)][effect (str)][required_ingredients:(int, int, ...)]
CREATE TABLE Potions (
    potion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    potion_name VARCHAR(100) UNIQUE NOT NULL,
    effect_description TEXT NOT NULL
);

-- Junction table for potion ingredients
CREATE TABLE Potion_Ingredients (
    potion_id INTEGER,
    ingredient_id INTEGER,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (potion_id, ingredient_id),
    FOREIGN KEY (potion_id) REFERENCES Potions(potion_id),
    FOREIGN KEY (ingredient_id) REFERENCES Apothecary(ingredient_id)
);

-- 3. Orders Table
-- [Customer Name (str)][Apothecary Order Item: (int, int,...)][Potion Order Item (int, int,...)]
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Junction tables for order items
CREATE TABLE Order_Ingredients (
    order_id INTEGER,
    ingredient_id INTEGER,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (order_id, ingredient_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (ingredient_id) REFERENCES Apothecary(ingredient_id)
);

CREATE TABLE Order_Potions (
    order_id INTEGER,
    potion_id INTEGER,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (order_id, potion_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (potion_id) REFERENCES Potions(potion_id)
);

-- NOTES
-- [required_ingredients:(int, int, ...)]  : tuple of ingredient id
-- [Apothecary Order Item: (int, int,...)] : tuple of ingredient id
-- [Potion Order Item (int, int,...)] : tuple of potion id
