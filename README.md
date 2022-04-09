# W3 Project - Building MySQL Database 

The goal of this project is to build our own database from several .csv files about films and a film rental service.

## Steps taken

1. Import the .csv as Pandas dataframes.
1. Inspect the dataframes to have a rough idea of the information availible.
1. Sketch the relationships between tables. The `actor` and `film` tables have a many-to-many relationship and no intermediate table is provided. The category column is, at first glance, disconnected from the rest. Other tables have direct connections.
1. Clean data: details provided below.
1. Create a brand new table, `original_lang`.
1. Save processed tables to .csv.
1. Connect to SQL Server and create a new database.
1. Export Pandas dataframes to SQL.
1. Configure primary keys and connections.
1. Execute queries.

## Final schema

![final_schema](https://i0.wp.com/itsoftware.com.co/content/wp-content/uploads/2018/03/que-es-y-para-que-sirve-mysql-1.jpg)

## About the cleaning process

- Several columns were dropped, particularly the `last_update` column present in all tables. 
- The category 0 as 'Unclassified' in the `category` table was added.
- The column `category_id` was added to `films` to ensure the connection between tables.
- A new table managing the many-to-many relationship between `film` and `actor` was created based on data from the `old_hdd` table.
- A new table called `original_lang` was created and populated with several random languages.

### Technology Stack

In this project the following libraries were used:

 - [Pandas](https://pandas.pydata.org/docs/)

 - [Numpy](https://numpy.org/doc/stable/) 

 - [PyMySQL](https://github.com/PyMySQL/PyMySQL) 

 - [SQLAlchemy](https://www.sqlalchemy.org/)

 - my own [support functions](https://github.com/jgchaparro/w4-database-project/blob/main/src/functions.py).