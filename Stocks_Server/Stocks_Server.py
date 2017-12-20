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
query = str.format("INSERT INTO DATABASE (SYMBOL, COMPANY, PRICE, QUANTITY) VALUES ('{0}', '{1}', '{2}', '{3}')", testsym,testcomp,testprice,testquant) #How to run a sql command
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

                elif "Buy" in data2:
                    data3 = data2.split("$")
                    query = str.format("UPDATE Stocks SET Quantity = Quantity -1 WHERE Symbol = '{0}'",data3[1])
                    try:
                        cursor.execute(query)
                        connection.commit()
                        self.send(("Success").encode())
                    except:
                        self.send(("Fail").encode())
                elif "Sell" in data2:
                    data3 = data2.split("$")
                    query = str.format("UPDATE Stocks SET Quantity = Quantity +1 WHERE Symbol = '{0}'",data3[1])
                    try:
                        cursor.execute(query)
                        connection.commit()
                        self.send(("Success").encode())
                    except:
                        self.send(("Fail").encode())
            except:
                print("Unexpected error:", sys.exc_info()[0])
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
            print (str.format("Incoming connection from {0}",repr(addr)))
            handler = Handle_Data(sock)

server = Server('0.0.0.0', 8000)
asyncore.loop()
