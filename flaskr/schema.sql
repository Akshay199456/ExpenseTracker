-- In SQLite, data is stored in tables and columns. These need to be created before 
-- you can store and retrieve data. Flaskr will store users in the user table, 
-- and posts in the post table. Create a file with the SQL commands needed to create 
-- empty tables:

DROP TABLE IF EXISTS user;

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);