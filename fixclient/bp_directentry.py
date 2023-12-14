import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import uuid
import baripool_action

def unique_id():
    return str(uuid.uuid4())[:8]

def submit_form():
    side_value = side_var.get()
    if side_value == "Buy":
        side_value = "1"
    elif side_value == "Sell":
        side_value = "2"
    fix_message = f"11={unique_id()};54={side_value};55={symbol_entry.get()};38={quantity_entry.get()};44={price_entry.get()};49={sender_entry.get()}"
    # also simulate some trades to match with
    baripool_action.bp_directentry_sim()
    output = baripool.on_new_order(fix_message)
    output_box.insert(tk.END, output)  # Insert the output at the end of the output box
    output_box.insert(tk.END, "\n")  # Add a newline to separate outputs
    output_box.see(tk.END)  # Scroll to the end of the output box

root = tk.Tk()
root.title("Order Entry")
root.configure(bg='#F0F0F0')

style = ttk.Style()
style.configure('TFrame', background='#F0F0F0')
style.configure('TLabel', background='#F0F0F0', font=('Arial', 12, 'bold'))
style.configure('TButton', font=('Arial', 12, 'bold'))
style.configure('TEntry', font=('Arial', 12))

mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
mainframe['padding'] = (30, 15)
font = ('Arial', 12)

# Create a StringVar for the dropdown
side_var = tk.StringVar()

# Create a StringVar for the dropdown
side_var = tk.StringVar()

# Create the dropdown with options "Buy" and "Sell"
side_dropdown = ttk.Combobox(mainframe, textvariable=side_var)
side_dropdown['values'] = ("Buy", "Sell")
side_dropdown.grid(column=1, row=0, padx=10, pady=10)
side_dropdown.current(0)  # set initial value to "Buy"

# Change the entry for the side to use the StringVar
side_entry = ttk.Entry(mainframe, textvariable=side_var, font=font)
side_entry.grid_forget()

symbol_entry = ttk.Entry(mainframe, font=font)
symbol_entry.grid(column=1, row=1, padx=10, pady=10)

quantity_entry = ttk.Entry(mainframe, font=font)
quantity_entry.grid(column=1, row=2, padx=10, pady=10)

price_entry = ttk.Entry(mainframe, font=font)
price_entry.grid(column=1, row=3, padx=10, pady=10)

sender_entry = ttk.Entry(mainframe, font=font)
sender_entry.grid(column=1, row=4, padx=10, pady=10)

label_font = ('Arial', 12, 'bold')

ttk.Label(mainframe, text="Side (54):", font=label_font).grid(column=0, row=0, sticky=tk.E)
ttk.Label(mainframe, text="Symbol (55):", font=label_font).grid(column=0, row=1, sticky=tk.E)
ttk.Label(mainframe, text="Quantity (38):", font=label_font).grid(column=0, row=2, sticky=tk.E)
ttk.Label(mainframe, text="Price (44):", font=label_font).grid(column=0, row=3, sticky=tk.E)
ttk.Label(mainframe, text="SenderCompID (49):", font=label_font).grid(column=0, row=4, sticky=tk.E)

submit_button = ttk.Button(mainframe, text="Submit Order", command=submit_form)
submit_button.grid(column=1, row=5, pady=20)

output_box = scrolledtext.ScrolledText(mainframe, wrap=tk.WORD, width=40, height=10, font=('Arial', 12))
output_box.grid(column=0, row=6, columnspan=2, pady=10)

root.mainloop()