# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 09:16:16 2022

@author: Jaime García Chaparr
"""
#%% Import modules

import pandas as pd
import numpy as np

import mysql.connector as conn
import pymysql
from sqlalchemy import create_engine

import random
from functions import find_category, find_actor_id, find_film_id, pass_

#%% Load data

actor = pd.read_csv('../data/actor.csv')
category = pd.read_csv('../data/category.csv')
film = pd.read_csv('../data/film.csv')
inventory = pd.read_csv('../data/inventory.csv')
language = pd.read_csv('../data/language.csv')
rental = pd.read_csv('../data/rental.csv')
old_hdd = pd.read_csv('../data/old_HDD.csv')

# Group all df in one list
df_lst = [actor, category, film, inventory, language, rental]
df_name_lst = ['actor', 'category', 'film', 'inventory', 'language', 'rental']

#%% Drop unneeded columns

actor = actor.drop(columns = ['last_update'])
category = category.drop(columns = ['last_update'])
film = film.drop(columns = ['description', 'release_year', # All films were released in 2006
                            'original_language_id', 'rating', 
                            'special_features', 'last_update']) 
inventory = inventory.drop(columns = ['last_update'])
language = language.drop(columns = ['last_update'])
rental = rental.drop(columns = ['last_update'])

#%% Add key 0 for unclassified films

category.loc[len(category)] = [0, 'Unclassified']
category.sort_values(by = 'category_id', inplace = True)

#%% Adjust `rental.inventory_id`: it does not match with `inventory` PK

valid_inv_id = inventory['inventory_id']

# Use a random number from inventory_id
rental['inventory_id'] = [random.choice(valid_inv_id) for _ in range(len(rental))]

#%% Create connection column for `category` and `film_id`: one-to-many connection

films_unique = film.title.unique()
film['category_id'] = [find_category(f, old_hdd) for f in films_unique]

#%% Create connection table for `actor` and `film`: many-to-many connection

# Create full name column
actor['full_name'] = actor['first_name'] + ' ' + actor['last_name']
old_hdd['full_name'] = old_hdd['first_name'] + ' ' + old_hdd['last_name']

# Create columns for connection table
old_hdd['actor_id'] = [find_actor_id(a, actor) for a in old_hdd.full_name]
old_hdd['film_id'] = [find_film_id(f, film) for f in old_hdd.title]
old_hdd['index' ] = [i for i in range(len(old_hdd))]

# Create final df
film_actor = old_hdd[['index', 'film_id', 'actor_id']]


#%% Save to clean .csv

# Refresh objects
df_lst = [actor, category, film, inventory, language, rental, film_actor]
df_name_lst = ['actor', 'category', 'film', 'inventory', 'language', 'rental', 'film_actor']

suffix = '_cl'

for df, df_name in zip(df_lst, df_name_lst):
    df.to_csv(f'../data/cleaned_csv/{df_name}{suffix}.csv')


#%% Create connection string

mysql_str_conn = f'mysql+pymysql://jgchaparro:{pass_}@127.0.0.1:3306/'
mysql_motor = create_engine(mysql_str_conn)


#%% Reinitialize DB

try:
    mysql_motor.execute('DROP DATABASE sql_proyect;')
except:
    pass
mysql_motor.execute('CREATE DATABASE sql_proyect;')

str_conn = f'mysql+pymysql://jgchaparro:{pass_}!@127.0.0.1:3306/sql_proyect'
motor = create_engine(str_conn)

#%% Add tables to SQL

for df, df_name in zip(df_lst, df_name_lst):
    df.to_sql(name = df_name, con = motor,
              if_exists = 'replace', index = False)

#%% Set primary keys

pks = {
       'actor' : 'actor_id',
       'film_actor' : 'index',
       'film' : 'film_id',
       'category' : 'category_id',
       'inventory' : 'inventory_id',
       'rental' : 'rental_id',
       'language' : 'language_id'
       }

for k, v in pks.items():
    try:
        motor.execute(f'ALTER TABLE {k} ADD PRIMARY KEY (`{v}`);')
    except:
        continue
    
#%% Add conections

conns = [
        {'ALTER' : 'film_actor', # Where it is not PK
         'CONSTRAINT' : 'fk_actor_id',
         'FOREIGN' : 'actor_id', # Column with same name
         'REFERENCES' : 'actor'}, # The other table
        
        {'ALTER' : 'film_actor',
         'CONSTRAINT' : 'fk_film_id',
         'FOREIGN' : 'film_id',
         'REFERENCES' : 'film'},
        
        {'ALTER' : 'film',
         'CONSTRAINT' : 'fk_film_id2',
         'FOREIGN' : 'language_id',
         'REFERENCES' : 'language'},

        {'ALTER' : 'film',
         'CONSTRAINT' : 'fk_category_id',
         'FOREIGN' : 'category_id',
         'REFERENCES' : 'category'},

        {'ALTER' : 'inventory',
         'CONSTRAINT' : 'fk_film_id_2',
         'FOREIGN' : 'film_id',
         'REFERENCES' : 'film'},
        
        {'ALTER' : 'rental',
         'CONSTRAINT' : 'fk_inventory_id',
         'FOREIGN' : 'inventory_id',
         'REFERENCES' : 'inventory'}
        ]

# =============================================================================
# f"""ALTER TABLE {c['ALTER']} 
#               ADD CONSTRAINT `fk_{c['FOREIGN']}`
#               FOREIGN KEY ({c['FOREIGN']})
#               REFERENCES {c['REFERENCES']}({c['FOREIGN']});
#               """
# 
# =============================================================================

