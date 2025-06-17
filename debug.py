import os
import sys
import traceback

# For local debugging
try:
    # Print environment information
    print("Python version:", sys.version)
    print("Current directory:", os.getcwd())
    print("Static folder exists:", os.path.exists('static'))
    print("Templates folder exists:", os.path.exists('templates'))

    # Import the app
    from app import app
    print("App imported successfully")
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    
    # Test database connection
    from app import db
    with app.app_context():
        try:
            db.engine.connect()
            print("Database connection successful")
            print("Tables in the database:", db.engine.table_names())
        except Exception as e:
            print("Database connection failed:", str(e))
            traceback.print_exc()
    
    if __name__ == '__main__':
        # Run the application
        app.run(host='0.0.0.0', port=5000, debug=True)

except Exception as e:
    print("Error in debug.py:", str(e))
    traceback.print_exc()
