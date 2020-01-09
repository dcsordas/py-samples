#!/bin/bash

sqlite3 -header -csv data/database.sqlite3 "SELECT name, username, email FROM user_data;" > data/user_data.csv
echo 'OK'
