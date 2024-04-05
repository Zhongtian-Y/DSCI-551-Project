DROP TABLE IF EXISTS users;
CREATE TABLE users(id int, username varchar(20), hashed_password varchar(255), type varchar(20));
SELECT * FROM usercrud.users;