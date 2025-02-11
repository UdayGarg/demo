# app/db/db_query.py

import sqlite3
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

def print_all_entries(db_path):
    console = Console()
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # This makes rows accessible as dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]

    if not tables:
        console.print("[bold red]No tables found in the database.[/bold red]")
    else:
        for table in tables:
            # Fetch all rows from the table
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()

            # Create a Rich Table for display
            rich_table = Table(title=f"Table: {table}", box=box.SIMPLE_HEAVY)
            
            if rows:
                # Get column headers from the first row
                headers = list(rows[0].keys())
                for header in headers:
                    rich_table.add_column(header, style="cyan", no_wrap=True)
                # Add each row of values
                for row in rows:
                    row_values = [str(row[col]) for col in headers]
                    rich_table.add_row(*row_values)
                console.print(rich_table)
            else:
                console.print(Panel(f"[yellow]No rows found in table '{table}'.[/yellow]", title=table))

    # Close the connection when done
    conn.close()

if __name__ == "__main__":
    # Adjust the path to your database file if necessary.
    db_file = "audit.db"
    if not os.path.exists(db_file):
        print(f"Database file '{db_file}' not found.")
    else:
        print_all_entries(db_file)