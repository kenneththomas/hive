import tkinter as tk
from tkinter import ttk, scrolledtext, font
import sys
import time
from datetime import datetime
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests')
import baripool
import uuid
import baripool_action

def unique_id():
    return str(uuid.uuid4())[:8]

def update_clock():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d-%b-%Y")
    time_label.config(text=f"{current_time}")
    date_label.config(text=f"{current_date}")
    root.after(1000, update_clock)

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
    timestamp = datetime.now().strftime("%H:%M:%S")
    output_box.insert(tk.END, f"[{timestamp}] {output}\n")
    output_box.see(tk.END)  # Scroll to the end of the output box
    status_var.set("ORDER SENT")
    root.after(2000, lambda: status_var.set("READY"))

root = tk.Tk()
root.title("BariPool Terminal")
root.configure(bg='black')

# Bloomberg-inspired color scheme
colors = {
    'bg': 'black',
    'text': '#FFFFFF',
    'highlight': '#FF8000',  # Bloomberg orange
    'header': '#004080',     # Dark blue for headers
    'input_bg': '#151515',   # Very dark gray
    'border': '#333333',     # Border color
    'green': '#33FF33',      # For "Buy" actions
    'red': '#FF3333',        # For "Sell" actions
    'status': '#303030'      # Status bar background
}

# Create custom font that resembles terminal text
terminal_font = font.nametofont("TkFixedFont").copy()
terminal_font.configure(size=10, family="Courier")
header_font = font.Font(family="Arial", size=11, weight="bold")
title_font = font.Font(family="Arial", size=14, weight="bold")

# Configure ttk styles
style = ttk.Style()
style.theme_use('alt')  # Start with a simple theme as base
style.configure('TFrame', background=colors['bg'])
style.configure('Header.TFrame', background=colors['header'])
style.configure('Status.TFrame', background=colors['status'])

style.configure('TLabel', 
                background=colors['bg'], 
                foreground=colors['text'], 
                font=terminal_font)
                
style.configure('Header.TLabel', 
                background=colors['header'], 
                foreground=colors['text'], 
                font=header_font)
                
style.configure('Title.TLabel', 
                background=colors['bg'], 
                foreground=colors['highlight'], 
                font=title_font)
                
style.configure('Status.TLabel', 
                background=colors['status'], 
                foreground=colors['text'], 
                font=terminal_font)
                
style.configure('Time.TLabel', 
                background=colors['bg'], 
                foreground=colors['highlight'], 
                font=terminal_font)

style.configure('TButton', 
                font=terminal_font, 
                background=colors['bg'], 
                foreground=colors['highlight'],
                borderwidth=1)
                
style.map('TButton',
    background=[('active', colors['highlight']), ('pressed', colors['header'])],
    foreground=[('active', 'black'), ('pressed', 'white')])
    
style.configure('TEntry', 
                font=terminal_font, 
                fieldbackground=colors['input_bg'], 
                foreground=colors['text'],
                borderwidth=1)
                
style.configure('TCombobox', 
                fieldbackground=colors['input_bg'], 
                foreground=colors['text'], 
                background=colors['input_bg'],
                arrowcolor=colors['highlight'])
                
style.map('TCombobox',
    fieldbackground=[('readonly', colors['input_bg'])],
    background=[('readonly', colors['input_bg'])],
    foreground=[('readonly', colors['text'])])

# Main layout
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# Header bar
header_frame = ttk.Frame(root, style='Header.TFrame')
header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
header_frame.grid_columnconfigure(0, weight=1)

ttk.Label(header_frame, text="BARIPOOL TRADING TERMINAL", style='Header.TLabel').grid(row=0, column=0, padx=10, pady=5, sticky="w")
date_label = ttk.Label(header_frame, text="", style='Header.TLabel')
date_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
time_label = ttk.Label(header_frame, text="", style='Header.TLabel')
time_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

# Main content frame
mainframe = ttk.Frame(root)
mainframe.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
mainframe.grid_columnconfigure(1, weight=1)
mainframe.grid_rowconfigure(6, weight=1)

# Title
ttk.Label(mainframe, text="ORDER ENTRY", style='Title.TLabel').grid(column=0, row=0, columnspan=2, sticky="w", padx=5, pady=10)