for c in conns:
    try:
        query = f"ALTER TABLE {c['ALTER']} ADD CONSTRAINT `{c['CONSTRAINT']}` FOREIGN KEY ({c['FOREIGN']}) REFERENCES {c['REFERENCES']}({c['FOREIGN']});"
        motor.execute(query)
    except Exception as e:
        print(e)
        print(' ')
        continue
    
#%% Query 1 - Which author has appeared in the most films?

q = """SELECT full_name, count(film_id) AS films \
FROM actor AS a \
LEFT JOIN film_actor as fa \
ON a.actor_id = fa.actor_id \

GROUP BY full_name \
ORDER BY films desc;"""

res1 = list(motor.execute(q))[0]


#%% Query 2 - Which is the film with the most actors?

q = """SELECT f.title, count(fa.actor_id) AS n_actors \
FROM film AS f \
LEFT JOIN film_actor as fa \
ON f.film_id = fa.film_id \
LEFT JOIN actor as a \
on fa.actor_id = a.actor_id \

GROUP BY f.film_id \
ORDER BY n_actors desc;"""

res2 = list(motor.execute(q))[0]

#%% Query 3 - In which films does Uma Wood appear?

q = """SELECT title \
FROM actor as a \
LEFT JOIN film_actor as fa \
ON a.actor_id = fa.actor_id \
LEFT JOIN film as f \
ON fa.film_id = f.film_id \
WHERE full_name = 'UMA WOOD';"""

res3 = list(motor.execute(q))

#%% Query 4 - Which is the most expensive film to replace?

q = """SELECT title, replacement_cost \
FROM film \
ORDER BY replacement_cost DESC;"""

res4 = list(motor.execute(q))[0]

#%% Query 5 - Which is the most popular genre?

q = """SELECT c.name, count(f.title) as tot \
FROM film AS f \
LEFT JOIN category AS c \
ON f.category_id = c.category_id  \
GROUP BY c.category_id \
ORDER BY tot desc;"""

res5 = list(motor.execute(q))[1]

#%% Query 6 - Which is the most common film in the inventory?

q = """SELECT f.title, count(i.inventory_id) as tot \
FROM inventory as i \
LEFT JOIN film as f \
ON i.film_id = f.film_id \
GROUP BY i.film_id \
ORDER BY tot desc;"""

res6 = list(motor.execute(q))[0]

#%% Query 7 - Which employee has sold the most?

q = """SELECT staff_id, count(rental_id) AS tot \
FROM rental \
GROUP BY staff_id \
ORDER BY tot DESC;"""

res7 = list(motor.execute(q))[0]

#%% Query 8 - Which is the longest film?

q = """SELECT title, length \
FROM film AS f \
ORDER BY length DESC \
LIMIT 1;"""

res8 = list(motor.execute(q))

#%% Query 9 - Which costumer rents the most?

q = """SELECT customer_id, count(inventory_id) AS tot \
FROM rental AS r \
GROUP BY customer_id \
ORDER BY tot DESC \
LIMIT 1;"""

res9 = list(motor.execute(q))

#%% Query 10 - Which film has the highest rental rate

q = """SELECT title, rental_rate \
FROM film AS f \
ORDER BY rental_rate DESC \
LIMIT 1;"""

res10 = list(motor.execute(q))