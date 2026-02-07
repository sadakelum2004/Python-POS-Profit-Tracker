import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# --- 1. Database Setup ---
def init_db():
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY, name TEXT, qty INTEGER, cost_price REAL, sell_price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
                      (id INTEGER PRIMARY KEY, name TEXT, qty INTEGER, profit REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. Functions ---
def get_total_profit():
    try:
        conn = sqlite3.connect('pos_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(profit) FROM sales")
        total = cursor.fetchone()[0]
        conn.close()
        return total if total else 0.0
    except:
        return 0.0

def view_stock():
    for i in tree.get_children():
        tree.delete(i)
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()
    # පරණ වැරැද්ද මෙතන නිවැරදි කර ඇත
    total_prof = get_total_profit()
    lbl_profit_val.config(text=f"Rs. {total_prof:.2f}")

def add_stock():
    name, qty, cost, sell = ent_name.get(), ent_qty.get(), ent_cost.get(), ent_sell.get()
    if not (name and qty and cost and sell):
        messagebox.showwarning("Error", "Please fill all fields!")
        return
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT qty FROM inventory WHERE name=?", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET qty=qty+?, cost_price=?, sell_price=? WHERE name=?", (qty, cost, sell, name))
    else:
        cursor.execute("INSERT INTO inventory (name, qty, cost_price, sell_price) VALUES (?, ?, ?, ?)", (name, qty, cost, sell))
    conn.commit()
    conn.close()
    view_stock()
    clear_fields()

def make_sale():
    name, qty_to_sell = ent_name.get(), ent_qty.get()
    if not (name and qty_to_sell):
        messagebox.showwarning("Error", "Enter Name and Qty!")
        return
    conn = sqlite3.connect('pos_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT qty, cost_price, sell_price FROM inventory WHERE name=?", (name,))
    row = cursor.fetchone()
    if row and row[0] >= int(qty_to_sell):
        qty_val = int(qty_to_sell)
        profit = (row[2] - row[1]) * qty_val
        cursor.execute("UPDATE inventory SET qty=qty-? WHERE name=?", (qty_val, name))
        cursor.execute("INSERT INTO sales (name, qty, profit) VALUES (?, ?, ?)", (name, qty_val, profit))
        conn.commit()
        messagebox.showinfo("Success", f"Sale Done! Profit: Rs.{profit:.2f}")
    else:
        messagebox.showerror("Error", "Stock issue!")
    conn.close()
    view_stock()

def clear_fields():
    ent_name.delete(0, tk.END); ent_qty.delete(0, tk.END)
    ent_cost.delete(0, tk.END); ent_sell.delete(0, tk.END)

# --- 3. GUI Layout ---
root = tk.Tk()
root.title("Modern POS Dashboard")
root.geometry("900x650")

# Header
header = tk.Frame(root, bg="#2c3e50", height=80)
header.pack(fill="x")
tk.Label(header, text="Inventory & Profit Tracker", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=10)

# Dashboard Summary
summary_frame = tk.Frame(root, pady=10)
summary_frame.pack()
tk.Label(summary_frame, text="TOTAL PROFIT:", font=("Arial", 12)).grid(row=0, column=0)
lbl_profit_val = tk.Label(summary_frame, text="Rs. 0.00", font=("Arial", 14, "bold"), fg="green")
lbl_profit_val.grid(row=0, column=1, padx=10)

# Input Area
input_frame = tk.LabelFrame(root, text=" Manage Stock ", padx=10, pady=10)
input_frame.pack(padx=20, pady=10, fill="x")

tk.Label(input_frame, text="Product:").grid(row=0, column=0)
ent_name = tk.Entry(input_frame); ent_name.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Qty:").grid(row=0, column=2)
ent_qty = tk.Entry(input_frame); ent_qty.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Cost:").grid(row=0, column=4)
ent_cost = tk.Entry(input_frame); ent_cost.grid(row=0, column=5, padx=5)

tk.Label(input_frame, text="Sell:").grid(row=0, column=6)
ent_sell = tk.Entry(input_frame); ent_sell.grid(row=0, column=7, padx=5)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Add Stock", command=add_stock, bg="blue", fg="white", width=15).pack(side="left", padx=10)
tk.Button(btn_frame, text="Sale", command=make_sale, bg="orange", fg="white", width=15).pack(side="left", padx=10)

# Table
tree_frame = tk.Frame(root)
tree_frame.pack(expand=True, fill="both", padx=20, pady=10)
cols = ("ID", "Name", "Qty", "Cost Price", "Sell Price")
tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=100, anchor="center")
tree.pack(expand=True, fill="both")

view_stock()
root.mainloop()