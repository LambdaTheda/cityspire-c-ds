from fastapi import APIRouter, HTTPException
#from database import fetch_query
from app import database, ml, viz,city

import pandas as pd

# Router

router = APIRouter()


@router.get('/city_information/{city}_{statecode}')
async def city_information(city: str, statecode: str):
    """
    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`
    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.
    ## Response
    JSON string of city information stats for more than 500
    U.S. cities.
    """

    query = """
    SELECT 
        City,   
        State,
        Population
    FROM cityspire
    """

    columns = [
        "City",
        "State",
        "Population"]

    df = pd.read_json(fetch_query(query, columns))

    # Input sanitization
    City = City.title()
    statecode = statecode.lower().upper()

    # Handle Edge Cases:
    # saint
    if City[0:5] == "Saint":
        City = City.replace("Saint", "St.")

    elif City[0:3] == "St ":
        City = City.replace("St", "St.")

    # fort
    elif city[0:3] == "Ft ":
        City = City.replace("Ft", "Fort")

    elif City[0:3] == "Ft.":
        City = City.replace("Ft.", "Fort")

    # multiple caps
    elif City[0:2] == 'Mc':
        City = City[:2] + City[2:].capitalize()

    # Find matching metro-area in database
    match = df.loc[(df.City.str.startswith(city)) &
                   (df.State.str.contains(statecode))].head(1)

    # Raise HTTPException for unknown inputs
    if len(match) < 1:
        raise HTTPException(
            status_code=404,
            detail=f'{city}, {statecode} not found!')

    # DF to dictionary
    pairs = match.to_json(orient='records')

    return pairs
