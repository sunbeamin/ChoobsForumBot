import sqlite3

class DatabaseInstance:
    def __init__(self, dbName):
        self.dbName = dbName
        try:
            self.dbConn = sqlite3.connect(self.dbName)
            print("Connected to the database")
        except sqlite3.Error as e:
            print(e)
            self.dbConn = None

    def incrementUserPostCounter(self, name):
        cursor = self.dbConn.execute(f"SELECT ID, PostCount from Users WHERE \"Name\"='{name}'")
        rows = cursor.fetchall()
        
        #No user with this name in our DB yet? Insert a new row
        if(len(rows) == 0):
            try:
                cursor = self.dbConn.execute(f"INSERT INTO Users (Name, PostCount) VALUES ('{name}', 1)")
                self.dbConn.commit()
            except sqlite3.Error as e:
                print(e)

        elif(len(rows) == 1):
            try:
                newCount = rows[0][1] + 1
                cursor = self.dbConn.execute(f"UPDATE Users SET PostCount = {newCount} where ID = {rows[0][0]}")
                self.dbConn.commit()     
            except sqlite3.Error as e:
                print(e)   
                
        else:
            print(f"Could not increment postcounter for user {name}")