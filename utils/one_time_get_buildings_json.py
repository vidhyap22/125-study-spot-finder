import sqlite3
import json

conn = sqlite3.connect("data/database/app.db")
cursor = conn.cursor()

#cursor.execute(""" UPDATE buildings SET latitude = ?, longitude = ? WHERE building_id = ?;""", (33.622124164117686, -117.87765800955238, "BOAT"))
#cursor.execute(""" UPDATE buildings SET latitude = ?, longitude = ? WHERE building_id = ?;""", (33.64631931956648, -117.84479913056312, "SH"))
#cursor.execute(""" UPDATE buildings SET latitude = ?, longitude = ? WHERE building_id = ?;""", (33.64511837382568, -117.83486293425993, "UNEXA"))
#cursor.execute(""" UPDATE buildings SET latitude = ?, longitude = ? WHERE building_id = ?;""", (33.62061862706447, -117.89182640357706, "SAIL"))
#cursor.execute(""" UPDATE buildings SET latitude = ?, longitude = ? WHERE building_id = ?;""", (33.64951855640875, -117.84558127304993, "DS"))
#conn.commit()
cursor.execute("""SELECT building_id, name, has_printer, opening_time, closing_time, longitude, latitude FROM buildings;""")
result = cursor.fetchall()

ts_result = []
for building in result:
    ts_result.append({"building_id": building[0], "name": building[1], "has_printer": building[2], "opening_time": building[3], "closing_time": building[4], "longitude": building[5], "latitude": building[6]})
#ts_string = str(ts_result)
#ts_string = '\n{'.join(ts_string.split('{'))
#print(ts_string)
for building in ts_result:
    if building["longitude"] is None:
        print(building)
file = open('zot-zot-study-spot/components/building-data.json', 'w')
json.dump(ts_result, file)
file.close()
conn.close()