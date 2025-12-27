import pyodbc
import os
from typing import List, Dict

class ERPDatabase:
    def __init__(self):
        self.connection_string = os.getenv(
           "AZURE_SQL_CONNECTION_STRING"
        )
        if not self.connection_string:
            raise ValueError("AZURE_SQL_CONNECTION_STRING not set")

    def get_connection(self):
        """Create and return a database connection"""
        return pyodbc.connect(self.connection_string)

    def execute_query(self, query: str) -> List[Dict]:
        """
        Execute a SELECT query and return result as list of dicts
        """
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        conn.close()

        return results

    def test_connection(self) -> bool:
        """Simple test to check DB connectivity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print("DB connection failed:", e)
            return False
