# maintains database connection
import psycopg2
import const

def connect():
	conn = psycopg2.connect(host = const.SQL_HOST,user = const.SQL_ADMIN,password = const.SQL_ADMIN_PASSWD, database=const.SQL_DATABASE)
	conn.autocommit = True
	global cursor
	cursor = conn.cursor()
	
def execute(query):
	if(not "cursor" in globals()):
		connect()
	cursor.execute(query)
	
def fetchone():
	return cursor.fetchone()