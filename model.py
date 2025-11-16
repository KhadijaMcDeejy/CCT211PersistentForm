import csv, os
import tkinter as tk


class Model(tk.Frame):
    """
    Data Processing
    """
    FILENAME = "InventoryManagement.csv"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.CSV_PATH = os.path.join(os.path.dirname(__file__), self.FILENAME)
        self.COLUMNS = [
            "APOTHECARY", "PRICE", "INVENTORY",
            "POTIONS", "EFFECT", "RECIPE",
            "CUSTOMER", "APOTHECARY ORDER", "BREWERY ORDER", "ACTIVITY STATUS"]
        self.rows = self.load_rows()
        self.dicts = self.group()
        self.tree = None  # Will be set by the view

    def load_rows(self):
        """
        Read the CSV using DictReader.
        """
        for enc in ("utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(self.CSV_PATH, newline="", encoding=enc) as f:
                    return list(csv.DictReader(f))
            except Exception:
                pass
        raise RuntimeError("Cannot read CSV with common encodings. Check file path/encoding.")

    def save_rows(self):
        """
        Save rows back to CSV file.
        """
        try:
            with open(self.CSV_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
                writer.writeheader()
                writer.writerows(self.rows)
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False

    def add_potion_pantry_row(self, item, price, qoh):
        """
        Add a new row to potion pantry data.
        """
        new_row = {
            "APOTHECARY": item,
            "PRICE": price,
            "INVENTORY": qoh,
            "POTIONS": "",
            "EFFECT": "",
            "RECIPE": "",
            "CUSTOMER": "",
            "APOTHECARY ORDER": "",
            "BREWERY ORDER": "",
            "ACTIVITY STATUS": ""
        }
        self.rows.append(new_row)
        success = self.save_rows()
        if success:
            self.dicts = self.group()  # Regroup data
        return success

    def update_potion_pantry_row(self, old_item, old_price, old_qoh, new_item, new_price, new_qoh):
        """
        Update an existing potion pantry row.
        """
        # Find and update the row
        for row in self.rows:
            if (row.get("APOTHECARY", "").strip() == old_item and
                    row.get("PRICE", "").strip() == old_price and
                    row.get("INVENTORY", "").strip() == old_qoh):
                row["APOTHECARY"] = new_item
                row["PRICE"] = new_price
                row["INVENTORY"] = new_qoh
                break

        success = self.save_rows()
        if success:
            self.dicts = self.group()  # Regroup data
        return success

    def delete_potion_pantry_row(self, item, price, qoh):
        """
        Delete a potion pantry row.
        """
        # Find and remove the row
        self.rows = [row for row in self.rows if not (
                row.get("APOTHECARY", "").strip() == item and
                row.get("PRICE", "").strip() == price and
                row.get("INVENTORY", "").strip() == qoh
        )]

        success = self.save_rows()
        if success:
            self.dicts = self.group()  # Regroup data
        return success

    def group(self):
        """
        potion_pantry_dict[item][item_price][item_qoh] -> list of rows
        info_scroll_dict[potion][effect][recipe] -> list of rows
        request_scroll_dict[activity][customer][apothecary_order][brewer_order] -> list of rows
        """
        potion_pantry_dict = {}
        info_scroll_dict = {}
        request_scroll_dict = {}

        for r in self.rows:
            # potion_pantry_dict: item -> price -> qoh -> rows
            item = r.get("APOTHECARY", "").strip()
            item_price = r.get("PRICE", "").strip()
            item_qoh = r.get("INVENTORY", "").strip()
            if item:
                (potion_pantry_dict.setdefault(item, {})
                 .setdefault(item_price, {})
                 .setdefault(item_qoh, []).append(r))

            # info_scroll_dict: potion -> effect -> recipe -> rows
            potion = r.get("POTIONS", "").strip()
            effect = r.get("EFFECT", "").strip()
            recipe = r.get("RECIPE", "").strip()
            if potion:
                (info_scroll_dict.setdefault(potion, {})
                 .setdefault(effect, {})
                 .setdefault(recipe, []).append(r))

            # request_scroll_dict: activity -> customer -> apothecary_order -> brewer_order -> rows
            activity = r.get("ACTIVITY STATUS", "").strip()
            customer = r.get("CUSTOMER", "").strip()
            apothecary_order = r.get("APOTHECARY ORDER", "").strip()
            brewer_order = r.get("BREWERY ORDER", "").strip()
            if activity:
                (request_scroll_dict.setdefault(activity, {})
                 .setdefault(customer, {})
                 .setdefault(apothecary_order, {})
                 .setdefault(brewer_order, []).append(r))

        return {
            "potion_pantry": potion_pantry_dict,
            "info_scroll": info_scroll_dict,
            "request_scroll": request_scroll_dict
        }

    def LoadData(self, tree_widget):
        """
        Load the grouped data into a treeview widget.
        """
        self.tree = tree_widget
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        # Load each dictionary section
        self._load_potion_pantry()
        self._load_info_scroll()
        self._load_request_scroll()

    def _load_potion_pantry(self):
        """Load potion pantry data into treeview"""
        potion_data = self.dicts["potion_pantry"]
        bank_iid = "bank:potion_pantry"
        self.tree.insert("", "end", iid=bank_iid, text="Potion Pantry")

        for item, price_data in potion_data.items():
            item_iid = f"{bank_iid}|item:{item}"
            self.tree.insert(bank_iid, "end", iid=item_iid, text=item)

            for price, qoh_data in price_data.items():
                price_iid = f"{item_iid}|price:{price}"
                self.tree.insert(item_iid, "end", iid=price_iid, text=f"Price: {price}")

                for qoh, rows in qoh_data.items():
                    qoh_iid = f"{price_iid}|qoh:{qoh}"
                    self.tree.insert(price_iid, "end", iid=qoh_iid, text=f"QOH: {qoh}")

                    for i, r in enumerate(rows):
                        leaf_iid = f"{qoh_iid}|row:{i}"
                        self.tree.insert(
                            qoh_iid, "end", iid=leaf_iid, text="",
                            values=[r.get(col, "") for col in self.COLUMNS]
                        )

        self.tree.item(bank_iid, open=True)

    def _load_info_scroll(self):
        """Load info scroll data into treeview"""
        info_data = self.dicts["info_scroll"]
        bank_iid = "bank:info_scroll"
        self.tree.insert("", "end", iid=bank_iid, text="Info Scroll")

        for potion, effect_data in info_data.items():
            potion_iid = f"{bank_iid}|potion:{potion}"
            self.tree.insert(bank_iid, "end", iid=potion_iid, text=potion)

            for effect, recipe_data in effect_data.items():
                effect_iid = f"{potion_iid}|effect:{effect}"
                self.tree.insert(potion_iid, "end", iid=effect_iid, text=f"Effect: {effect}")

                for recipe, rows in recipe_data.items():
                    recipe_iid = f"{effect_iid}|recipe:{recipe}"
                    self.tree.insert(effect_iid, "end", iid=recipe_iid, text=f"Recipe: {recipe}")

                    for i, r in enumerate(rows):
                        leaf_iid = f"{recipe_iid}|row:{i}"
                        self.tree.insert(
                            recipe_iid, "end", iid=leaf_iid, text="",
                            values=[r.get(col, "") for col in self.COLUMNS]
                        )

        self.tree.item(bank_iid, open=True)

    def _load_request_scroll(self):
        """Load request scroll data into treeview"""
        request_data = self.dicts["request_scroll"]
        bank_iid = "bank:request_scroll"
        self.tree.insert("", "end", iid=bank_iid, text="Request Scroll")

        for activity, customer_data in request_data.items():
            activity_iid = f"{bank_iid}|activity:{activity}"
            self.tree.insert(bank_iid, "end", iid=activity_iid, text=activity)

            for customer, order_data in customer_data.items():
                customer_iid = f"{activity_iid}|customer:{customer}"
                self.tree.insert(activity_iid, "end", iid=customer_iid, text=customer)

                for apoth_order, brewer_data in order_data.items():
                    order_iid = f"{customer_iid}|apoth_order:{apoth_order}"
                    self.tree.insert(customer_iid, "end", iid=order_iid, text=f"Apothecary Order: {apoth_order}")

                    for brewer_order, rows in brewer_data.items():
                        brewer_iid = f"{order_iid}|brewer_order:{brewer_order}"
                        self.tree.insert(order_iid, "end", iid=brewer_iid, text=f"Brewer Order: {brewer_order}")

                        for i, r in enumerate(rows):
                            leaf_iid = f"{brewer_iid}|row:{i}"
                            self.tree.insert(
                                brewer_iid, "end", iid=leaf_iid, text="",
                                values=[r.get(col, "") for col in self.COLUMNS]
                            )

        self.tree.item(bank_iid, open=True)

    def on_select(self, event):
        """
        Called when the selection changes.
        We only show detailed info if the selected item is a leaf (i.e., it has values).
        Group nodes (bank/card-type) have no 'values' and are ignored here.
        """
        if not self.tree:
            return

        sel = self.tree.selection()
        if not sel:
            return

        item_id = sel[0]
        values = self.tree.item(item_id, "values")

        if values and len(values) == len(self.COLUMNS):
            # Leaf node with full data
            apothecary = values[0] or "N/A"
            potion = values[3] or "N/A"
            customer = values[6] or "N/A"
            status = f"Selected: {apothecary} | {potion} | {customer}"
        else:
            # Group node - show the text label
            text = self.tree.item(item_id, "text")
            status = f"Group: {text}"

        # Update status if available in the parent
        if hasattr(self, 'status'):
            self.status.set(status)
        else:
            print(status)  # Fallback to console output

    def get_filtered_data(self, filter_type, filter_value):
        """
        Get filtered data based on type and value.
        """
        if filter_type == "apothecary":
            return self._filter_by_apothecary(filter_value)
        elif filter_type == "potion":
            return self._filter_by_potion(filter_value)
        elif filter_type == "customer":
            return self._filter_by_customer(filter_value)
        else:
            return self.rows

    def _filter_by_apothecary(self, apothecary_name):
        """Filter rows by apothecary name"""
        return [r for r in self.rows if r.get("APOTHECARY", "").strip() == apothecary_name]

    def _filter_by_potion(self, potion_name):
        """Filter rows by potion name"""
        return [r for r in self.rows if r.get("POTIONS", "").strip() == potion_name]

    def _filter_by_customer(self, customer_name):
        """Filter rows by customer name"""
        return [r for r in self.rows if r.get("CUSTOMER", "").strip() == customer_name]

    def update(self):
        """Reload data from CSV and regroup"""
        self.rows = self.load_rows()
        self.dicts = self.group()
