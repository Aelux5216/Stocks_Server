import asyncore
import socket
import sqlite3
from sqlite3 import Error
import sys
import socket

#Test data
testsym = "Bob"
testcomp = "Bobbers"
testprice = 120.33
testquant = 100

connection = sqlite3.connect("Stocks.db") #Connect to the database
cursor = connection.cursor() #Create instance that allows me to enter commands
'''
query = str.format("INSERT INTO DATABASE (SYMBOL, COMPANY, PRICE, QUANTITY) VALUES (''{0}'', ''{1}'', '{2}', '{3}')", testsym,testcomp,testprice,testquant) #How to run a sql command
cursor.execute(query) #Run the query
connection.commit() #Save changes to the database
'''

class Handle_Data(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(1024)

        data2 = data.decode('ascii')

        if data2:
            try:
                if data2 == "RequestDB":
                    query = "SELECT Symbol, Company, Price, Quantity FROM Stocks"
                    cursor.execute(query)
                    stringbuilder = ""
                    for row in cursor:
                        for cell in row:
                            cellF = str.format("{0}$",cell)
                            stringbuilder = stringbuilder + cellF
                    self.send(stringbuilder.encode())

                elif "GetOwnedStocks" in data2:
                    data3 = data2.split("$")
                    username = data3[1]
                    try:
                        query = "SELECT * FROM Usernames"
                        cursor.execute(query)
                        #Database exists

                        try:
                            query = str.format("SELECT Username FROM Usernames WHERE Username = '{0}'",username)
                            cursor.execute(query)

                            query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username)
                            cursor.execute(query)
                            
                            stringbuilder = ""

                            for row in cursor:
                                for cell in row:
                                    cellF = str.format("{0}$",cell)
                                    stringbuilder = stringbuilder + cellF

                            self.send(stringbuilder.encode())
                        except:
                            stringbuilder = "" 

                            query = str.format("INSERT INTO Usernames (Username) VALUES ('{0}')",username)
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("CREATE TABLE {0}OwnedStocks (StockID INTEGER, Symbol TEXT, Company TEXT, Price TEXT, Quantity INTEGER)",username)
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("INSERT INTO {0}OwnedStocks SELECT StockID,Symbol,Company,Price,Quantity FROM Stocks",username)
                            cursor.execute(query)
                            connection.commit()
                        
                            query = str.format("ALTER TABLE {0}OwnedStocks ADD OwnedStocks INTEGER",username)
                            cursor.execute(query)
                            connection.commit()
                        
                            query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = 0 WHERE Symbol IS NOT NULL",username)
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("CREATE TABLE {0}PurchaseHistory (PurchaseTimestamp DATETIME,Description TEXT)",username)
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username)
                            cursor.execute(query)

                            stringbuilder = ""

                            for row in cursor:
                                for cell in row:
                                    cellF = str.format("{0}$",cell)
                                    stringbuilder = stringbuilder + cellF

                            self.send(stringbuilder.encode())
                             
                    except:
                        
                        query = "CREATE TABLE Usernames (Username TEXT)"
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("INSERT INTO Usernames (Username) VALUES ('{0}')",username)
                        cursor.execute(query)
                        connection.commit()

                        query = "ALTER TABLE Usernames ADD Balance DECIMAL"
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("CREATE TABLE {0}OwnedStocks (StockID INTEGER, Symbol TEXT, Company TEXT, Price TEXT, Quantity INTEGER)",username)
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("INSERT INTO {0}OwnedStocks SELECT StockID,Symbol,Company,Price,Quantity FROM Stocks",username)
                        cursor.execute(query)
                        connection.commit()
                        
                        query = str.format("ALTER TABLE {0}OwnedStocks ADD OwnedStocks INTEGER",username)
                        cursor.execute(query)
                        connection.commit()
                        
                        query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = 0 WHERE Symbol IS NOT NULL",username)
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("CREATE TABLE {0}PurchaseHistory (PurchaseTimestamp DATETIME,Description TEXT)",username)
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username)
                        cursor.execute(query)

                        stringbuilder = ""

                        for row in cursor:
                            for cell in row:
                                cellF = str.format("{0}$",cell)
                                stringbuilder = stringbuilder + cellF

                        self.send(stringbuilder.encode())

                elif "GetPurchaseHistory" in data2:
                    data3 = data2.split("$")
                    username = data3[1]
                    query = str.format("SELECT * FROM {0}PurchaseHistory",username)
                    connection.execute(query)
                    
                    stringbuilder = ""

                    for row in cursor:
                        for cell in row:
                            cellF = str.format("{0}$",cell)
                            stringbuilder = stringbuilder + cellF

                    self.send(stringbuilder.encode())

                elif "GetBalance" in data2:
                    data3 = data2.split("$")
                    username = data3[1]
                    balance = data3[2].replace(',','')
                    
                    query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username)

                    connection.execute(query)

                    stringbuilder = ""

                    for row in cursor.execute(query):
                        stringbuilder = str.format("{0}",row[0])

                    if stringbuilder == 'None':
                        #Balance doesnt exist
                        query = str.format("UPDATE Usernames SET Balance = {0} WHERE Username = '{1}'",balance,username,)
                        connection.execute(query)
                        connection.commit()
                        
                        query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username)
                        connection.execute(query)

                        stringbuilder = ""

                        for row in cursor.execute(query):
                            stringbuilder = str.format("{0}",row[0])

                        self.send(stringbuilder.encode())
                    else:
                        #Balance exists
                        query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username)
                        connection.execute(query)

                        stringbuilder = ""

                        for row in cursor.execute(query):
                            stringbuilder = str.format("{0}",row[0])

                        self.send(stringbuilder.encode())

                elif "BuyStock" in data2:
                    data3 = data2.split("$")
                    query = str.format("UPDATE Stocks SET Quantity = Quantity -1 WHERE Symbol = '{0}'",data3[1])
                    try:
                        cursor.execute(query)
                        connection.commit()
                        self.send(("Success").encode())
                    except:
                        self.send(("Fail").encode())
                elif "SellStock" in data2:
                    data3 = data2.split("$")
                    query = str.format("UPDATE Stocks SET Quantity = Quantity +1 WHERE Symbol = '{0}'",data3[1])
                    try:
                        cursor.execute(query)
                        connection.commit()
                        self.send(("Success").encode())
                    except:
                        self.send(("Fail").encode())
            except:
                print("Unexpected error:", sys.exc_info())
        else:
            pass

class Server(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        print("listening..")

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print (str.format("Incoming connection from '{0}'",repr(addr)))
            handler = Handle_Data(sock)
            print("listening..")

server = Server('0.0.0.0', 8000)
asyncore.loop()
