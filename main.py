#CCT211 Assignment 2--Persistent Form
#Comments:

from cProfile import label
import tkinter as tk
from tkinter import ttk, messagebox
import model

#GLOBAL THEME (consistent widget rendering on macOS + Windows)
def configure_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")   #uses the "CLAM" style to ensure its consistent across both OS systems; replaces the default Aqua theme on macOS

    #Configures consistent styling across ALL widgets
    style.configure("TEntry", padding = 4)
    style.configure("TButton", padding = 6)
    style.configure("TLabel", background = "white")
    style.configure("NavButton.TButton", background = "white")

    #NAVIGATION Styling
    style.configure("NavButton.TButton", font = ("Verdana", 10), background = "white") #when unactive
    style.configure("BoldNav.TButton", font = ("Verdana", 10, "bold"), background = "white") #when active

    style.map("Treeview.Heading",background=[],relief=[])
    style.map("Vertical.TScrollbar", background=[], arrowcolor=[])

#the NAVIGATION
class NavigationBar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white", bd = .5, relief = "solid")
        self.controller = controller
        self.nav_buttons = {}

        nav_items = [ #list of NAVIGATION items
            ("Overview", OverviewPage), #Overview / Welcome Chamber
            ("Potion Pantry", PotionPantryPage), #Inventory / Potion Pantry
            ("Request Scrolls", RequestScrollsPage), #Orders / Request Scrolls
        ]

        #MENU ITEMS (displayed using button widgets to show user activity and sub options were not needed)
        for text, page_class in nav_items:
            navBtn = ttk.Button(
                self,
                text = text,
                style = "NavButton.TButton",
                command = lambda p = page_class: controller.show_frame(p)
            )
            navBtn.pack(side = "left", padx = 18)
            self.nav_buttons[page_class] = navBtn

        #WELCOME MENU item (displayed on the right side of the menu; welcomes whichever user who signed in)
        self.welcome_label = ttk.Label(
            self,
            text = "Welcome!",
            font = ("Verdana", 10, "italic"),
        )
        self.welcome_label.pack(side = "right", padx = 18)

    #UPDATES ACTIVE FRAME (based on user interactions)
    def update_active(self, active_page):
        for page_class, button in self.nav_buttons.items():
            if page_class == active_page:
                button.config(style = "BoldNav.TButton")
            else:
                button.config(style = "NavButton.TButton")

    def refresh_username(self):
        username = self.controller.username
        if username:
            self.welcome_label.config(text = f"Welcome {username.capitalize()}!")
        else:
            self.welcome_label.config(text = "Welcome!")

# Main Application
class CalcifersLedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcifer’s Ledger - Magic Record Keeping System")
        self.root.geometry("1200x600")

        self.valid_logins = {
            "howl": "fire123",
            "sophie": "howlcastle",
            "calcifer": "flame!"
        }

        self.username = None #intializes the username of whom has logged into the application
        self.model = model.Model()

        container = tk.Frame(self.root, bg = "white")
        container.pack(fill = "both", expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        # INITIALIZES all of our pages
        for Page in (LoginPage, OverviewPage, PotionPantryPage, RequestScrollsPage):
            frame = Page(parent = container, controller = self)
            self.frames[Page] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(PotionPantryPage) #SHOWS THE LOGIN PAGE FRAME

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

        #ONLY Updates active nav items when relevant (when the user interacts with them)
        if hasattr(frame, "nav_frame"):
            frame.nav_frame.refresh_username()
            frame.nav_frame.update_active(page_class) #updates active section of the navigation (BOLDS IT)

# Windows in Application
class LoginPage(tk.Frame):
     def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")
        self.controller = controller

        center_frame = tk.Frame(self, bg = "white")
        center_frame.place(relx = 0.5, rely = 0.5, anchor = "center")

        #LOGIN TITLE
        title_frame = tk.Frame(center_frame, bg = "white", bd = 2, relief = "solid")
        title_frame.pack(pady = (0, 16))

        ttk.Label( #HEADER TITLE
            title_frame,
            text = "Calcifer’s Ledger",
            font = ("Palatino", 50, "bold"),
        ).pack()

        ttk.Label( #SUBHEADER TITLE
            title_frame,
            text = "Magic Record Keeping System",
            font = ("Verdana", 13),
        ).pack(pady=(0, 8))

        #FORM area (centered within center_frame)
        form_frame = tk.Frame(center_frame, bg = "white")
        form_frame.pack()

        #LOGIN ROW
        login_row = tk.Frame(form_frame, bg = "white") #the login form row
        login_row.pack(anchor = "center", pady = 6)
        ttk.Label(login_row, text = "Login:", font = ("Verdana", 12)).pack(side = "left", padx = (0, 8))
        #LOGIN ENTRY
        self.login_entry = ttk.Entry(login_row, width = 25)
        self.login_entry.pack(side = "left")

        #PASSWORD ROW
        pass_row = tk.Frame(form_frame, bg = "white") #the password form row
        pass_row.pack(anchor = "center", pady = 6)
        ttk.Label(pass_row, text = "Password:", font = ("Verdana", 12)).pack(side = "left", padx = (0, 8))
        #PASS ENTRY
        self.password_entry = ttk.Entry(pass_row, width = 25, show = "*")
        self.password_entry.pack(side = "left")

        #BUTTON
        btn_row = tk.Frame(center_frame, bg = "white")
        btn_row.pack(pady = 14)
        ttk.Button(
            btn_row,
            text = "Login",
            command = self.check_login
        ).pack()

     def check_login(self):
        username = self.login_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        valid_logins = self.controller.valid_logins

        if username in valid_logins and valid_logins[username] == password:
            messagebox.showinfo("Access Granted", f"Welcome, {username.capitalize()}!")

            overview_page = self.controller.frames[OverviewPage]
            self.controller.username = username #Updates the NAVIGATION with the username of whom logged in

            self.controller.show_frame(OverviewPage) #Switches to the overview frame
        else:
            messagebox.showerror("Access Denied", "Invalid login or password.")
            self.password_entry.delete(0, tk.END)

class OverviewPage(tk.Frame): #OVERVIEW (known as the Welcome Chamber in the menu)
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")
        self.controller = controller

        #initializes the NAVIGATION BAR in the overview page
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill = "x", pady = 5)

        label1 = ttk.Label(self, text = "OverviewPage test").pack() #TESTING

