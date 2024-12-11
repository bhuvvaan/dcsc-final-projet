import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



# Connect to the default database
conn = psycopg2.connect(
    host="localhost",   # or the IP of your service if not using port-forwarding
    port=5432,
    user="postgres",
    password="my-password",  # Replace with your password
    database="postgres"  # Default database in PostgreSQL
)


# Set the isolation level to AUTOCOMMIT
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor object
cur = conn.cursor()


create_table_query = '''
CREATE TABLE IF NOT EXISTS video_details (
    video_id SERIAL PRIMARY KEY,
    video_link_minio TEXT NOT NULL,
    ppt_link TEXT
);
'''

cur.execute(create_table_query)
print("Table 'video_details' created successfully!")



# Close the cursor and connection
cur.close()
conn.close()
