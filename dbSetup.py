# This initial setup script creates the Database and tables for the ovInfo application
# requires a db location, user and password configured in const.py
import psycopg2
import const

def connect():
	conn = psycopg2.connect(host = const.SQL_HOST,user = const.SQL_ADMIN,password = const.SQL_ADMIN_PASSWD, database=const.SQL_DATABASE)
	conn.autocommit = True
	return conn.cursor()
	
def createTable(tableName, fieldString):
	cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (tableName,))
	if cur.fetchone()[0]:
		print("Table '%s' already exists." % tableName)
	else:
		tableString = 'CREATE TABLE "%s" (%s);' % (tableName,fieldString)
		print("Creating table '%s'." % tableName)
		cur.execute('CREATE TABLE "%s" (%s);' % (tableName,fieldString))
	
cur = connect()
createTable('messages_sent','messageID VARCHAR(256) PRIMARY KEY, sendDate date')