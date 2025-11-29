import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# -------------------- DATABASE CONFIG --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "jollidog_system"
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect: {e}")
        return None

def fetch_user_accounts():
    conn = get_db_connection()
    accounts = {}
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM user_accounts")
        for username, password in cursor.fetchall():
            accounts[username] = password
        cursor.close()
        conn.close()
    return accounts

def add_user_account(username, password, first_name, middle_name, last_name, age):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_accounts (username, password, first_name, middle_name, last_name, age) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, password, first_name, middle_name, last_name, age)
            )
            conn.commit()
        except mysql.connector.Error as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Could not add account: {e}")
        finally:
            cursor.close()
            conn.close()

def on_enter(e):
    e.widget["background"] = "#E5C168"
    e.widget["foreground"] = "white"

def on_leave(e):
    e.widget["background"] = "white"
    e.widget["foreground"] = "black"
    
def make_window_responsive(win, min_w=800, min_h=600):
    win.resizable(True, True)
    win.minsize(min_w, min_h)

def register_page():
    win = tk.Tk()
    win.title("Create Account")
    win.geometry("1920x1080")
    win.configure(bg="#FFF0B9")

    def validate_password(*args):
        password = password_var.get()
        if len(password) < 6:
            password_req_label.config(text="Password: 6-9 characters (Too short)", fg="red")
        elif len(password) > 9:
            password_req_label.config(text="Password: 6-9 characters (Too long)", fg="red")
        else:
            password_req_label.config(text="Password: 6-9 characters (Good)", fg="green")

    def register_now():
        first_name = first_name_entry.get().strip()
        middle_name = middle_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        u = username_entry.get().strip()
        p = password_var.get().strip()
        
        if not all([first_name, last_name, u, p]):
            messagebox.showwarning("Error", "Please fill all required fields.")
            return
        
        if len(p) < 6 or len(p) > 9:
            messagebox.showwarning("Error", "Password must be between 6 and 9 characters.")
            return
        
        accounts = fetch_user_accounts()
        if u in accounts:
            messagebox.showerror("Error", "Username already exists.")
            return
        
        add_user_account(u, p, first_name, middle_name, last_name, None)
        messagebox.showinfo("Success", "User registered successfully!")
        win.destroy()
        users_login_page()

    # MAIN GRID
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    main_frame = tk.Frame(win, bg="#FFF0B9")
    main_frame.grid(row=0, column=0, sticky="nsew")

    for i in range(12):
        main_frame.grid_rowconfigure(i, weight=1 if i in (0, 11) else 0)
    main_frame.grid_columnconfigure(0, weight=1)  # labels
    main_frame.grid_columnconfigure(1, weight=2)  # entries/buttons

    # TITLE
    tk.Label(main_frame, text="Create an Account", bg="#FFF0B9", font=("Arial", 40))\
        .grid(row=1, column=0, columnspan=2, pady=10)

    # FIRST NAME
    tk.Label(main_frame, text="First Name:", bg="#FFF0B9", font=("Arial", 20)).grid(row=2, column=0, pady=5, sticky="e")
    first_name_entry = tk.Entry(main_frame, width=30, font=("Arial", 20))
    first_name_entry.grid(row=2, column=1, pady=5, sticky="w")

    # MIDDLE NAME
    tk.Label(main_frame, text="Middle Name:", bg="#FFF0B9", font=("Arial", 20)).grid(row=3, column=0, pady=5, sticky="e")
    middle_name_entry = tk.Entry(main_frame, width=30, font=("Arial", 20))
    middle_name_entry.grid(row=3, column=1, pady=5, sticky="w")

    # LAST NAME
    tk.Label(main_frame, text="Last Name:", bg="#FFF0B9", font=("Arial", 20)).grid(row=4, column=0, pady=5, sticky="e")
    last_name_entry = tk.Entry(main_frame, width=30, font=("Arial", 20))
    last_name_entry.grid(row=4, column=1, pady=5, sticky="w")

    # USERNAME
    tk.Label(main_frame, text="Username:", bg="#FFF0B9", font=("Arial", 20)).grid(row=5, column=0, pady=5, sticky="e")
    username_entry = tk.Entry(main_frame, width=30, font=("Arial", 20))
    username_entry.grid(row=5, column=1, pady=5, sticky="w")

    # PASSWORD REQUIREMENT LABEL (aligned with entries)
    password_req_label = tk.Label(main_frame, text="Password: 6-9 characters", bg="#FFF0B9", font=("Arial", 16))
    password_req_label.grid(row=6, column=1, pady=(10, 0), sticky="w")

    # ENTER PASSWORD
    tk.Label(main_frame, text="Create Password:", bg="#FFF0B9", font=("Arial", 20)).grid(row=7, column=0, pady=5, sticky="e")
    password_frame = tk.Frame(main_frame, bg="#FFF0B9")
    password_frame.grid(row=7, column=1, pady=5, sticky="w")

    password_var = tk.StringVar()
    password_var.trace('w', validate_password)
    password_entry = tk.Entry(password_frame, width=25, font=("Arial", 20), show="*", textvariable=password_var)
    password_entry.pack(side="left")

    def toggle_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
            show_pass_btn.config(text="Hide")
        else:
            password_entry.config(show="*")
            show_pass_btn.config(text="Show")

    show_pass_btn = tk.Button(password_frame, text="Show", command=toggle_password, width=5, font=("Arial", 10))
    show_pass_btn.pack(side="left", padx=(5, 0))

    # REGISTER BUTTON (aligned with entry column)
    register_btn = tk.Button(main_frame, text="Register", width=15, command=register_now, font=("Arial", 15))
    register_btn.grid(row=8, column=1, pady=20, sticky="w")

    # BACK BUTTON (aligned with entry column)
    back_btn = tk.Button(main_frame, text="Back", width=15, command=lambda: (win.destroy(), users_login_page()), font=("Arial", 15))
    back_btn.grid(row=9, column=1, pady=5, sticky="w")

    register_btn.bind("<Enter>", on_enter)
    register_btn.bind("<Leave>", on_leave)
    back_btn.bind("<Enter>", on_enter)
    back_btn.bind("<Leave>", on_leave)

    win.mainloop()

