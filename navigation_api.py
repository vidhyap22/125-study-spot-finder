import requests
import sqlite3


def get_building_coords(building_id, connection):
    #access database to fetch latitude, longitude of a building id using sqlite3 connection
    cursor = connection.execute("SELECT longitude, latitude FROM buildings WHERE building_id = ?;", (building_id,))
    longitude, latitude = cursor.fetchone()
    cursor.close()
    return latitude, longitude # This might seem like backwards order but the api requires this order this is easier

def build_url(map_api_key, start_lon, start_lat, dest_lon, dest_lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking?"
    url += "api_key=" + map_api_key
    url += '&'
    url += 'start=' + str(start_lat) + ',' + str(start_lon)
    url += '&'
    url += 'end='+ str(dest_lat) + ',' +  str(dest_lon)
    return url

def get_data(url):
    response = requests.get(url)
    data = response.json()
    print(data)
    return data

if __name__ == "__main__":
    #example code
    connection = sqlite3.connect('data/database/app.db')
    start = get_building_coords("ICS", connection)
    dest = get_building_coords("LLIB", connection)
    url = build_url(api_key, *start, 33.647176,-117.841159) 
    print(url)
    data = get_data(url)

#things to add:
#check that starting coordinates are within the bounds of UCI (find min and max long and lat)
#parse returned data
#replace building coordinates in database with ones that are more friendly for this API (the Langson coordinates
#take you to the side entrance instead of the main one because those coordinates are on the side) while the ones
#from openrouteservice take you to the main entrance all the time so actually there is a tradeoff here, but I think
#most people just always take the main entrance anayways?