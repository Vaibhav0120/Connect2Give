# This file tells Django to use PyMySQL instead of the default mysqlclient.
# This is the key to making the project work without needing C++ build tools.

import pymysql

# Tell Django to pretend that PyMySQL is the original MySQLdb driver
pymysql.install_as_MySQLdb()