import requests

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


url = build_url("eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjgwYTA3ZjIyOWJhMzQ4ODU4MDJkM2NkNmFkNmNjNTIzIiwiaCI6Im11cm11cjY0In0=", 33.644697379161755, -117.8423970937729, 33.64750186874794, -117.84176945686342)
print(url)
data = get_data(url)