class PotionPantryPage(tk.Frame):  # INVENTORY
    def __init__(self, parent, controller):
        super().__init__(parent, bg="blanched almond")
        self.controller = controller
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill="x", pady=0)

        info_button = ttk.Button(self, text="[Info]", command=self.show_info)
        info_button.pack(side="bottom", anchor="nw", padx=20, pady=(5,10))

        content_frame = tk.Frame(self, bg="black")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        self.create_inventory_table(content_frame)

        # Bind keyboard shortcuts to the treeview
        self.tree.bind("<KeyPress>", self.handle_keypress)

    def handle_keypress(self, event):
        """Handle keyboard shortcuts"""
        if event.keysym.lower() == 'e':
            self.edit_row()
        elif event.keysym.lower() == 'a':
            self.add_row()
        elif event.keysym == 'Delete':
            self.delete_row()

    def create_inventory_table(self, parent):
        """Create the inventory table that corresponds to potion_pantry dict"""
        style = ttk.Style()
        style.configure("Treeview",
                        font=("Verdana", 20),
                        rowheight=40,
                        background="lemon chiffon",
                        fieldbackground="lemon chiffon")

        style.configure("Treeview.Heading",
                        font=("Verdana", 13, "bold"),
                        background="MistyRose2")

        style.configure("Vertical.TScrollbar",
                        background="MistyRose2",
                        fieldbackground="white")

        self.tree = ttk.Treeview(parent,
                                 columns=("Item", "Price", "QoH"),
                                 show="headings", height=15)
        columns = [
            ("Item", 600),
            ("Price", 200),
            ("QoH", 200)
        ]
        for col, width in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        # Set focus to treeview so it can receive keyboard events
        self.tree.focus_set()

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.load_inventory_data()

    def show_info(self):
        """Show info message about keyboard shortcuts"""
        messagebox.showinfo("Keyboard Shortcuts",
                            "E - Edit selected row\n"
                            "A - Add new row\n"
                            "Click on a row to select it first.")

    def edit_row(self):
        """Edit the selected row"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to edit.")
            return

        item = selected[0]
        current_values = self.tree.item(item, 'values')

        # Create edit dialog
        self.create_edit_dialog("Edit Row", current_values, item)

    def add_row(self):
        """Add a new row"""
        self.create_edit_dialog("Add New Row", ("", "", ""), None)

    def delete_row(self):
        """Delete the selected row"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return

        item = selected[0]
        values = self.tree.item(item, 'values')

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n"
            f"Item: {values[0]}\n"
            f"Price: {values[1]}\n"
            f"QoH: {values[2]}"
        )

        if confirm:
            # Delete from model
            success = self.controller.model.delete_potion_pantry_row(
                values[0], values[1], values[2]
            )
            if success:
                messagebox.showinfo("Success", "Row deleted successfully!")
                self.load_inventory_data()  # Refresh table
            else:
                messagebox.showerror("Error", "Failed to delete row from file.")

    def save_changes(self, dialog, item_entry, price_entry, qoh_entry, item, current_values):
        """Save changes to the model and refresh the table"""
        new_values = (
            item_entry.get().strip(),
            price_entry.get().strip(),
            qoh_entry.get().strip()
        )

        if not new_values[0]:
            messagebox.showerror("Error", "Item name cannot be empty.")
            return

        success = False
        if item is None:  # Adding new row
            # Add to model
            success = self.controller.model.add_potion_pantry_row(
                new_values[0], new_values[1], new_values[2]
            )
            if success:
                messagebox.showinfo("Success", "New row added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add new row to file.")
        else:  # Editing existing row
            # Update in model
            success = self.controller.model.update_potion_pantry_row(
                current_values[0], current_values[1], current_values[2],  # old values
                new_values[0], new_values[1], new_values[2]  # new values
            )
            if success:
                messagebox.showinfo("Success", "Row updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update row in file.")

        if success:
            self.load_inventory_data()  # Refresh table to show updated data
            dialog.destroy()

    def create_edit_dialog(self, title, current_values, item):
        """Create dialog for editing/adding rows"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.configure(bg="blanched almond")
        dialog.transient(self)  # Set to be on top of the main window
        dialog.grab_set()  # Modal dialog

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Form frame
        form_frame = tk.Frame(dialog, bg="blanched almond", padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        # Item field
        ttk.Label(form_frame, text="Item:", background="blanched almond").grid(row=0, column=0, sticky="w", pady=5)
        item_entry = ttk.Entry(form_frame, width=30, font=("Verdana", 12))
        item_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        item_entry.insert(0, current_values[0])
        item_entry.focus_set()  # Focus on first field

        # Price field
        ttk.Label(form_frame, text="Price:", background="blanched almond").grid(row=1, column=0, sticky="w", pady=5)
        price_entry = ttk.Entry(form_frame, width=30, font=("Verdana", 12))
        price_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        price_entry.insert(0, current_values[1])

        # QoH field
        ttk.Label(form_frame, text="QoH:", background="blanched almond").grid(row=2, column=0, sticky="w", pady=5)
        qoh_entry = ttk.Entry(form_frame, width=30, font=("Verdana", 12))
        qoh_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        qoh_entry.insert(0, current_values[2])

        # Button frame
        button_frame = tk.Frame(form_frame, bg="blanched almond")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        def save_and_close():
            self.save_changes(dialog, item_entry, price_entry, qoh_entry, item, current_values)

        def cancel():
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_and_close).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=10)

        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_and_close())
        # Bind Escape key to cancel
        dialog.bind('<Escape>', lambda e: cancel())

        # Make form responsive
        form_frame.columnconfigure(1, weight=1)

    def load_inventory_data(self):
        """Load data from model's potion_pantry dict into the table"""
        self.tree.delete(*self.tree.get_children())
        if hasattr(self.controller, 'model'):
            try:
                # Refresh the model data first
                self.controller.model.update()
                pantry_data = self.controller.model.dicts["potion_pantry"]

                if not pantry_data:
                    self.tree.insert("", "end", values=("No data found", "", ""))
                    return

                for item, price_data in pantry_data.items():
                    for price, qoh_data in price_data.items():
                        for qoh, rows in qoh_data.items():
                            for row in rows:
                                self.tree.insert("", "end", values=(
                                    item,
                                    price,
                                    qoh,
                                ))
            except Exception as e:
                self.tree.insert("", "end", values=(
                    f"Error loading data: {str(e)}", "", ""
                ))
        else:
            self.tree.insert("", "end", values=(
                "Model not initialized", "", ""
            ))
