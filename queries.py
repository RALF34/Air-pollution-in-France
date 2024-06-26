import pandas as pd
import streamlit as st

OVERSEAS_DEPARTMENTS = [
    "GUADELOUPE",
    "GUYANE",
    "MARTINIQUE",
    "LA REUNION",
    "MAYOTTE",
    "SAINT-MARTIN"]

@st.cache_resource
def load_data():
    locations = pd.read_csv("data/location_data.csv")
    regions = locations[
        ["region","department"]].groupby("region")
    departments = locations[
        ["department","city"]].groupby("department")
    cities = locations[
        ["city","station","coordinates"]].groupby("city")

    data = pd.read_csv("data/pollution_data.csv")
    columns = data.columns[:-1]
    working_days = data[data["working day"]][columns]
    weekends = data[data["working day"]==False][columns]
    distribution_pollutants = working_days[
        ["station","pollutant"]].groupby("station")
    distribution_cities = working_days[
        ["pollutant","station"]].groupby("pollutant")
    columns = ["station","pollutant"]
    working_days = working_days.groupby(columns)
    weekends = weekends.groupby(columns)
    return {
        "regions": regions,
        "departments": departments,
        "cities": cities,
        "distribution_pollutants": distribution_pollutants,
        "distribution_cities": distribution_cities,
        "working_days": working_days,
        "weekends": weekends}

def get_data(s, p):
    '''
    Return the pandas dataframes (or None when not enough data)
    containing hourly average air concentrations of pollutant "p" 
    recorded by station "s" on both working_days and weekends.
    '''
    dictionary = load_data()
    x, y  = dictionary["working_days"], dictionary["weekends"]
    result = []
    for data in [x, y]:
        try:
            result.append(data.get_group((s,p)))
        except:
            result.append(None)
    return result

def get_items(where, group):
    '''
    Extract the data from the appropriate pandas GroupBy object 
    which are associated to group "group_name".

    Arguments:
    where -- name of the pandas GroupBy object where we want to 
             retrieve the data from.
    group -- name of the group whose data we want to extract.
    '''

    dictionary = load_data()
    data = dictionary[where]
    if where == "regions" and not(group):
        items = list(data.groups.keys())
        for e in OVERSEAS_DEPARTMENTS:
            items.remove(e)
        items.append("OUTRE-MER")
    else:
        if group == "OUTRE-MER":
            items = OVERSEAS_DEPARTMENTS
        else:
            data = data.get_group(group)
            if where == "cities":
                items = list(zip(
                    data["station"].to_list(),
                    data["coordinates"].to_list()))
            else:
                items = data.to_list()
                if where == "distribution_pollutants":
                    items = [e+" pollution" for e in items]
    return items
