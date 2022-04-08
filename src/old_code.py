# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:58:13 2022

@author: Jaime García Chaparr
"""

# =============================================================================
# 
# 
# acts_id = actor['actor_id'].tolist()
# 
# # Create list of tuples matching one film to one actor
# film_actor_tuples = []
# for film_id in film['film_id']:
#     n_actors = random.randint(3, 10) # Select random number of actors
#     film_actors = random.sample(acts_id, n_actors) # Select random actors for each film
#     for actor_id in film_actors:
#         film_actor_tuples.append((film_id, actor_id))
# 
# # Create connection dataframe to manage many-to-many connection
# film_actor = pd.DataFrame({'film_id' : [el[0] for el in film_actor_tuples],
#                         'actor_id' : [el[1] for el in film_actor_tuples]})
# 
# # Add to table lists
# df_lst.append(film_actor)
# df_name_lst.append('film_actor')
# 
# =============================================================================

