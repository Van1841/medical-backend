from geopy.distance import geodesic
import math

HOSPITALS_DATABASE = [
    {"name": "City General Hospital", "lat": 23.0225, "lon": 72.5714},
    {"name": "Apollo Hospital", "lat": 23.0330, "lon": 72.5650},
    {"name": "Sterling Hospital", "lat": 23.0300, "lon": 72.5800},
    {"name": "Shalby Hospital", "lat": 23.0500, "lon": 72.5500},
    {"name": "Zydus Hospital", "lat": 23.0100, "lon": 72.5900},
    {"name": "Krishna Heart Hospital", "lat": 23.0400, "lon": 72.5600},
    {"name": "Civil Hospital", "lat": 23.0350, "lon": 72.5750},
    {"name": "Medanta Hospital", "lat": 23.0150, "lon": 72.5850},
    {"name": "Max Hospital", "lat": 23.0450, "lon": 72.5550},
    {"name": "Fortis Hospital", "lat": 23.0200, "lon": 72.5700},
]

def find_nearest_hospitals(user_lat, user_lon, limit=5):
    try:
        user_location = (user_lat, user_lon)
        
        hospitals_with_distance = []
        
        for hospital in HOSPITALS_DATABASE:
            hospital_location = (hospital['lat'], hospital['lon'])
            distance = geodesic(user_location, hospital_location).kilometers
            
            hospitals_with_distance.append({
                'name': hospital['name'],
                'distance': round(distance, 2),
                'lat': hospital['lat'],
                'lon': hospital['lon']
            })
        
        hospitals_with_distance.sort(key=lambda x: x['distance'])
        
        return hospitals_with_distance[:limit]
        
    except Exception as e:
        print(f"Hospital locator error: {str(e)}")
        return []

def get_google_maps_link(lat, lon):
    return f"https://www.google.com/maps/search/hospitals/@{lat},{lon},14z"
