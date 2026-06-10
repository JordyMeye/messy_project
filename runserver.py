"""
Flask Application Server
Runs the Flask application with database controller integration.
"""

import os
from FlaskWebProject1 import app

if __name__ == '__main__':
    # Run Flask on 0.0.0.0:8080 (accessible from outside container)
    app.run(host='0.0.0.0', port=8080, debug=False)