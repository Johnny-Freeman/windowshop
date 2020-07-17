from src_vault_connect import wrapper_psql_rev4_3 as psql
from config.psql_config import CONFIG_PSQL_VAULTKEEPER_TEST
DEFAULT_CONFIG = CONFIG_PSQL_VAULTKEEPER_TEST

class DB_Functions(): #this has blocking coded in with self.psql_connection.wait(), this is for single use cases!
	# General
	def __init__(self, db_config = DEFAULT_CONFIG):
		self.db_config = db_config
		
	def try_query(self, query):
		# trys submitting query (one shot use)
		# handles emergency disconnect if needed
		self.psql_connection = psql.PSQL_NON_BLOCK_Connection(self.db_config)
		try:
			self.psql_connection.QUERY_DB(query)
			self.psql_connection.wait()
			print(self.psql_connection.GET_response())
		except Exception as err:
			self.psql_connection.DISCONNECT()
			# bughammer.error(err)
			raise err
		self.psql_connection.DISCONNECT()
		
	def create_schema(self, schema_name):
		sql_query = """CREATE SCHEMA IF NOT EXISTS """ + schema_name
		return self.try_query(sql_query)
		
	def drop_schema(self, schema_name, cascade = False):
		sql_query = """DROP SCHEMA """ + schema_name
		if cascade:
			sql_query += """ CASCADE"""
		return self.try_query(sql_query)
		
	def create_table(self, custom_query):
		# so many variables, made custom
		return self.try_query(custom_query)
		
	def drop_table(self, table_name, schema_name=None, cascade=False):
		full_table_name = table_name
		if not '.' in table_name:
			if schema_name == None:
				raise ValueError("optional_param: 'schema_name' or 'schema_name.table_name' must be provided in params")
			else:
				full_table_name = schema_name + '.' + table_name
		
		sql_query = """DROP TABLE """ + full_table_name
		if cascade:
			sql_query += """ CASCADE"""
		return self.try_query(sql_query)
		
if __name__ == "__main__":
	db = DB_Functions()
	#db.create_schema('clock')
	#db.drop_schema('clock')
	
	
	db.drop_schema("day_0", cascade=True)
	
	
	
	
	
	
	pass