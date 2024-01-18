import asyncore #Import modules
import socket
import sqlite3
from sqlite3 import Error
import sys
import socket
from datetime import datetime, date, time

connection = sqlite3.connect("Stocks.db") #Connect to the database 
cursor = connection.cursor() #Create instance that allows me to enter commands

class Handle_Data(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(1024) #Recieve data from the client.

        data2 = data.decode('ascii') #Decode the data recieved from ascii(since it was sent from c# code it will be in ascii).

        if data2: #If there is any data run a command. 
            try:
                if data2 == "RequestDB": #This command selects all the columns from my Stocks table.
                    query = "SELECT Symbol, Company, Price, Quantity FROM Stocks"
                    cursor.execute(query)
                    stringbuilder = ""
                    for row in cursor:   #This loops over every row and cell from the query ran above 
                        for cell in row: #which gets all my data from the stocks table.
                            cellF = str.format("{0}$",cell)
                            stringbuilder = stringbuilder + cellF
                    self.send(stringbuilder.encode()) #Send the data with defualt encoding.

                elif "GetOwnedStocks" in data2: #This command gets the stocks that are owned by the person signed in.
                    data3 = data2.split("$")
                    username = data3[1] #This gets the username from the data recieved.
                    try:
                        query = "SELECT * FROM Usernames" #Check to see if the Usernames table exists.
                        cursor.execute(query)
                        #Database exists

                        try:
                            query = str.format("SELECT Username FROM Usernames WHERE Username = '{0}'",username) #Check to see if username exists.
                            cursor.execute(query)

                            query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username) #If the username exists get the stocks that they own.
                            cursor.execute(query)
                            
                            stringbuilder = ""

                            for row in cursor: #If username exists loop over the query results and add to string with delimiter.
                                for cell in row:
                                    cellF = str.format("{0}$",cell)
                                    stringbuilder = stringbuilder + cellF

                            self.send(stringbuilder.encode()) #Send the data with default encoding.
                        except:
                            #If username doesnt exists.
                            stringbuilder = "" 

                            query = str.format("INSERT INTO Usernames (Username) VALUES ('{0}')",username) #Add username to database.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("CREATE TABLE {0}OwnedStocks (Symbol TEXT)",username) #Create Database of stocks.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("INSERT INTO {0}OwnedStocks SELECT Symbol FROM Stocks",username) #Insert all of the stock information into a new table based on the username. 
                            cursor.execute(query)
                            connection.commit()
                        
                            query = str.format("ALTER TABLE {0}OwnedStocks ADD OwnedStocks INTEGER",username) #Insert a new column which will contain the owned stocks of the user.
                            cursor.execute(query)
                            connection.commit()
                        
                            query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = 0 WHERE Symbol IS NOT NULL",username) #Set all owned stocks to 0 as no stocks will be owned at this point.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("CREATE TABLE {0}PurchaseHistory (ID INTEGER, Description TEXT,PRIMARY KEY(ID))",username) #Add purchase history column to store the log for each user.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username) #Get the owned stocks from the users table.
                            cursor.execute(query)

                            stringbuilder = ""

                            for row in cursor: #Loop to get the owned stocks and add my delimiter.
                                for cell in row:
                                    cellF = str.format("{0}$",cell)
                                    stringbuilder = stringbuilder + cellF

                            self.send(stringbuilder.encode())
                             
                    except:
                        #If Username table doesn't exst.
                        query = "CREATE TABLE Usernames (Username TEXT)" #Create Username table.
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("INSERT INTO Usernames (Username) VALUES ('{0}')",username) #Add the username into the table.
                        cursor.execute(query)
                        connection.commit()

                        query = "ALTER TABLE Usernames ADD Balance DECIMAL(5,2)" #Add Balance column which is a decimal with max of 5 digits and up two decimal places.
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("CREATE TABLE {0}OwnedStocks (Symbol TEXT)",username) #Create user table.
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("INSERT INTO {0}OwnedStocks SELECT Symbol FROM Stocks",username) #Insert details from stocks table into user tables.
                        cursor.execute(query)
                        connection.commit()
                        
                        query = str.format("ALTER TABLE {0}OwnedStocks ADD OwnedStocks INTEGER",username) #Add stocks column to user table.
                        cursor.execute(query)
                        connection.commit()
                        
                        query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = 0 WHERE Symbol IS NOT NULL",username) #Set owned stocks to 0 since they won't own any at this point.
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("CREATE TABLE {0}PurchaseHistory (ID INTEGER, Description TEXT,PRIMARY KEY(ID))",username) #reate Purchase History table based on the user. 
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks ",username) #Select Stocks that the user owns.
                        cursor.execute(query)

                        stringbuilder = ""

                        for row in cursor: #Loop over stocks owned and send them with default encoding.
                            for cell in row:
                                cellF = str.format("{0}$",cell)
                                stringbuilder = stringbuilder + cellF

                        self.send(stringbuilder.encode())

                elif "GetPurchaseHistory" in data2: #If this is in data run this command
                    data3 = data2.split("$")
                    username = data3[1] #Get username from recieved data.
                    query = str.format("SELECT Description FROM {0}PurchaseHistory",username) #Select purchase history from details.
                    cursor.execute(query)

                    test = cursor.fetchone() #Fetch only one result.

                    if test == None: #Check if this result is blank.
                        self.send(("None").encode())
                    else:

                        cursor.execute(query) #Get full results.

                        stringbuilder = ""

                        for row in cursor: #For all the data loop over it and send it with default encoding.
                            for cell in row:
                                cellF = str.format("{0}$",cell)
                                stringbuilder = stringbuilder + cellF

                        self.send(stringbuilder.encode())

                elif "GetBalance" in data2: #If this is in data run this command
                    data3 = data2.split("$")
                    username = data3[1]
                    balance = data3[2].replace(',','') #Remove , from balance.
                    
                    query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username) #Select balance related to the username

                    cursor.execute(query)

                    stringbuilder = ""

                    for row in cursor.execute(query): #Get one result.
                        stringbuilder = str.format("{0}",row[0])

                    if stringbuilder == 'None': #Check to see if the user has a balance set.
           
                        query = str.format("UPDATE Usernames SET Balance = {0} WHERE Username = '{1}'",balance,username) #If balance doesn't exist set it to default value 20,000
                        cursor.execute(query)                                                                        #which comes from the gui of the client.
                        connection.commit()
                        
                        query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username) #Select the balance related to the username.
                        cursor.execute(query)

                        stringbuilder = ""

                        for row in cursor.execute(query):
                            stringbuilder = str.format("{0}",row[0])

                        self.send(stringbuilder.encode()) #Send the balance to the server. 
                    else:
                        #If balance exists then send it
                        query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username)
                        cursor.execute(query)

                        stringbuilder = ""

                        for row in cursor.execute(query):
                            stringbuilder = str.format("{0}",row[0])

                        self.send(stringbuilder.encode())

                elif "BuyStock" in data2:
                    data3 = data2.split("$")

                    symbol = data3[1] #Get symbol from data recieved.
                    username = data3[2] #Get username from data recieved.
                    price = 0
                    company = ""

                    query = str.format("SELECT Price FROM Stocks WHERE Symbol = '{0}'",symbol) #Get the price of the stock.
                    
                    for row in cursor.execute(query):
                            price = float(row[0].replace(',','')) #Convert to float so that the price is to 2 decimal places.
                    
                    query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username) #Select the users balance.
                    
                    for row in cursor.execute(query):
                        currentBalance = row[0]

                    queryResult = currentBalance - price #Minus the price of the stock from the users current balance.

                    if queryResult < 0: #If the users balance is less than zero after buying the stock send nofunds to client to show error.
                        query = str.format("UPDATE Usernames SET Balance = {0}",currentBalance) 
                        cursor.execute(query)
                        connection.commit()

                        self.send(("NoFunds").encode())
                    else:
                        #If funds do exist.
                        query = str.format("SELECT Quantity FROM Stocks WHERE Symbol = '{0}'",symbol) #Make sure the company has stocks to buy.

                        for row in cursor.execute(query):
                            queryresult2 = (row[0])

                        if (queryresult2 > 0) == True: #If the company does have stocks avaliable.
                            query = str.format("UPDATE Stocks SET Quantity = Quantity - 1 WHERE Symbol = '{0}'",symbol) #Update the stocks table to minus 1 from the selected stock.
                            cursor.execute(query)
                            connection.commit()

                            timestamp = datetime.now() #Get the time of purchase.

                            query = str.format("SELECT Price FROM Stocks WHERE Symbol = '{0}'",symbol)
                    
                            for row in cursor.execute(query):
                                price = float(row[0].replace(',','')) #Convert to 2 decimal places.
                    
                            query = str.format("SELECT Balance FROM Usernames WHERE Username = '{0}'",username) #Get the users balance.
                    
                            for row in cursor.execute(query):
                                currentBalance = row[0]

                            query = str.format("UPDATE Usernames SET Balance = Balance - {0} WHERE Username = '{1}'",price,username) #Update the users balance.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("SELECT Company FROM Stocks WHERE Symbol = '{0}'",symbol) #Select the company the user selected.
                        
                            for row in cursor.execute(query):
                                company = str.format("{0}",row[0])

                            timeTimestamp = str.format("{0}:{1}:{2}",timestamp.time().hour,timestamp.time().minute,timestamp.time().second) #Format the time so milliseconds aren't included.

                            description = str.format("Purchased 1 stock from {0} on {1} at {2} for £{3}",company,timestamp.date(),timeTimestamp,price) #Construct the log message.

                            query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = OwnedStocks + 1 WHERE Symbol = '{1}'",username,symbol) #Update the user table to add the owned stock. 
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("SELECT Description FROM {0}PurchaseHistory",username)
                            cursor.execute(query)
                            queryResult3 = cursor.fetchall()

                            if len(queryResult3) == 30: #Select purchase history check if equal to 30 and if it is run SQL queries to delete and then insert.
                                
                                query = str.format("DELETE FROM {0}PurchaseHistory WHERE Description IN (SELECT Description FROM {0}PurchaseHistory ORDER BY ID ASC LIMIT 1)",username)
                                cursor.execute(query)
                                connection.commit()
                                
                                query = str.format("INSERT INTO {0}PurchaseHistory (Description) VALUES ('{1}')",username,description) #Add log message to user tables.
                                cursor.execute(query)
                                connection.commit()

                                self.send(("Success").encode())
                            else:
                                query = str.format("INSERT INTO {0}PurchaseHistory (Description) VALUES ('{1}')",username,description) #Add log message to user tables.
                                cursor.execute(query)
                                connection.commit()

                                self.send(("Success").encode()) #Send success message to client.
                        else:
                            self.send(("NoCompanyStocksOwned").encode()) #If the company owns no stocks then send error command to client.

                elif "SellStock" in data2:
                    data3 = data2.split("$")

                    symbol = data3[1] #Get symbol from recieved data.
                    username = data3[2] #Get username from recieved data.
                    queryresult = 0
                    company = ""
                    price = 0

                    query = str.format("SELECT OwnedStocks FROM {0}OwnedStocks WHERE Symbol = '{1}'",username,symbol) #Find how many stocks of the selected company the user owns.

                    for row in cursor.execute(query):
                        queryresult = (row[0])

                    if (queryresult > 0) == True: #If the user owns stocks from the company.
                        query = str.format("UPDATE Stocks SET Quantity = Quantity + 1 WHERE Symbol = '{0}'",symbol) #If the user owns stocks from the company.
                        cursor.execute(query)
                        connection.commit()

                        timestamp = datetime.now() #Get time that the stock was sold.

                        query = str.format("SELECT Company FROM Stocks WHERE Symbol = '{0}'",symbol) #Select the company again.

                        for row in cursor.execute(query):
                            company = str.format("{0}",row[0])

                        query = str.format("SELECT Price FROM Stocks WHERE Symbol = '{0}'",symbol) #Get price of the selected stock.
                    
                        for row in cursor.execute(query):
                            price = float(row[0].replace(',',''))

                        timeTimestamp = str.format("{0}:{1}:{2}",timestamp.time().hour,timestamp.time().minute,timestamp.time().second) #Format the time so milliseconds aren't included.

                        description = str.format("Sold 1 stock from {0} on {1} at {2} for £{3}",company,timestamp.date(),timeTimestamp,price) #Structure the log message.

                        query = str.format("UPDATE {0}OwnedStocks SET OwnedStocks = OwnedStocks - 1 WHERE Symbol = '{1}'",username,symbol) #Remove a stock from the users table.
                        cursor.execute(query)
                        connection.commit()

                        query = str.format("SELECT Description FROM {0}PurchaseHistory",username)
                        cursor.execute(query)
                        queryResult4 = cursor.fetchall()

                        if len(queryResult4) == 30: #Select purchase history check if equal to 30 and if it is run SQL queries to delete and then insert.
                            query = str.format("DELETE FROM {0}PurchaseHistory WHERE Description IN (SELECT Description FROM {0}PurchaseHistory ORDER BY ID ASC LIMIT 1)",username)
                            cursor.execute(query)
                            connection.commit()
                                
                            query = str.format("INSERT INTO {0}PurchaseHistory (Description) VALUES ('{1}')",username,description) #Add log message to user tables.
                            cursor.execute(query)
                            connection.commit()

                            self.send(("Success").encode())
                        else:
                            query = str.format("INSERT INTO {0}PurchaseHistory (Description) VALUES ('{1}')",username,description) #Add the log to purchase history table.
                            cursor.execute(query)
                            connection.commit()

                            query = str.format("SELECT Price FROM Stocks WHERE Symbol = '{0}'",symbol) #Get price of stock.

                            for row in cursor.execute(query):
                                price = float(row[0].replace(',','')) #Convert to 2 decimal places.
                        
                            query = str.format("UPDATE Usernames SET Balance = Balance + {0}",price) #Update the users balance.
                            cursor.execute(query)
                            connection.commit()

                            self.send(("Success").encode()) #Send the success message to the client.
                    else:
                        self.send(("NoOwnedStocks").encode()) #If the company doesn't have any avaliable stocks send error message to client.
            except:
                print("Unexpected error:", sys.exc_info()) #For my own use in case something goes wrong.
        else:
            pass

class Server(asyncore.dispatcher):

    def __init__(self, host, port): #Create method that accepts self value and a host and port input.
        asyncore.dispatcher.__init__(self) #Create instance of dispatcher class.
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM) #Create a blank socket.
        self.set_reuse_addr() #Stop the socket from timing out.
        self.bind((host, port)) #Create variable get set for host and port types.
        self.listen(5) #Listen for a maximum of up to 5 queued connections

    def handle_accept(self): #Create method for accepting connections.
        pair = self.accept()
        if pair is not None: #If the client isnt empty set the client variable.
            sock, addr = pair
            print (str.format("Incoming connection from '{0}'",repr(addr))) #Print client ip address.
            handler = Handle_Data(sock) #Pass to the data class.
            print("listening..")

server = Server('0.0.0.0', 8000) #Create new instance of server, 0.0.0.0 means it will host on any port so both 127.0.0.1(local pc only) and 192.168.1.1 will be hosted so it can be accessed from other pcs.
print("listening..") #State that the server is listening again. 
asyncore.loop() #Call loop method of asyncore to begin listening for clients again.
