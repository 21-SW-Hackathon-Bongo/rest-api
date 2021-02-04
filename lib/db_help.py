import pymysql

db_config = {
	'host' : '127.0.0.1',
	'port' : 3306,
	'user' : 'root',
	'password' : '',
	'database' : 'bongo',
	'charset' : 'utf8'
}

class dbHelper:
	def __init__(self):
		self.conn = pymysql.connect(host=db_config['host'],
									port=db_config['port'],
									user=db_config['user'],
									password=db_config['password'],
									db=db_config['database'],
									charset=db_config['charset'])
		self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

	def sample(self):
		sql = "SELECT * FROM test"
		self.cursor.execute(sql)
		result = self.cursor.fetchall()

		return result
