# Models sent messages database interface
import dbConnection
	
def addNewMessage(messageID):
	dbConnection.execute("INSERT INTO messages_sent(messageID, sendDate) VALUES ('%s', NOW())" % messageID)
	
def messageExists(messageID):
	if messageID == "":
		return False
	dbQuery = "SELECT * FROM messages_sent WHERE messageID = '%s'" % messageID
	dbConnection.execute(dbQuery)
	return dbConnection.fetchone() is not None
