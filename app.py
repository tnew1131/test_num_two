import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3
import os
from openpyxl import Workbook

DB_NAME = 'inventory.db'

# Theme colors


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🗂️ Inventory Manager")
        self.root.configure(bg=DARK_BG)
        self.user_id = None
        self.build_login_screen()

    def build_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="🔐 Login", font=("Arial", 16), bg=DARK_BG, fg=DARK_FG).pack(pady=10)

        self.username_entry = tk.Entry(self.root, bg=ENTRY_BG, fg=ENTRY_FG)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Username")

        self.password_entry = tk.Entry(self.root, show="*", bg=ENTRY_BG, fg=ENTRY_FG)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Password")

        tk.Button(self.root, text="Login", command=self.login, bg=BTN_BG, fg=BTN_FG).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register, bg=BTN_BG, fg=BTN_FG).pack()

    def build_dashboard(self):
        self.clear_screen()

        tk.Label(self.root, text="📦 Inventory Dashboard", font=("Arial", 16), bg=DARK_BG, fg=DARK_FG).pack(pady=10)

        self.items_list = tk.Listbox(self.root, width=60, bg=ENTRY_BG, fg=ENTRY_FG)
        self.items_list.pack(pady=5)
        self.load_items()

        tk.Button(self.root, text="➕ Add Item", command=self.add_item, bg=BTN_BG, fg=BTN_FG).pack(pady=2)
        tk.Button(self.root, text="🗑️ Delete Selected", command=self.delete_item, bg=BTN_BG, fg=BTN_FG).pack(pady=2)
        tk.Button(self.root, text="📤 Export to Excel", command=self.export_to_excel, bg=BTN_BG, fg=BTN_FG).pack(pady=2)
        tk.Button(self.root, text="🔒 Logout", command=self.logout, bg=BTN_BG, fg=BTN_FG).pack(pady=5)

    def register(self):
        user = self.username_entry.get()
        pw = self.password_entry.get()
        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
            conn.commit()
            messagebox.showinfo("Success", "Registered successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        conn.close()

    def login(self):
        user = self.username_entry.get()
        pw = self.password_entry.get()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (user, pw))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.user_id = result[0]
            self.build_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def logout(self):
        self.user_id = None
        self.build_login_screen()

    def add_item(self):
        name = simpledialog.askstring("Item Name", "Enter item name:")
        if not name:
            return
        qty = simpledialog.askinteger("Quantity", "Enter quantity:")
        if qty is None:
            return
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)",
                     (self.user_id, name, qty))
        conn.commit()
        conn.close()
        self.load_items()

    def load_items(self):
        self.items_list.delete(0, tk.END)
        conn = sqlite3.connect(DB_NAME)
        rows = conn.execute("SELECT id, item_name, quantity FROM inventory WHERE user_id=?", (self.user_id,))
        for row in rows:
            self.items_list.insert(tk.END, f"ID: {row[0]} | {row[1]} - Qty: {row[2]}")
        conn.close()

    def delete_item(self):
        selected = self.items_list.curselection()
        if not selected:
            return
        item_text = self.items_list.get(selected[0])
        item_id = int(item_text.split('|')[0].split(':')[1].strip())
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM inventory WHERE id=? AND user_id=?", (item_id, self.user_id))
        conn.commit()
        conn.close()
        self.load_items()
## حمود محمود 
    

        if not items:
            messagebox.showinfo("No Data", "No items to export.")
            return

        wb = Workbook()
        ws = wb.active
        ws.append(["Item Name", "Quantity"])

        for item in items:
            ws.append(item)

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb.save(file_path)
            messagebox.showinfo("Exported", f"Data exported to {file_path}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run app
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.geometry("500x500")
    app = InventoryApp(root)
    root.mainloop()

