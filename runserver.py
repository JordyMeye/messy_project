"""
Database Controller & Web Server
Handles all database connections, operations, and HTTP routing requests.
"""

import os
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Dict, Any

# Ensure external dependencies are cleanly resolved or handled gracefully
try:
    import mysql.connector
except ImportError:
    mysql.connector = None


class DatabaseController:
    """Controller class to manage database connections and queries"""
    
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
        if not mysql.connector:
            return {
                "status": "error",
                "message": "mysql-connector-python package missing from container environment"
            }
            
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
        Execute a custom query on the database
        
        Args:
            query: SQL query to execute
            
        Returns:
            Dictionary with status and results or error message
        """
        if not mysql.connector:
            return {
                "status": "error",
                "message": "mysql-connector-python package missing from container environment"
            }

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


class TimeServiceHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler mapping application route responses"""

    def do_GET(self):
        if self.path == '/time':
            current_filename = os.path.basename(__file__)
            
            # Instantiate the database controller mapping to the Docker Compose service DNS
            db = DatabaseController(host="mysql-db", user="root", password="admin")
            db_response = db.get_current_timestamp()
            
            if db_response["status"] == "success":
                db_time = db_response["mysql_time"]
            else:
                db_time = f"Error connecting to DB: {db_response['message']}"

            # Formulate the structural response containing the requested string keys
            response_data = {
                "status": "success",
                "message": f"look my time is : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "mysql_time": db_time,
                "source_file": current_filename
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run(server_class=HTTPServer, handler_class=TimeServiceHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting application server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()