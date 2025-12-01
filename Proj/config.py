import secrets
import psycopg2

def get_connection():
    return psycopg2.connect(database="HIC project", user="postgres",
                        password="Molosky404", host="localhost", port="5432")
# !!ADD THIS FILE TO GIT IGNORE ONCE WE START USING DATABASE!!

#This is where well do database connections
