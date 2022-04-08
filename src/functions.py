# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:51:30 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np

def find_category(title, df):
    """Finds the category of the provided film title."""
    try:
        return df[df.title == title]['category_id'].iloc[0]
    except:
        return 0

def find_actor_id(full_name, df):
    """Finds the author ID given the full name."""
    try:
        return df[df.full_name == full_name]['actor_id'].iloc[0]
    except:
        return np.nan
    
def find_film_id(title, df):
    """Finds the film ID based on the title given."""
    try:
        return df[df.title == title]['film_id'].iloc[0]
    except:
        return np.nan
