#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('top_500.db')

cursor = conn.cursor()
cursor.execute('''CREATE TABLE top500
                (date_captured text, rank text, ghzdays real, member_name text)''')
conn.commit()
conn.close()
