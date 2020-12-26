DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL);

DROP TABLE IF EXISTS resources;
CREATE TABLE resources (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  type TEXT NOT NULL);;

DROP TABLE IF EXISTS users_resources;
CREATE TABLE users_resources (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  resource_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (resource_id) REFERENCES resources (id),
  UNIQUE (user_id, resource_id));
