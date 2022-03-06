"""Import sqlite3"""
import sqlite3

def create_db():
    """Try and create a database called 'team_stats'"""
    try:
        sqlite_connection = sqlite3.connect('SQLite_Python.db')
        sqlite_create_table_query = '''CREATE TABLE team_stats (
                                    team_name text NOT NULL,
                                    won_games_as_home_team integer NOT NULL,
                                    won_games_as_visitor_team integer NOT NULL,
                                    lost_games_as_home_team integer NOT NULL,
                                    lost_games_as_visitor_team integer NOT NULL);'''

        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        print("SQLite table 'team_stats' created")

        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating SQLite table, reason:", error)


def insert_records(season_games):
    """Insert data into an existing table created by create_db"""

    try:
        sqlite_connection = sqlite3.connect('SQLite_Python.db')
        cursor = sqlite_connection.cursor()
        print("Successfully connected to SQLite")
        print("Adding records.")
        for entry in season_games:
            data = (
                entry['team_name'],
                entry['won_games_as_home_team'],
                entry['won_games_as_visitor_team'],
                entry['lost_games_as_home_team'],
                entry['lost_games_as_visitor_team'],
                )
            sqlite_insert_query = """INSERT INTO team_stats
                                (team_name, won_games_as_home_team, won_games_as_visitor_team, lost_games_as_home_team, lost_games_as_visitor_team) 
                                VALUES 
                                (?,?,?,?,?)"""

            cursor.execute(sqlite_insert_query, data)
        sqlite_connection.commit()
        print("Records inserted successfully into team_stats table.")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into SQLite table, reason: ", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("SQLite connection is closed.")
