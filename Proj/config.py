import secrets
import psycopg2

def get_connection():
    return psycopg2.connect(database="HIC_db2", user="postgres",
                        password="359846Cb", host="localhost")
# !!ADD THIS FILE TO GIT IGNORE ONCE WE START USING DATABASE!!

#This is where well do database connections