class RequestScrollsPage(tk.Frame): #ORDERS
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")

        #initializes the NAVIGATION BAR in the request scrolls page
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill = "x", pady = 5)

        label3 = ttk.Label(self, text = "RequestScrollsPage test").pack() #TESTING

        """
        FEATURES NEEDED:
        -status legend frame (consists of labels representing the status of orders: ongoing, requested, completed and cannot be completed;
       on the left)
        -orders table (consists of column headers: order#, client name, order request, status and action;
        users cannot modify any of the table values, except action which will be display/update based on inventory quantites;

        action cell states:
            if the state of the order is ongoing, users can press the cell to complete the order (the cell will say "COMPLETE ORDER"); 
            if the state of the order is completed, users cannot interact with the cell (the cell will say "NO ACTION REQUIRED");
            if the state of the order is requested, it is a new order and the user can press the cell to complete the order (the cell will say "ACCEPT ORDER AND COMPLETE")
            if the state of the order is cannot be completed, the user cannot interact with the cell (the cell will say "ORDER MORE [item that doesn't meet quantity] TO COMPLETE ORDER")

        a pop up will prompt the user to save after they interact with a cell in the action column)
        -update button (saves changes (if any) based on orders that the user chose to complete; will save )
        """

if __name__ == '__main__':
    root = tk.Tk()
    configure_style(root)
    app = CalcifersLedgerApp(root)
    root.mainloop()





