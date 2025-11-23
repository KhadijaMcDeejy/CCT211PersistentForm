#CCT211 Assignment 2--Persistent Form
#Comments:

from cProfile import label
import tkinter as tk
from tkinter import ttk, messagebox
import models
from models import SQLStorage
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

import init_db
init_db.initialize_database()

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
            ("Apothecary", PotionPantryPage), #Inventory / Potion Pantry
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
        self.root.geometry("1350x600")

        self.valid_logins = {
            "howl": "fire123",
            "sophie": "howlcastle",
            "calcifer": "flame!"
        }

        self.username = None #intializes the username of whom has logged into the application
        self.model = models.SQLStorage()

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
        self.show_frame(RequestScrollsPage) #SHOWS THE LOGIN PAGE FRAME

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

        #Overview: TITLE Frame
        title_frame = tk.Frame(self, bg = "white")
        title_frame.pack(fill = "x", pady = (10, 20))
        ttk.Label(
            title_frame,
            text = "Overview",
            font = ("Palatino", 42, "bold"),
            background = "white",
        ).pack(anchor="w", padx = 30)

        #Overview: Content Area
        content_frame = tk.Frame(self, bg = "white")
        content_frame.pack(fill = "both", expand = True, padx = 30, pady = 10)
        content_frame.grid_columnconfigure(0, weight = 1)  #chart column: for the chart of past popular orders!
        content_frame.grid_columnconfigure(1, weight = 1)  #text column: giving context of the chart!
        content_frame.grid_rowconfigure(0, weight = 1)

        #Overview: Content Area- Left Side (CHART of past popular orders)
        chart_container = tk.Frame(content_frame, bg = "white", bd = 2, relief = "solid")
        chart_container.grid(row = 0, column = 0, sticky = "nsew", padx = (0, 20))
        self.create_popular_orders_chart(chart_container) #generates the Matplotlib chart
        ttk.Label( #chart title for user context
            chart_container,
            text = "Past Popular Orders",
            font = ("Verdana", 11, "italic"),
            background = "white"
        ).pack(side = "bottom", pady = 8)

        #fetching popular orders for the right side content area (specifically for the body_text section):
        storage = SQLStorage()
        order_data = storage.fetch_total_orders_by_item_type()
        if order_data:
            order_list = [(row["item_name"], int(row["total_ordered"])) for row in order_data] #converts the sqlite3 row into dict for access

            order_list.sort(key=lambda x: x[1], reverse=True) #Sorts the highest to the lowest most popular past orders

            #Extracts the top 3 most popular orders and bottom least popular order
            top_3 = order_list[:3] #top 3 popular order stored in top_3
            least = order_list[-1] if len(order_list) > 0 else ("None", 0) #least popular order stored in least
        else:
            top_3 = [("No data", 0), ("No data", 0), ("No data", 0)]
            least = ("No data", 0)

        storage.close()

        #Overview: Content Area- Right Side (Text regarding past popular orders)
        text_container = tk.Frame(content_frame, bg = "white", bd = 2, relief = "solid")
        text_container.grid(row = 0, column = 1, sticky="nsew")
        ttk.Label( #Subheader
            text_container,
            text = "Apothecary Insights",
            font = ("Verdana", 18, "bold"),
            background = "white",
        ).pack(anchor = "nw", padx = 20, pady = (20, 10))
        body_text = ( #Variable for body text (body_text)
            "Welcome to Calcifer's Ledger, your enchanted inventory and order management system. "
            "This magical ledger organizes the apothecary’s stock and tracks incoming orders, "
            "ensuring the castle’s operations run smoothly and efficiently.\n\n"
            "The chart on the left displays trends in past orders, highlighting the most requested items. "
            "By visualizing these patterns, castle staff can anticipate demand, optimize inventory, "
            "and maintain appropriate stock levels for upcoming requests.\n\n"
            "Current most popular orders:\n"
            f"1. {top_3[0][0]}\n"
            f"2. {top_3[1][0]}\n"
            f"3. {top_3[2][0]}\n\n"
            "Least popular order:\n"
            f"- {least[0]}"
        )
        ttk.Label( #body text area
            text_container,
            text=body_text,
            font=("Verdana", 11),
            wraplength = 400,
            background = "white",
            justify = "left"
        ).pack(anchor = "nw", padx = 20, pady = (0, 20))

    #Overview: chart functions
    def create_popular_orders_chart(self, container):
            matplotlib.use("Agg")
            storage = SQLStorage() #calls the SQLStorage class in the init_db.py file

            try:
                order_data = storage.fetch_total_orders_by_item_type() #calls fetch_total_orders_by_item_type and retrieves the values of item_name and total_ordered from the database
                #print([dict(row) for row in order_data]) #test print statement to show values of previous orders

                if order_data:
                    items = [row['item_name'] for row in order_data]
                    counts = [int(row['total_ordered'] or 0) for row in order_data]
                else:
                    items = ["No data"]
                    counts = [0]
            except Exception as e: #Error exception statement
                print("Chart DB Error:", e)
                items = ["No data"]
                counts = [0]

            #plots the bar chart!
            fig = Figure(figsize=(8, 4), dpi = 100) #size of chart
            ax = fig.add_subplot(111)
            #draws each bar
            bars = ax.bar(items, counts, color = 'skyblue') #initializes each bar values and colour

            #Chart titles
            ax.set_title("Popular Past Orders")
            ax.set_xlabel("Item Name")
            ax.set_ylabel("Total Orders")
            #Chart subtitles: Item Names
            ax.set_xticks(range(len(items)))  #sets the tick positions
            ax.set_xticklabels(items, rotation = 45, ha="right", fontsize = 6)

            fig.subplots_adjust(bottom=0.3) #gives space for the tick labels on the x axis

            #Quantity labels for each bar (displays an exact value for the user)
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,  #centers the text horizontally ontop of the bar
                    height / 2, #places the text (quantity) in the middle of the bar for visual clarity
                    str(count), #count is the value of quantity
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color="white"
                )

            #embeds the chart in Tkinter window
            canvas = FigureCanvasTkAgg(fig, master = container)
            canvas.draw() #draws the canvas
            canvas.get_tk_widget().pack(fill = "both", expand = True, padx = 10, pady = 10) #packs the canvas widget onto the window

            storage.close()

        #label1 = ttk.Label(self, text = "OverviewPage test").pack() #TESTING

class PotionPantryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.configure(bg = "black")
        self.nav_frame.pack(fill="x", pady=5)

        # Create a storage instance using the models SQLStorage
        self.storage = models.SQLStorage()
        self.current_ingredient = None
        self.current_potion = None
        self.order_mode = False
        self.selected_ingredients = []
        self.selected_potions = []

        # Main container with three frames
        main_container = tk.Frame(self, bg="black")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure grid weights for distribution
        main_container.columnconfigure(0, weight=1)  # Frame 1
        main_container.columnconfigure(1, weight=500)  # Frame 2
        main_container.columnconfigure(2, weight=1)  # Frame 3
        main_container.rowconfigure(0, weight=1)

        # Frame 1 (LHS) - Ingredients
        self.frame1 = tk.Frame(main_container, bg="lemon chiffon", relief="sunken", bd=2)
        self.frame1.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.create_ingredients_frame()

        # Frame 2 (Middle) - Display area
        self.frame2 = tk.Frame(main_container, bg="black", relief="sunken", bd=2)  
        self.frame2.grid(row=0, column=1, sticky="nsew", padx=5)
        self.create_display_frame()

        # Frame 3 (RHS) - Potions and Info
        self.frame3 = tk.Frame(main_container, bg="light blue", relief="sunken", bd=2)
        self.frame3.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        self.create_potions_frame()

        # Load initial data
        self.load_ingredients_menu()
        self.load_potions_menu()

    def create_ingredients_frame(self):
        """Create Frame 1 - Ingredients scrollable menu"""
        # Title
        title_label = tk.Label(self.frame1, text="Ingredients", font=("Verdana", 14, "bold"),bg="lemon chiffon", fg="medium orchid")
        title_label.pack(pady=10)
        # Scrollable frame for ingredient buttons
        button_container = tk.Frame(self.frame1, bg="lemon chiffon")
        button_container.pack(fill="both", expand=True, padx=0, pady=0)
        # Canvas and scrollbar
        self.ingredient_canvas = tk.Canvas(button_container, bg="lemon chiffon", highlightthickness=0)
        scrollbar = ttk.Scrollbar(button_container, orient="vertical", command=self.ingredient_canvas.yview)
        self.ingredient_button_frame = tk.Frame(self.ingredient_canvas, bg="lemon chiffon")
        self.ingredient_button_frame.bind(
            "<Configure>",
            lambda e: self.ingredient_canvas.configure(scrollregion=self.ingredient_canvas.bbox("all"))
        )
        self.ingredient_canvas.create_window((0, 0), window=self.ingredient_button_frame, anchor="nw")
        self.ingredient_canvas.configure(yscrollcommand=scrollbar.set)

        self.ingredient_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_display_frame(self):
        """Create Frame 2 - Display area for images and order creation"""
        self.display_container = tk.Frame(self.frame2, bg="black")
        self.display_container.pack(fill="both", expand=True)

        # Default display
        self.default_label = tk.Label(self.display_container,
                                      text="Select an ingredient or potion to view details\n\n"
                                           "Select an ingredients' QoH to edit it\n\n"
                                           "Select 'Create Order' button to create an order",
                                      font=("Verdana", 12), bg="black", fg="white")
        self.default_label.pack(expand=True)

        # Image display area ===========================================================================================
        # (initially hidden)
        self.image_display_frame = tk.Frame(self.display_container, bg="black")

        # Image label
        self.ingredient_image_label = tk.Label(self.image_display_frame, bg="black")
        self.ingredient_image_label.pack(expand=True, pady=20)

        # Buttons frame (for ingredient details)
        self.buttons_frame = tk.Frame(self.image_display_frame, bg="black")
        self.buttons_frame.pack(pady=20)

        self.price_button = ttk.Button(self.buttons_frame, text="Price: $0.00", width=15)
        self.price_button.pack(side="left", padx=10, pady=10)

        self.qoh_button = ttk.Button(self.buttons_frame, text="QoH: 0", width=15,
                                     command=self.show_qoh_editor)
        self.qoh_button.pack(side="left", padx=10)

        # Potion display area ==========================================================================================
        self.potion_display_frame = tk.Frame(self.display_container, bg="black")
        # Potion image label
        self.potion_image_label = tk.Label(self.potion_display_frame, bg="black")
        self.potion_image_label.pack(pady=0)
        # Potion effect text
        self.potion_effect_text = tk.Text(self.potion_display_frame, wrap="word", width=40, height=5,
                                          font=("Verdana", 10), bg="black", fg="white",
                                          relief="flat", bd=0,
                                          highlightthickness=0)
        self.potion_effect_text.pack(fill="none", expand=0, pady=(0,0), padx=(50,0), side="left")
        self.potion_effect_text.config(state="disabled")

        # Potion Ingredients text area
        self.potion_ingredients_text = tk.Text(self.potion_display_frame, wrap="word", width=40, height=6,
                                          font=("Verdana", 10), bg="black", fg="white",
                                          relief="flat", bd=0,
                                          highlightthickness=0)
        self.potion_ingredients_text.pack(fill="none", expand=0, pady=(0,0), padx=(0,0), side="right")
        self.potion_ingredients_text.config(state="disabled")

        # Order creation area
        self.order_creation_frame = tk.Frame(self.display_container, bg="black")

        order_title = tk.Label(self.order_creation_frame, text="Create New Order",
                               font=("Verdana", 16, "bold"), bg="black", fg="white")
        order_title.pack(pady=10)

        # Customer name input
        customer_frame = tk.Frame(self.order_creation_frame, bg="black")
        customer_frame.pack(fill="x", pady=10)
        tk.Label(customer_frame, text="Customer Name:", font=("Verdana", 11), bg="black", fg="white").pack(side="left")
        self.customer_entry = ttk.Entry(customer_frame, width=25)
        self.customer_entry.pack(side="left", padx=10)

        # Selected ingredients display
        ing_frame = tk.Frame(self.order_creation_frame, bg="black")
        ing_frame.pack(fill="both", expand=True, pady=10)
        tk.Label(ing_frame, text="Selected Ingredients:", font=("Verdana", 11, "bold"), bg="black", fg="white").pack(
            anchor="w")
        self.ingredients_text = tk.Text(ing_frame, wrap="word", width=40, height=6,
                                        font=("Verdana", 9), bg="black", fg="white", relief="sunken", bd=1)
        self.ingredients_text.pack(fill="both", expand=True, pady=5)
        self.ingredients_text.config(state="disabled")

        # Selected potions display
        pot_frame = tk.Frame(self.order_creation_frame, bg="black")
        pot_frame.pack(fill="both", expand=True, pady=10)
        tk.Label(pot_frame, text="Selected Potions:", font=("Verdana", 11, "bold"), bg="black", fg="white").pack(
            anchor="w")
        self.potions_text = tk.Text(pot_frame, wrap="word", width=40, height=6,
                                    font=("Verdana", 9), bg="black", fg="white", relief="sunken", bd=1)
        self.potions_text.pack(fill="both", expand=True, pady=5)
        self.potions_text.config(state="disabled")

        # Order buttons
        order_buttons = tk.Frame(self.order_creation_frame, bg="black")
        order_buttons.pack(pady=20)
        self.create_order_btn = ttk.Button(order_buttons, text="Create Order",
                                           command=self.create_order)
        self.create_order_btn.pack(side="left", padx=10)
        self.cancel_order_btn = ttk.Button(order_buttons, text="Cancel",
                                           command=self.cancel_order_creation)
        self.cancel_order_btn.pack(side="left", padx=10)

    def create_potions_frame(self):
        """Create Frame 3 - Potions scrollable menu and info"""
        # Title
        title_label = tk.Label(self.frame3, text="Potions", font=("Verdana", 14, "bold"),
                               bg="light blue",fg="navy")
        title_label.pack(pady=10)

        # Scrollable frame for potion buttons
        button_container = tk.Frame(self.frame3, bg="light blue")
        button_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Canvas and scrollbar
        self.potion_canvas = tk.Canvas(button_container, bg="light blue", highlightthickness=0)
        scrollbar = ttk.Scrollbar(button_container, orient="vertical", command=self.potion_canvas.yview)
        self.potion_button_frame = tk.Frame(self.potion_canvas, bg="light blue")

        self.potion_button_frame.bind(
            "<Configure>",
            lambda e: self.potion_canvas.configure(scrollregion=self.potion_canvas.bbox("all"))
        )

        self.potion_canvas.create_window((0, 0), window=self.potion_button_frame, anchor="nw")
        self.potion_canvas.configure(yscrollcommand=scrollbar.set)

        self.potion_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create Order button
        create_order_btn = ttk.Button(self.frame3, text="Create Order",
                                      command=self.start_order_creation)
        create_order_btn.pack(side="bottom", anchor="sw", padx=100, pady=10)

    def load_ingredients_menu(self):
        """Load ingredients into Frame 1"""
        for widget in self.ingredient_button_frame.winfo_children():
            widget.destroy()

        try:
            ingredients = self.storage.get_all_ingredients()
            if not ingredients:
                tk.Label(self.ingredient_button_frame, text="No ingredients", bg="light gray").pack(pady=10)
                return

            for ingredient in ingredients:
                btn = ttk.Button(
                    self.ingredient_button_frame,
                    text=ingredient.name,
                    command=lambda ing=ingredient: self.show_ingredient_details(ing)
                )
                btn.pack(fill="x", pady=5, padx=(20,0))

        except Exception as e:
            print(f"Error loading ingredients: {e}")
            tk.Label(self.ingredient_button_frame, text=f"Error: {str(e)}", bg="light gray").pack(pady=10)

    def load_potions_menu(self):
        """Load potions into Frame 3"""
        for widget in self.potion_button_frame.winfo_children():
            widget.destroy()

        try:
            potions = self.storage.get_all_potions()
            if not potions:
                tk.Label(self.potion_button_frame, text="No potions", bg="light blue").pack(pady=10)
                return

            for potion in potions:
                btn = ttk.Button(
                    self.potion_button_frame,
                    text=potion.name,
                    command=lambda pot=potion: self.show_potion_details(pot)
                )
                btn.pack(fill="x", pady=5, padx=(30,0))

        except Exception as e:
            print(f"Error loading potions: {e}")
            tk.Label(self.potion_button_frame, text=f"Error: {str(e)}", bg="light blue").pack(pady=10)

    def show_ingredient_details(self, ingredient):
        """Show ingredient details in Frame 2"""
        if self.order_mode:
            self.toggle_ingredient_selection(ingredient)
            return

        self.current_ingredient = ingredient
        self.hide_all_displays()
        self.image_display_frame.pack(fill="both", expand=True)

        # Load and display image
        image = self.load_ingredient_image(ingredient.ingredient_id)
        if image:
            self.ingredient_image_label.config(image=image)
            self.ingredient_image_label.image = image  # Keep reference
        else:
            self.ingredient_image_label.config(text=f"Ingredient: {ingredient.name}")

        # Update buttons
        self.price_button.config(text=f"Price: ${ingredient.price:.2f}")
        self.qoh_button.config(text=f"QoH: {ingredient.quantity}")
        self.buttons_frame.pack()

    def show_potion_details(self, potion):
        """Show potion details in Frame 2"""
        if self.order_mode:
            self.toggle_potion_selection(potion)
            return

        self.current_potion = potion
        self.hide_all_displays()
        self.potion_display_frame.pack(fill="both", expand=True)

        # Load and display image
        image = self.load_potion_image(potion.potion_id)
        if image:
            self.potion_image_label.config(image=image)
            self.potion_image_label.image = image  # Keep reference
        else:
            self.potion_image_label.config(text=f"Potion: {potion.name}")

        # Update effect text
        self.potion_effect_text.config(state="normal")
        self.potion_effect_text.delete(1.0, tk.END)
        self.potion_effect_text.insert(1.0, potion.effect)
        self.potion_effect_text.config(state="disabled")

        # Update ingredients text - FIXED THIS PART
        self.potion_ingredients_text.config(state="normal")
        self.potion_ingredients_text.delete(1.0, tk.END)

        # Get the ingredients for this potion
        ingredients_list = self.storage.get_potion_ingredients(potion.potion_id)

        if ingredients_list:
            ingredients_text = "Ingredients:\n"
            for ingredient in ingredients_list:
                ingredients_text += f"• {ingredient.name}: {getattr(ingredient, 'quantity_in_recipe', 1)} units\n"
        else:
            ingredients_text = "No ingredients listed for this potion."

        self.potion_ingredients_text.insert(1.0, ingredients_text)
        self.potion_ingredients_text.config(state="disabled")

    def hide_all_displays(self):
        """Hide all display frames"""
        self.default_label.pack_forget()
        self.image_display_frame.pack_forget()
        self.potion_display_frame.pack_forget()
        self.order_creation_frame.pack_forget()
        self.buttons_frame.pack_forget()

    def start_order_creation(self):
        """Start order creation mode"""
        self.order_mode = True
        self.selected_ingredients = []
        self.selected_potions = []
        self.hide_all_displays()
        self.order_creation_frame.pack(fill="both", expand=True)
        self.customer_entry.delete(0, tk.END)
        self.update_selection_displays()

    def cancel_order_creation(self):
        """Cancel order creation and return to normal mode"""
        self.order_mode = False
        self.selected_ingredients = []
        self.selected_potions = []
        self.hide_all_displays()
        self.default_label.pack(expand=True)

    def toggle_ingredient_selection(self, ingredient):
        """Toggle ingredient selection in order mode"""
        if ingredient in self.selected_ingredients:
            self.selected_ingredients.remove(ingredient)
        else:
            self.selected_ingredients.append(ingredient)
        self.update_selection_displays()

    def toggle_potion_selection(self, potion):
        """Toggle potion selection in order mode"""
        if potion in self.selected_potions:
            self.selected_potions.remove(potion)
        else:
            self.selected_potions.append(potion)
        self.update_selection_displays()

    def update_selection_displays(self):
        """Update the selection display text boxes"""
        # Update ingredients text
        self.ingredients_text.config(state="normal")
        self.ingredients_text.delete(1.0, tk.END)
        for ing in self.selected_ingredients:
            self.ingredients_text.insert(tk.END, f"• {ing.name}\n")
        self.ingredients_text.config(state="disabled")

        # Update potions text
        self.potions_text.config(state="normal")
        self.potions_text.delete(1.0, tk.END)
        for pot in self.selected_potions:
            self.potions_text.insert(tk.END, f"• {pot.name}\n")
        self.potions_text.config(state="disabled")

    def create_order(self):
        """Create the order from selections"""
        customer_name = self.customer_entry.get().strip()
        if not customer_name:
            messagebox.showerror("Error", "Please enter a customer name.")
            return

        if not self.selected_ingredients and not self.selected_potions:
            messagebox.showerror("Error", "Please select at least one ingredient or potion.")
            return

        # Here you would save the order to your database
        # For now, just show a success message
        messagebox.showinfo("Success", f"Order created for {customer_name}!")
        self.cancel_order_creation()

    def show_qoh_editor(self):
        """Show QoH editor"""
        if not self.current_ingredient:
            messagebox.showinfo("Info", "Please select an ingredient first.")
            return

        editor = tk.Toplevel(self)
        editor.title(f"Edit Quantity - {self.current_ingredient.name}")
        editor.geometry("300x200")
        editor.transient(self)
        editor.grab_set()

        main_frame = tk.Frame(editor, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text=f"Update quantity for {self.current_ingredient.name}:",
                 font=("Verdana", 10)).pack(pady=(0, 10))

        entry_frame = tk.Frame(main_frame)
        entry_frame.pack(pady=10)

        qoh_var = tk.StringVar(value=str(self.current_ingredient.quantity))
        qoh_entry = ttk.Entry(entry_frame, textvariable=qoh_var, width=10, font=("Verdana", 10))
        qoh_entry.pack(side="left", padx=(0, 10))
        qoh_entry.select_range(0, tk.END)
        qoh_entry.focus()

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        def save_qoh():
            try:
                new_qoh = int(qoh_var.get().strip())
                if new_qoh < 0:
                    messagebox.showerror("Error", "Quantity cannot be negative.", parent=editor)
                    return

                # Update the ingredient
                self.current_ingredient.quantity = new_qoh
                self.storage.save_ingredient(self.current_ingredient)
                self.show_ingredient_details(self.current_ingredient)
                messagebox.showinfo("Success", f"Updated {self.current_ingredient.name} quantity to {new_qoh}",
                                    parent=editor)
                editor.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for quantity.", parent=editor)

        ttk.Button(button_frame, text="Save", command=save_qoh).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=editor.destroy).pack(side="left", padx=5)

    def load_ingredient_image(self, ingredient_id):
        """Load ingredient image using PIL with black background"""
        try:
            image_path = f"Ingredients/I{ingredient_id}.png"
            image = Image.open(image_path)

            # Convert to RGBA if not already to handle transparency
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Create a black background image
            background = Image.new('RGBA', image.size, (0, 0, 0, 255))

            # Composite the image over the black background
            image_with_bg = Image.alpha_composite(background, image)

            # Convert back to RGB for Tkinter compatibility
            image_with_bg = image_with_bg.convert('RGB')

            image_with_bg = image_with_bg.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_with_bg)
            return photo
        except Exception as e:
            print(f"Error loading image for ingredient {ingredient_id}: {e}")
            # Return a black placeholder
            placeholder = Image.new('RGB', (400, 400), (0, 0, 0))
            photo = ImageTk.PhotoImage(placeholder)
            return photo

    def load_potion_image(self, potion_id):
        """Load potion image using PIL with black background"""
        try:
            image_path = f"potions/P{potion_id}.png"
            image = Image.open(image_path)

            # Convert to RGBA if not already to handle transparency
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Create a black background image
            background = Image.new('RGBA', image.size, (0, 0, 0, 255))

            # Composite the image over the black background
            image_with_bg = Image.alpha_composite(background, image)

            # Convert back to RGB for Tkinter compatibility
            image_with_bg = image_with_bg.convert('RGB')

            image_with_bg = image_with_bg.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_with_bg)
            return photo
        except Exception as e:
            print(f"Error loading image for potion {potion_id}: {e}")
            # Return a black placeholder
            placeholder = Image.new('RGB', (400, 400), (0, 0, 0))
            photo = ImageTk.PhotoImage(placeholder)
            return photo

