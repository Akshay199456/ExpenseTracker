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
-- 	10 -> send request to send to the person
-- 	20 -> send request to receive from the person
-- 	30 -> receive request to send to the person
-- 	40 -> receive request to receive from the person

-- Continuing the request_type

--  50 -> completed accepted request to send money -> request made by the current_user
--  51 -> completed accepted request to send money -> request made by the other_user
--  60 -> completed accepted request to receive money -> request made by the current_user
--  61 -> completed accepted request to receive money -> request made by the other_user

--  70 -> completed rejected request to send money to the person -> request made by the current_user
--  71 -> completed rejected request to send money -> request made by the other_user
--  80 -> completed rejected request to receive money -> request made by the current_user
--  81 -> completed rejected request to receive money -> request made by the other_user
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

