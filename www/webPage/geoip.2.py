import ast
import json

geoip = list()
with open('server_map.txt') as file:
    for line in file:
        _, ip, latlng = line.strip().split(' ', 2)
        try:
            geoip.append(dict(
                name=ip, 
                latLng=ast.literal_eval(latlng),
            ))
        except SyntaxError:
            print(ip, latlng)

print(geoip)
with open('server_map.json', 'w') as file:
    json.dump(geoip, file)
