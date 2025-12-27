from db_connector import ERPDatabase

db = ERPDatabase()

if db.test_connection():
    print("Connected to Azure SQL!")
else:
    print("Heyy! not possible to connect!")