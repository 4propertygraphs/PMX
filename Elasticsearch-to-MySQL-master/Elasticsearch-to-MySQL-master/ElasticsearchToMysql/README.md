# Elasticsearch to mysql database #
This repository retrieves data from elasticsearch to then put it in a mysql database. So it can be used to generate a pmx report.

## How to configure the project ##
### Mysql DataBase ###
You first need to make sure you have a mysql database setup.
This project uses xampp to run the mysql database but you can use anything as long as you can run a mysql database.

once you have done that you need to update the DATABASE_URI in the settings.py.
The structure should be:

    "mysql+pymsql://{username of your database}@{server address}{port number}/{database name}"

### Python Project Setup ###
To install all the dependancies:

    python -m pip install -r requirements.txt

after that you have a virtual env running and it should work after you run main.py

## some quick notes ##
This program can be very slow.
If you want to make it run quickly change the setting:

    REMOVE_ROGUE_DATA = True
and set it to False
This will make the code run faster, and this can be nice for testing but the output is going to have a lot of rogue data that should not be there.