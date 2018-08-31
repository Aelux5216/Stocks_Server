# Stocks Server

<p align="center">
<img src="https://img.shields.io/badge/python-3.6-blue.svg" style="max-height: 300px;"></a>
</p>

## About

This server allows multiple clients to buy/sell theoretic stocks using a SQLite db file.

## Features

* Buy and sell stock from a database
* Supports multiple clients
* Stores user details and order history.

## Possible to do list 

* Swap SQLite file for a dedicated database server
* Add feedback for when the database file can't be located/reached
* Add more feedback to the console incuding showing the current ips
 
## How to use

**Note: This program can only be used with the matching clients using the host computers main ip address**

* Start server
* Check what the main ip is using command prompt
* Connect clients and proccess stocks
* If you want to edit the database manually then use SQL to open the .db file

## Installation

Download/Clone the repo and grab the stocks_server folder, as long as you have all of the files within this folder 
double click the the .py to run the program. 

## Issues

If you come across any issues while using this program or have any suggestions, feel free to create an 
issue with as much information as you can.

## Dependencies

* Python 3.6 64 bit installed
* Python pre-installed modules - [socket, sys and datetime](https://www.mozilla.org/en-US/MPL/2.0/)
* Python extra module - [asyncore](https://github.com/somdoron/AsyncIO)
* The matching stock client on this [github](https://github.com/Jstanford5216/Stocks_Client)

## License

This project is available under the MIT license. See the LICENSE file for more info.

