-- In SQLite, data is stored in tables and columns. These need to be created before 
-- you can store and retrieve data. Flaskr will store users in the user table, 
-- and posts in the post table. Create a file with the SQL commands needed to create 
-- empty tables:

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS expense;

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);

CREATE TABLE category (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	type TEXT NOT NULL,
	FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE expense (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	category_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	value INTEGER NOT NULL,
	FOREIGN KEY(category_id) REFERENCES category(id),
	FOREIGN KEY(user_id) REFERENCES user(id)
);