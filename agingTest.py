import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
from datetime import date
import math

def select_csv_file():
    """Opens a file dialog to select a CSV file and prints its path."""
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        print(f"Selected file path: {file_path}")
        with open(file_path, mode= 'r') as file: 
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # create a list of lists
            # format:  ['ID', 'Date', 'Sale', 'Type', 'Gift Card #', 'Amount', 'Refund', 'Original Type', 'Original Amount', 'Customer']
            payments_list = list(csv_reader)

            # Strip header row, sort remainder by "ID" so list is in chronological order
            header = payments_list[0:1]
            data_rows = payments_list[1:]
            data_rows.sort(key=lambda row: int(row[0]))
            sortedList = header + data_rows

            # Convert "Amount" in each row to float
            for sublist in sortedList[1:]:  # Start from index 1 to skip the header row
                try:
                    sublist[5] = float(sublist[5][1:])  # note: [1:] is used in the second index because the first character in "Amount" is "$"
                except ValueError:
                    # Handle cases where conversion is not possible (e.g., if there are non-numeric entries)
                    print(f"Could not convert {sublist[5]} to float. Skipping.")
                    pass

            # define variables
            debits = 0.0
            credits = 0.0
            paidInvoices = []
            unpaidInvoices = []
            remainingCredit = 0.0

            # For each Credit Account "Type" row, add "Amount" to debits or credits depending on sign of "Amount"
            for row in sortedList:
                if row[3] == "Credit Account":
                    if row[5] > 0:
                        debits += row[5]
                    else:
                        credits += row[5]

            # We subtract from this in the loop below
            remainingCredit = credits

            # If money is owed, iterate through all payments, deducting each debit amount on account from available credit.
            # If debit amount is fully covered by available credit, add "Sale" number to list of paid invoices.
            # When credit runs out (remainingCredit >= 0), break out of loop, saving the "Sale" number as first entry in a list of unpaid invoices.
            if debits > abs(credits):
                for row in sortedList:
                    if row[3] == "Credit Account":
                        if row[5] > 0:
                            remainingCredit += row[5]
                            if remainingCredit < 0.005: # allow for rounding error with floats
                                paidInvoices.append([row[2], row[1], row[5]])
                            else:
                                #print(remainingCredit)
                                unpaidInvoices.append([row[2], row[1], round(remainingCredit, 2)])
                                break

            foundFirstUnpaidInvoiceFlag = 0
            totalBalance = 0.0

            try:
                if unpaidInvoices[0]:
                    for row in sortedList:
                        if row[2] == unpaidInvoices[0][0]:
                            foundFirstUnpaidInvoiceFlag = 1
                        elif foundFirstUnpaidInvoiceFlag:
                            if row[3] == "Credit Account":
                                if row[5] > 0:
                                    unpaidInvoices.append([row[2], row[1], row[5]])

                # Find the Days Past for each unpaid invoice and add this to the list.
                for row in unpaidInvoices:
                    subString = row[1].partition(' ')[0]
                    dt_obj1 = date.today()
                    dt_obj2 = datetime.strptime(subString, "%Y-%m-%d").date()
                    difference = dt_obj1 - dt_obj2
                    days_difference = difference.days
                    row.append(days_difference)
                    totalBalance += row[2]
                print(totalBalance)
                print(unpaidInvoices)

                unpaidInvoices.insert(0, ["Sale #", "Date", "Amount Owed", "Days Past"])

                with open(file_path, mode='r', newline='') as file:
                    reader = csv.reader(file)
                    existing_data = list(reader)
                    data_to_write = unpaidInvoices + existing_data

                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(data_to_write)
                    status_label.config(text=f"Unpaid Invoices Written to CSV File")
                    
            except:
                print("Nothing Owed")
                status_label.config(text=f"No Unpaid Invoices")




root = tk.Tk()
root.title("CSV File Selector")
root.geometry("400x150") # Set initial window size

# Add a button to open the file dialog
select_button = tk.Button(
    root,
    text="Browse for CSV File",
    command=select_csv_file
)
select_button.pack(pady=20)

status_label = tk.Label(
    root, 
    text="Please Select Payments CSV file...", 
    wraplength=350
)
status_label.pack(pady=10)

root.mainloop()