# Create a StringVar for the dropdown and status
side_var = tk.StringVar()
status_var = tk.StringVar(value="READY")

# Form fields with Bloomberg-style labels
field_labels = ['SIDE:', 'SYMBOL:', 'QTY:', 'PRICE:', 'SENDER:']
field_tags = ['(54)', '(55)', '(38)', '(44)', '(49)']

# Side dropdown
ttk.Label(mainframe, text=f"{field_labels[0]} {field_tags[0]}", style='TLabel').grid(column=0, row=1, sticky="e", padx=5, pady=2)
side_dropdown = ttk.Combobox(mainframe, textvariable=side_var, style='TCombobox', width=15)
side_dropdown['values'] = ("Buy", "Sell")
side_dropdown.grid(column=1, row=1, sticky="w", padx=5, pady=2)
side_dropdown.current(0)
side_dropdown.configure(state='readonly')

# Symbol entry
ttk.Label(mainframe, text=f"{field_labels[1]} {field_tags[1]}", style='TLabel').grid(column=0, row=2, sticky="e", padx=5, pady=2)
symbol_entry = ttk.Entry(mainframe, font=terminal_font, width=15)
symbol_entry.grid(column=1, row=2, sticky="w", padx=5, pady=2)

# Quantity entry
ttk.Label(mainframe, text=f"{field_labels[2]} {field_tags[2]}", style='TLabel').grid(column=0, row=3, sticky="e", padx=5, pady=2)
quantity_entry = ttk.Entry(mainframe, font=terminal_font, width=15)
quantity_entry.grid(column=1, row=3, sticky="w", padx=5, pady=2)

# Price entry
ttk.Label(mainframe, text=f"{field_labels[3]} {field_tags[3]}", style='TLabel').grid(column=0, row=4, sticky="e", padx=5, pady=2)
price_entry = ttk.Entry(mainframe, font=terminal_font, width=15)
price_entry.grid(column=1, row=4, sticky="w", padx=5, pady=2)

# Sender entry
ttk.Label(mainframe, text=f"{field_labels[4]} {field_tags[4]}", style='TLabel').grid(column=0, row=5, sticky="e", padx=5, pady=2)
sender_entry = ttk.Entry(mainframe, font=terminal_font, width=15)
sender_entry.grid(column=1, row=5, sticky="w", padx=5, pady=2)

# Output box (bordered to look like a terminal window)
output_frame = ttk.Frame(mainframe, borderwidth=2, relief="solid")
output_frame.grid(column=0, row=6, columnspan=2, sticky="nsew", padx=5, pady=10)
output_frame.grid_columnconfigure(0, weight=1)
output_frame.grid_rowconfigure(0, weight=1)

output_box = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=terminal_font)
output_box.grid(column=0, row=0, sticky="nsew", padx=1, pady=1)
output_box.configure(bg=colors['input_bg'], fg=colors['text'], insertbackground=colors['highlight'])
output_box.insert(tk.END, "*** BARIPOOL TRADING TERMINAL READY ***\n")

# Function key bar
function_frame = ttk.Frame(mainframe)
function_frame.grid(column=0, row=7, columnspan=2, sticky="ew", padx=5, pady=5)

f_keys = [
    ("F1:Help", lambda: None),
    ("F2:Submit", submit_form),
    ("F3:Clear", lambda: [e.delete(0, 'end') for e in [symbol_entry, quantity_entry, price_entry, sender_entry]]),
    ("F4:Exit", root.destroy)
]

for i, (text, cmd) in enumerate(f_keys):
    btn = ttk.Button(function_frame, text=text, command=cmd)
    btn.grid(column=i, row=0, padx=5, pady=2)
    function_frame.grid_columnconfigure(i, weight=1)

# Status bar
status_frame = ttk.Frame(root, style='Status.TFrame')
status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
status_frame.grid_columnconfigure(0, weight=1)

status_label = ttk.Label(status_frame, textvariable=status_var, style='Status.TLabel')
status_label.grid(row=0, column=0, sticky="w", padx=10, pady=3)

# Set window size and start the clock
root.geometry("700x600")
update_clock()
root.mainloop()