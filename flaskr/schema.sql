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
	password TEXT NOT NULL,
	budget INTEGER DEFAULT 0
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

-- friendrequest table

-- --
-- id - > id of the row stored in the database
-- user_id -> id of the user who is making the request
-- friend_id -> id of the user whom you have accepted as a friend, sent request, received request from
-- friend_type_request -> type of friend request
-- --

-- -- 
-- For friend_type_request, currently can take up 3 possible values
-- 0 and 1. 
-- 	0 -> friend request has been sent
-- 	1 -> friend request has been received
--  2 -> friend request has been accepted and is a friend
-- --

CREATE TABLE friendrequest (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	friend_id INTEGER NOT NULL,
	friend_type_request INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES user(id),
	FOREIGN KEY(friend_id) REFERENCES user(id)
)



-- transaction table

-- --
-- id -> id of the transaction
-- user_id -> id of the user making the request
-- friend_id -> id of the user to whom the request is being sent top-level
-- request_type -> the type of request made by the user
-- amount -> amount that's being requested
-- --


-- --
-- For request_type, there are 4 possible values:
-- 	1 -> send request to send to the person
-- 	2 -> send request to receive from the person
-- 	3 -> receive request to send to the person
-- 	4 -> receive request to receive from the person

--  The above requests will also have an edit and non-edited suffix added to them
--  	0 -> not edited
-- 		1 -> edited

-- Continuing the request_type

--  5 -> completed accepted request to send money
--  6 -> completed accepted request to receive money 
--  7 -> completed rejected request to send money
--  8 -> completed rejected request to receive money
-- --

CREATE TABLE transactionrequest (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	friend_id INTEGER NOT NULL,
	request_type INTEGER NOT NULL,
	amount INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES user(id),
	FOREIGN KEY(friend_id) REFERENCES user(id)
)

