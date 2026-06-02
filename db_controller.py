"""
Database Controller
Handles all database connections and operations
"""

import mysql.connector
from typing import Optional, Dict, Any


class DatabaseController:
    """Controller class to manage database connections and queries"""
    
    # UPDATED: Changed default host from "172.17.0.2" to "mysql-db"
    def __init__(self, host: str = "mysql-db", user: str = "root", password: str = "admin"):
        """
        Initialize the database controller with connection parameters
        
        Args:
            host: Database host IP/address
            user: Database user
            password: Database password
        """
        self.host = host
        self.user = user
        self.password = password
    
    def get_current_timestamp(self) -> Optional[Dict[str, Any]]:
        """
        Query the database for the current timestamp
        
        Returns:
            Dictionary with status and timestamp or error message
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT CURRENT_TIMESTAMP();")
            result = cursor.fetchone()
            
            db_time = str(result[0])
            
            cursor.close()
            connection.close()
            
            return {
                "status": "success",
                "mysql_time": db_time
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a custom query  on the database
        
        Args:
            query: SQL query to execute
            
        Returns:
            Dictionary with status and results or error message
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                "status": "success",
                "results": [str(row) for row in result]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }