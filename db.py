import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SQLite:
    """
    This class is a context manager for the database.
    Use this for handling db operations within this file
    """
    def __init__(self):
        self.dbName = os.path.join(BASE_DIR, "ChoobsForum.db")
    def __enter__(self):
        self.conn = sqlite3.connect(self.dbName)
        return self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

class NotFoundError(Exception):
    pass

def incrementUserPostCounter(name):
    """
    Increment the post count variable of given user by 1

    Parameters
    ----------
    name : `str`\n
        Name of the user to increment postcount for
    
    Returns
    ----------
    postCount : `int`\n
        The postcount after increment
    """
    postCount = 0

    with SQLite() as cur:
        try:
            results = cur.execute(f"SELECT ID, PostCount from Users WHERE \"Name\"='{name}'")
            rows = results.fetchall()

            #No user with this name in our DB yet? Insert a new row
            if(len(rows) == 0):
                cur.execute(f"INSERT INTO Users (Name, PostCount) VALUES ('{name}', 1)")

            #If user was found, increment post count by 1 
            elif(len(rows) == 1):
                postCount = rows[0][1] + 1
                cur.execute(f"UPDATE Users SET PostCount = {postCount} where ID = {rows[0][0]}")  

            else:
                postCount = 0
                raise NotFoundError(f"Unable to find user: {name}")

            return postCount

        except sqlite3.Error as e:
            print(e)

def getAssignedRole(name):
    """
    Get the assigned role for a user

    Parameters
    ----------
    name : `str`\n
        Name of the user to get role for
    
    Returns
    ----------
    role : `int`\n
        currently assigned role
    """
    rows = None

    with SQLite() as cur:
        try:
            cursor = cur.execute(f"SELECT AssignedRole from Users WHERE \"Name\"='{name}'")
            rows = cursor.fetchone()
            if rows is None:
                raise NotFoundError(f"Unable to find role of user: {name}")
            
            return rows[0]
        except sqlite3.Error as e:
            print(e)
            raise NotFoundError(f"Unable to find role of user: {name}")



def setAssignedRole(name, role):
    """
    Set the assigned role for a user

    Parameters
    ----------
    name : `str`\n
        Name of the user to set role for
    role : `int`\n
        Role enum to write
    """
    with SQLite() as cur:
        try:
            cur.execute(f"UPDATE Users SET AssignedRole = {role} WHERE \"Name\"='{name}'")
        except sqlite3.Error as e:
            print(e)
            raise NotFoundError(f"Unable to find role of user: {name}")

def getPostCountHiscores():
    """
    Gets a list of 10 users with highest postcount
    
    Returns
    ----------
    List of tuples with names and their respective post count
    """
    with SQLite() as cur:
        try:
            cur.execute("SELECT Name, PostCount FROM Users ORDER BY PostCount DESC LIMIT 10;")
            return cur.fetchall()
        except sqlite3.Error as e:
                print(e)   