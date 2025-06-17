# Migration script for MySQL database
# Run this locally in your VS Code environment
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure MySQL connection
config = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DATABASE', 'research_platform'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

try:
    # Connect to MySQL
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Add funding related columns to document table
    print('Adding funding-related columns to document table...')
    cursor.execute('ALTER TABLE document ADD COLUMN IF NOT EXISTS is_funding_enabled BOOLEAN DEFAULT false;')
    cursor.execute('ALTER TABLE document ADD COLUMN IF NOT EXISTS funding_goal FLOAT;')
    
    # Add stripe_session_id column to funding table if it exists
    print('Adding stripe_session_id column to funding table if it exists...')
    cursor.execute('''
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = %s AND table_name = 'funding';
    ''', (config['database'],))
    
    if cursor.fetchone()[0] > 0:
        cursor.execute('ALTER TABLE funding ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255);')
    
    # Commit changes
    conn.commit()
    print('Migration completed successfully')
    
except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection closed")