class RequestScrollsPage(tk.Frame):  # ORDERS
    """
    FEATURES NEEDED:
        -status legend frame (consists of labels representing the status of orders:requested, ongoing, completed and cannot be completed;
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
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Initialize the NAVIGATION BAR
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill="x", pady=5)
        self.nav_frame.config(bg="black")

        # Create a storage instance
        self.storage = models.SQLStorage()

        # Main container
        main_container = tk.Frame(self, bg="black")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== LEFT COLUMN - Status Legend =====
        left_container = tk.Frame(main_container, bg="black")
        left_container.pack(side="left", fill="y", padx=(0, 20))

        # Status Legend Frame
        legend_frame = tk.Frame(left_container, bg="white", relief="raised", bd=2)
        legend_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            legend_frame,
            text="Order Status Legend",
            font=("Verdana", 14, "bold"),
            background="white"
        ).pack(pady=10)

        # Status items
        status_items = [
            ("Requested", "New orders waiting to be processed", "light yellow"),
            ("Ongoing", "Orders being prepared", "light coral"),
            ("Completed", "Successfully fulfilled orders", "light green"),
            ("Cannot Complete", "Insufficient ingredients", "light coral")
        ]

        for status, description, color in status_items:
            status_frame = tk.Frame(legend_frame, bg="white")
            status_frame.pack(fill="x", padx=10, pady=5)

            # Color indicator
            color_label = tk.Label(status_frame, bg=color, width=3, height=1)
            color_label.pack(side="left", padx=(0, 10))

            # Status text
            text_frame = tk.Frame(status_frame, bg="white")
            text_frame.pack(side="left", fill="x", expand=True)

            ttk.Label(
                text_frame,
                text=status,
                font=("Verdana", 10, "bold"),
                background="white"
            ).pack(anchor="w")

            ttk.Label(
                text_frame,
                text=description,
                font=("Verdana", 8),
                background="white"
            ).pack(anchor="w")

        # Update Button
        update_btn = ttk.Button(
            left_container,
            text="Refresh Orders",
            command=self.refresh_orders
        )
        update_btn.pack(side="bottom", fill="x", pady=(10, 0))

        # ===== RIGHT COLUMN - Orders Table =====
        right_container = tk.Frame(main_container, bg="black")
        right_container.pack(side="right", fill="both", expand=True)

        # Table Header
        header_frame = tk.Frame(right_container, bg="black")
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header_frame,
            text="Order Management",
            font=("Verdana", 18, "bold"),
            background="black",
            foreground="white"
        ).pack(side="left")

        # Orders Table Frame
        table_frame = tk.Frame(right_container, bg="white", relief="sunken", bd=2)
        table_frame.pack(fill="both", expand=True)

        # Create Treeview (table)
        columns = ("order_id", "customer", "items", "status", "action")
        self.orders_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        # Define headings
        self.orders_tree.heading("order_id", text="Order #")
        self.orders_tree.heading("customer", text="Client Name")
        self.orders_tree.heading("items", text="Order Request")
        self.orders_tree.heading("status", text="Status")
        self.orders_tree.heading("action", text="Action")

        # Define column widths
        self.orders_tree.column("order_id", width=80, anchor="center")
        self.orders_tree.column("customer", width=120, anchor="center")
        self.orders_tree.column("items", width=200, anchor="w")
        self.orders_tree.column("status", width=120, anchor="center")
        self.orders_tree.column("action", width=200, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind click event for action column
        self.orders_tree.bind("<ButtonRelease-1>", self.on_table_click)

        # Load initial data
        self.load_orders_table()

    def load_orders_table(self):
        """Load all orders into the table"""
        try:
            # Clear existing items
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)

            # Get all orders with order_status
            self.storage.data_access.execute("SELECT * FROM Orders ORDER BY order_id;")
            orders = []
            for row in self.storage.data_access:
                orders.append({
                    'order_id': row[0],
                    'customer_name': row[1],
                    'order_status': row[2]
                })

            if not orders:
                # Display no orders message
                self.orders_tree.insert("", "end", values=("No orders", "", "", "", ""))
                return

            for order in orders:
                order_id = order['order_id']
                customer_name = order['customer_name']
                order_status = order.get('order_status', 0)

                # Get order items
                order_items = self.get_order_items(order_id)
                items_text = self.format_items_text(order_items)

                # Get status text
                status_text = self.get_status_text(order_status)

                # Get action text based on status
                action_text, action_state = self.get_action_details(order_id, order_status, order_items)

                # Insert into table
                self.orders_tree.insert(
                    "",
                    "end",
                    values=(
                        order_id,
                        customer_name,
                        items_text,
                        status_text,
                        action_text
                    ),
                    tags=(f"status_{order_status}", action_state)
                )

            # Configure tag colors
            self.orders_tree.tag_configure("status_0", background="light yellow")
            self.orders_tree.tag_configure("status_1", background="light coral")
            self.orders_tree.tag_configure("status_2", background="light green")
            self.orders_tree.tag_configure("status_3", background="light coral")
            self.orders_tree.tag_configure("disabled", foreground="gray")

        except Exception as e:
            print(f"Error loading orders table: {e}")
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def get_order_items(self, order_id):
        """Get all items (ingredients and potions) for an order"""
        items = []

        # Get ingredients
        try:
            self.storage.data_access.execute("""
                                             SELECT a.ingredient_name, oi.quantity
                                             FROM Order_Ingredients oi
                                                      JOIN Apothecary a ON oi.ingredient_id = a.ingredient_id
                                             WHERE oi.order_id = ?
                                             """, (order_id,))
            ingredients = self.storage.data_access.fetchall()
            for ing in ingredients:
                items.append(f"{ing[1]}x {ing[0]}")
        except Exception as e:
            print(f"Error fetching ingredients for order {order_id}: {e}")

        # Get potions
        try:
            self.storage.data_access.execute("""
                                             SELECT p.potion_name, op.quantity
                                             FROM Order_Potions op
                                                      JOIN Potions p ON op.potion_id = p.potion_id
                                             WHERE op.order_id = ?
                                             """, (order_id,))
            potions = self.storage.data_access.fetchall()
            for pot in potions:
                items.append(f"{pot[1]}x {pot[0]}")
        except Exception as e:
            print(f"Error fetching potions for order {order_id}: {e}")

        return items

    def format_items_text(self, items):
        """Format items text for display in table"""
        if not items:
            return "No items"

        # Show first 2-3 items, then "and X more"
        if len(items) <= 3:
            return ", ".join(items)
        else:
            return ", ".join(items[:2]) + f" and {len(items) - 2} more"

    def get_status_text(self, order_status):
        """Get human-readable status text"""
        status_map = {
            0: "Requested",
            1: "Ongoing",
            2: "Completed",
            3: "Cannot Complete"
        }
        return status_map.get(order_status, "Unknown")

    def get_action_details(self, order_id, order_status, order_items):
        """Get action text and state based on order status"""
        if order_status == 0:  # Requested
            return "ACCEPT ORDER AND COMPLETE", "enabled"

        elif order_status == 1:  # Ongoing
            # Check if we can complete
            can_complete = self.check_order_feasibility(order_id)
            if can_complete:
                return "COMPLETE ORDER", "enabled"
            else:
                # Find which ingredients are insufficient
                missing_items = self.get_missing_ingredients(order_id)
                if missing_items:
                    return f"ORDER MORE {missing_items[0]} TO COMPLETE", "disabled"
                else:
                    return "INSUFFICIENT INGREDIENTS", "disabled"

        elif order_status == 2:  # Completed
            return "NO ACTION REQUIRED", "disabled"

        elif order_status == 3:  # Cannot Complete
            missing_items = self.get_missing_ingredients(order_id)
            if missing_items:
                return f"ORDER MORE {missing_items[0]} TO COMPLETE", "disabled"
            else:
                return "INSUFFICIENT INGREDIENTS", "disabled"

        return "UNKNOWN STATUS", "disabled"

    def get_missing_ingredients(self, order_id):
        """Get list of ingredients that are insufficient for this order"""
        missing = []
        try:
            # Get all potions in the order
            self.storage.data_access.execute("""
                                             SELECT p.potion_id, op.quantity
                                             FROM Order_Potions op
                                                      JOIN Potions p ON op.potion_id = p.potion_id
                                             WHERE op.order_id = ?
                                             """, (order_id,))
            potions = self.storage.data_access.fetchall()

            for potion_id, quantity in potions:
                # Get ingredients needed for this potion
                ingredients = self.storage.get_potion_ingredients(potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * quantity
                    if ingredient.quantity < required_qty:
                        missing.append(ingredient.name)

        except Exception as e:
            print(f"Error getting missing ingredients: {e}")

        return missing

    def on_table_click(self, event):
        """Handle clicks on the table, specifically action column"""
        item = self.orders_tree.identify_row(event.y)
        column = self.orders_tree.identify_column(event.x)

        if item and column == "#5":  # Action column
            values = self.orders_tree.item(item, "values")
            order_id = int(values[0])
            order_status = self.get_order_status_from_text(values[3])
            action_text = values[4]

            # Only process if action is enabled
            tags = self.orders_tree.item(item, "tags")
            if "disabled" not in tags:
                self.handle_order_action(order_id, order_status, action_text)

    def get_order_status_from_text(self, status_text):
        """Convert status text back to status code"""
        status_map = {
            "Requested": 0,
            "Ongoing": 1,
            "Completed": 2,
            "Cannot Complete": 3
        }
        return status_map.get(status_text, 0)

    def handle_order_action(self, order_id, order_status, action_text):
        """Handle order actions based on current status"""
        if order_status == 0:  # Requested -> Process to Ongoing
            self.process_order(order_id)

        elif order_status == 1:  # Ongoing -> Complete
            if "COMPLETE" in action_text:
                self.complete_order(order_id)

    def process_order(self, order_id):
        """Process a requested order (move from status 0 to 1 or 3)"""
        try:
            # Check if we have sufficient ingredients
            can_complete = self.check_order_feasibility(order_id)

            # Update order status
            new_status = 1 if can_complete else 3  # Ongoing or Cannot Complete
            self.storage.data_access.execute(
                "UPDATE Orders SET order_status = ? WHERE order_id = ?",
                (new_status, order_id)
            )
            self.storage.conn.commit()

            # If we can complete, update ingredient quantities
            if can_complete:
                self.update_ingredient_quantities(order_id)

            # Show confirmation
            status_msg = "Order processed successfully!" if can_complete else "Order processed but cannot be completed due to insufficient ingredients"
            messagebox.showinfo("Order Processed", status_msg)

            # Reload table
            self.load_orders_table()

        except Exception as e:
            print(f"Error processing order {order_id}: {e}")
            messagebox.showerror("Error", f"Failed to process order: {str(e)}")

    def complete_order(self, order_id):
        """Complete an ongoing order (move from status 1 to 2)"""
        try:
            # Update order status to completed
            self.storage.data_access.execute(
                "UPDATE Orders SET order_status = 2 WHERE order_id = ?",
                (order_id,)
            )
            self.storage.conn.commit()

            messagebox.showinfo("Order Completed", f"Order #{order_id} has been completed!")

            # Reload table
            self.load_orders_table()

        except Exception as e:
            print(f"Error completing order {order_id}: {e}")
            messagebox.showerror("Error", f"Failed to complete order: {str(e)}")

    def check_order_feasibility(self, order_id):
        """Check if an order can be completed based on available ingredients"""
        try:
            # Get all potions in the order
            self.storage.data_access.execute("""
                                             SELECT p.potion_id, op.quantity
                                             FROM Order_Potions op
                                                      JOIN Potions p ON op.potion_id = p.potion_id
                                             WHERE op.order_id = ?
                                             """, (order_id,))
            potions = self.storage.data_access.fetchall()

            for potion_id, quantity in potions:
                # Get ingredients needed for this potion
                ingredients = self.storage.get_potion_ingredients(potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * quantity
                    if ingredient.quantity < required_qty:
                        return False  # Insufficient ingredients

            return True  # All ingredients are sufficient

        except Exception as e:
            print(f"Error checking order feasibility: {e}")
            return False

    def update_ingredient_quantities(self, order_id):
        """Update ingredient quantities when an order is processed"""
        try:
            # Get all potions in the order
            self.storage.data_access.execute("""
                                             SELECT p.potion_id, op.quantity
                                             FROM Order_Potions op
                                                      JOIN Potions p ON op.potion_id = p.potion_id
                                             WHERE op.order_id = ?
                                             """, (order_id,))
            potions = self.storage.data_access.fetchall()

            for potion_id, quantity in potions:
                # Get ingredients needed for this potion
                ingredients = self.storage.get_potion_ingredients(potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * quantity
                    # Update the ingredient quantity
                    new_qty = ingredient.quantity - required_qty
                    if new_qty < 0:
                        new_qty = 0

                    self.storage.data_access.execute(
                        "UPDATE Apothecary SET ingredient_qoh = ? WHERE ingredient_id = ?",
                        (new_qty, ingredient.ingredient_id)
                    )

            self.storage.conn.commit()

        except Exception as e:
            print(f"Error updating ingredient quantities: {e}")
            self.storage.conn.rollback()

    def refresh_orders(self):
        """Refresh the orders display"""
        self.load_orders_table()
        messagebox.showinfo("Refreshed", "Orders have been refreshed!")

if __name__ == '__main__':
    root = tk.Tk()
    configure_style(root)
    app = CalcifersLedgerApp(root)
    root.mainloop()






