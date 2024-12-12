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
CREATE TABLE IF NOT EXISTS video_details_temp (
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




# '''
# import psycopg2

# # Connect to the exampledb_1 database
# conn = psycopg2.connect(
#     host="localhost",   # or the IP of your service if not using port-forwarding
#     port=5432,
#     user="postgres",
#     password="your_password",  # Replace with your password
#     database="exampledb_1"  # The database where the table is created
# )

# # Create a cursor object
# cur = conn.cursor()

# # Define the INSERT query
# insert_query = '''
# INSERT INTO video_details (video_link_minio, ppt_link) 
# VALUES (%s, %s);
# '''

# # Data to insert into the table
# data_to_insert = [
#     ('https://minio.example.com/video1.mp4', 'https://example.com/ppt1.pptx'),
#     ('https://minio.example.com/video2.mp4', 'https://example.com/ppt2.pptx'),
#     ('https://minio.example.com/video3.mp4', 'https://example.com/ppt3.pptx')
# ]

# # Insert data into the table
# for data in data_to_insert:
#     cur.execute(insert_query, data)

# print("Rows inserted successfully!")

# # Commit the transaction
# conn.commit()

# # Close the cursor and connection
# cur.close()
# conn.close()

# '''