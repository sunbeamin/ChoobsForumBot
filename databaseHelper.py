import sqlite3

class ChoobsDatabase:
    """
    This class is an interface for transferring data from and to the 
    local sqlite db. Make an instance of this class to initiate the connection.
    Call fucntions on the class to interact with the databasze

    Parameters
    ----------
    dbName : `str`\n
        Name of the local db file

    """
    def __init__(self, dbName):
        self.dbName = dbName
        try:
            self.dbConn = sqlite3.connect(self.dbName)
            print("Connected to the database")
        except sqlite3.Error as e:
            print(e)
            self.dbConn = None


    def incrementUserPostCounter(self, name):
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
        cursor = self.dbConn.execute(f"SELECT ID, PostCount from Users WHERE \"Name\"='{name}'")
        rows = cursor.fetchall()
        
        #No user with this name in our DB yet? Insert a new row
        if(len(rows) == 0):
            try:
                postCount = 1
                cursor = self.dbConn.execute(f"INSERT INTO Users (Name, PostCount) VALUES ('{name}', 1)")
                self.dbConn.commit()
            except sqlite3.Error as e:
                print(e)

        elif(len(rows) == 1):
            try:
                postCount = rows[0][1] + 1
                cursor = self.dbConn.execute(f"UPDATE Users SET PostCount = {postCount} where ID = {rows[0][0]}")
                self.dbConn.commit()     
            except sqlite3.Error as e:
                print(e)   
                
        else:
            postCount = 0
            print(f"Could not increment postcounter for user {name}")

        return postCount

    def getPostCountHiscores(self):
        """
        Gets a list of 10 users with highest postcount
        
        Returns
        ----------
        List of tuples with names and their respective post count
        """
        try:
            cursor = self.dbConn.execute("SELECT Name, PostCount FROM Users ORDER BY PostCount DESC LIMIT 10;")
        except sqlite3.Error as e:
                print(e)   
        return cursor.fetchall()