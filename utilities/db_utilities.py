import sqlite3


def create_db(db_name):
    """
    Create Database of Top 500 ranks for the last 365 days.
    :param db_name: Name of sqlite3 DB file to create.
    :return:
    """
    print("Building database file named {}.".format(db_name))

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE top500
                    (date_captured text, rank text, ghzdays real, member_name text,
                    UNIQUE (date_captured, rank) ON CONFLICT IGNORE)''')
    conn.commit()
    conn.close()


def add_today_ranks(data: str, db_name: str):
    """
    Grab today's Top 500 rank and values.  Add them to the database.
    :param data: List of today's data parsed from Top 500 table.
    :param db_name:
    :return:
    """
    print("Adding today's Top 500 data into DB named {}.".format(db_name))
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.executemany('INSERT INTO top500 VALUES(?, ?, ?, ?)', data)

    conn.commit()
    conn.close()
