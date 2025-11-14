#CCT211 Assignment 2--Persistent Form
#Comments:

from cProfile import label
import tkinter as tk
from tkinter import messagebox


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
            navBtn = tk.Button(
                self,
                text = text,
                font = ("Verdana", 10),
                bg = "white",
                bd = 0,
                padx = 10,
                pady = 5,
                activebackground = "#e5e5e5",
                command = lambda p = page_class: controller.show_frame(p)
            )
            navBtn.pack(side = "left", padx = 18)
            self.nav_buttons[page_class] = navBtn
        
        #
        username = controller.username

        #WELCOME MENU item (displayed on the right side of the menu; welcomes whichever user who signed in)
        self.welcome_label = tk.Label(
            self,
            text = "Welcome!",
            font = ("Verdana", 10, "italic"),
            bg = "white"
        )
        self.welcome_label.pack(side = "right", padx = 18)

    #UPDATES ACTIVE FRAME (based on user interactions)
    def update_active(self, active_page):
        for page_class, button in self.nav_buttons.items():
            if page_class == active_page:
                button.config(font=("Verdana", 10, "bold"), fg = "#000")
            else:
                button.config(font = ("Verdana", 10), fg = "#666")

    def update_username(self, username):
        self.welcome_label.config(text = f"Welcome {username.capitalize()}!")
    
    def refresh_username(self):
        username = self.controller.username
        if username:
            self.welcome_label.config(text=f"Welcome {username.capitalize()}!")
        else:
            self.welcome_label.config(text="Welcome!")

#
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
   
        container = tk.Frame(self.root, bg = "white")
        container.pack(fill = "both", expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        #INITIALIZES all of our pages
        for Page in (LoginPage, OverviewPage, PotionPantryPage, RequestScrollsPage):
            frame = Page(parent = container, controller = self)
            self.frames[Page] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(LoginPage) #SHOWS THE LOGIN PAGE FRAME

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

        #ONLY Updates active nav items when relevant (when the user interacts with them)
        if hasattr(frame, "nav_frame"):
            frame.nav_frame.refresh_username()
            frame.nav_frame.update_active(page_class) #updates active section of the navigation (BOLDS IT)

class LoginPage(tk.Frame):
     def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")
        self.controller = controller

        #Creates a 3x3 grid to display the login widgets in the center of the frame
        for r in range(3):
            self.grid_rowconfigure(r, weight=1)
        for c in range(3):
            self.grid_columnconfigure(c, weight=1)

        center_frame = tk.Frame(self, bg = "white") #placed in the middle row (row = 1, col = 1)
        center_frame.grid(row = 1, column = 1) #places the frame directly into the grid      

        #LOGIN TITLE
        title_frame = tk.Frame(center_frame, bg = "white", bd = 2, relief = "solid")
        title_frame.pack(pady = (0, 16), anchor = "center")

        tk.Label( #HEADER TITLE
            title_frame,
            text = "Calcifer’s Ledger",
            font = ("Palatino", 50, "bold"),
            bg = "white"
        ).pack()

        tk.Label( #SUBHEADER TITLE
            title_frame,
            text = "Magic Record Keeping System",
            font = ("Verdana", 13),
            bg = "white"
        ).pack(pady=(0, 8))

        #FORM area (centered within center_frame)
        form_frame = tk.Frame(center_frame, bg = "white")
        form_frame.pack()

        #LOGIN
        login_row = tk.Frame(form_frame, bg = "white") #the login form row
        login_row.pack(anchor = "center", pady = 6)
        tk.Label(login_row, text = "Login:", font = ("Verdana", 12), bg = "white").pack(side = "left", padx = (0, 8))
        self.login_entry = tk.Entry(login_row, width = 25, font = ("Verdana", 12), bd = 2, relief = "groove")
        self.login_entry.pack(side = "left")

        #PASSWORD
        pass_row = tk.Frame(form_frame, bg = "white") #the password form row
        pass_row.pack(anchor = "center", pady = 6)
        tk.Label(pass_row, text = "Password:", font = ("Verdana", 12), bg = "white").pack(side = "left", padx = (0, 8))
        self.password_entry = tk.Entry(pass_row, width = 25, font = ("Verdana", 12), bd=2, relief = "groove", show = "*")
        self.password_entry.pack(side = "left")

        #BUTTON
        btn_row = tk.Frame(center_frame, bg = "white")
        btn_row.pack(pady = 14)
        login_btn = tk.Button(
            btn_row,
            text = "Login",
            font = ("Verdana", 12, "bold"),
            bg = "#f4a261",
            command = self.check_login
        )
        login_btn.pack()

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
        self.nav_frame.pack(fill = "x", pady=5)

        label1 = tk.Label(self, text="OverviewPage test").pack() #TESTING

class PotionPantryPage(tk.Frame): #INVENTORY 
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")

        #initializes the NAVIGATION BAR in the potion pantry page
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill="x", pady = 5)

        label2 = tk.Label(self, text="PotionPantryPage test").pack() #TESTING

class RequestScrollsPage(tk.Frame): #ORDERS
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")

        #initializes the NAVIGATION BAR in the request scrolls page
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill = "x", pady = 5)

        label3 = tk.Label(self, text="RequestScrollsPage test").pack() #TESTING

if __name__ == '__main__':
    root = tk.Tk()
    app = CalcifersLedgerApp(root)
    root.mainloop()