#--------------user login-------------------
def users_login_page():
    win = tk.Tk()
    win.title("User Login")
    win.geometry("1920x1080")
    win.configure(bg="#FFF0B9")

    make_window_responsive(win, 800, 600)

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    main_frame = tk.Frame(win, bg="#FFF0B9")
    main_frame.grid(row=0, column=0, sticky="nsew")

    for i in range(11):
        main_frame.grid_rowconfigure(i, weight=1 if i in (0, 10) else 0)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=0)
    main_frame.grid_columnconfigure(2, weight=1)

    tk.Label(main_frame, text="User Login", font=("Arial", 40), bg="#FFF0B9").grid(row=1, column=1, pady=20)
    tk.Label(main_frame, text="Username:", font=("Arial", 20), bg="#FFF0B9").grid(row=2, column=1)
    username_entry = tk.Entry(main_frame, width=25, font=("Arial", 20))
    username_entry.grid(row=3, column=1, pady=10)

    tk.Label(main_frame, text="Password:", font=("Arial", 20), bg="#FFF0B9").grid(row=4, column=1)
    password_entry = tk.Entry(main_frame, width=25, font=("Arial", 20), show="*")
    password_entry.grid(row=5, column=1, pady=10, sticky="w")

    def toggle_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
            show_pass_btn.config(text="Hide")
        else:
            password_entry.config(show="*")
            show_pass_btn.config(text="Show")

    show_pass_btn = tk.Button(main_frame, text="Show", command=toggle_password, width=5)
    show_pass_btn.grid(row=5, column=2, padx=(5,0), sticky="w")

    def attempt_login():
        u = username_entry.get().strip()
        p = password_entry.get().strip()
        accounts = fetch_user_accounts()
        if u in accounts and accounts[u] == p:
            messagebox.showinfo("Success", "Login Successful!")
            win.destroy()
            import ordering
            ordering.ordering_system(u)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    login_btn = tk.Button(main_frame, text="Login", font=("Arial", 10), width=10, command=attempt_login)
    login_btn.grid(row=7, column=1, pady=5)

    back_btn = tk.Button(main_frame, text="Back", font=("Arial", 10), width=10, command=lambda: (win.destroy(), main_window()))
    back_btn.grid(row=9, column=1, pady=5)

    login_btn.bind("<Enter>", on_enter)
    login_btn.bind("<Leave>", on_leave)
    back_btn.bind("<Enter>", on_enter)
    back_btn.bind("<Leave>", on_leave)

    win.mainloop()

def load_logo():
    try:
        return tk.PhotoImage(file="logo.png")
    except:
        print("⚠ logo.png not found")
        return None

def main_window():
    win = tk.Tk()
    win.title("JOLLIDOG ORDERING SYSTEM")
    win.geometry("1920x1080")
    win.configure(bg="#940000")

    make_window_responsive(win, 800, 700)

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    main_frame = tk.Frame(win, bg="#2E2E2E")
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Adjust row weights
    main_frame.grid_rowconfigure(0, weight=2)  # Space for logo
    main_frame.grid_rowconfigure(1, weight=0)  # Welcome label
    main_frame.grid_rowconfigure(2, weight=0)  # Login button
    main_frame.grid_rowconfigure(3, weight=0)  # Register button
    main_frame.grid_rowconfigure(4, weight=0)  # Exit button
    main_frame.grid_rowconfigure(5, weight=2)  # Space at bottom

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=0)
    main_frame.grid_columnconfigure(2, weight=1)

    logo = load_logo()
    if logo:
        logo_label = tk.Label(main_frame, image=logo, bg="#2E2E2E")
        logo_label.image = logo
        logo_label.grid(row=0, column=1, pady=(40, 10))

    welcome_label = tk.Label(
        main_frame, text="Welcome to Jollidog",
        font=("Arial", 24, "bold"), fg="white", bg="#2E2E2E"
    )
    welcome_label.grid(row=1, column=1, pady=10)

    login_button = tk.Button(
        main_frame, text="Login", width=20, height=2, bg="white",
        font=("Arial", 12, "bold"),
        command=lambda: (win.destroy(), users_login_page())
    )
    login_button.grid(row=2, column=1, pady=10)

    register_button = tk.Button(
        main_frame, text="Register", width=20, height=2, bg="white",
        font=("Arial", 12, "bold"),
        command=lambda: (win.destroy(), register_page())
    )
    register_button.grid(row=3, column=1, pady=10)

    exit_button = tk.Button(
        main_frame, text="Exit", width=20, height=2, bg="red", fg="white",
        font=("Arial", 12, "bold"),
        command=win.destroy  # closes the window
    )
    exit_button.grid(row=4, column=1, pady=10)

    # Bind hover effects
    register_button.bind("<Enter>", on_enter)
    register_button.bind("<Leave>", on_leave)
    login_button.bind("<Enter>", on_enter)
    login_button.bind("<Leave>", on_leave)
    exit_button.bind("<Enter>", lambda e: e.widget.config(bg="#2E2E2E"))
    exit_button.bind("<Leave>", lambda e: e.widget.config(bg="red"))

    win.mainloop()

if __name__ == "__main__":
    main_window()