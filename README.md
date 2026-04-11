# pakistan travel assistant 🗺️

A full-stack web app that finds the shortest route between any two cities in Pakistan and predicts the travel cost — all powered by A* search and a Random Forest ML model. Built for the AI Lab course (CSL-411) at Bahria University Karachi Campus.

---

## what it does

Planning a trip in Pakistan usually means juggling Google Maps for directions and guessing costs based on your vehicle. This app solves both in one place — type your start city, end city, and vehicle type, and it gives you the optimal route and an estimated cost immediately.

It also has a chatbot assistant for quick travel queries and saves your trip history automatically.

---

## how it works

```
user input (city A → city B, vehicle type)
        ↓
geocoding via Geopy → coordinates
        ↓
KDTree spatial index → nearest graph nodes
        ↓
A* search on road network graph → shortest path + distance
        ↓
Random Forest model → predicted cost (PKR)
        ↓
MongoDB → trip saved to history
        ↓
result displayed on frontend
```

**A\* search** uses the Haversine formula as the heuristic — straight-line distance between coordinates — to prioritize nodes closer to the destination and avoid exploring unnecessary paths.

**Random Forest Regressor** is trained on distance + vehicle type pairs and predicts cost in PKR. Vehicle types supported: Bike, Car, Bus/Van.

---

## tech stack

| layer | tech |
|-------|------|
| backend | Python, Flask |
| AI / pathfinding | NetworkX (A* search), Haversine heuristic |
| ML model | Scikit-Learn (Random Forest Regressor) |
| geospatial | GeoPandas, Shapely, Geopy |
| database | MongoDB |
| frontend | HTML5, CSS3, Vanilla JavaScript |
| road data | OpenStreetMap shapefile (`hotosm_pak_roads_lines_shp.shp`) |

---

## getting started

**prerequisites**
- Python 3.8+
- MongoDB running locally
- The OSM shapefile (see project drive link below)

**install dependencies**
```bash
pip install flask pymongo networkx scikit-learn geopandas shapely geopy
```

**run the app**
```bash
python app.py
```

Then open `http://localhost:5000` in your browser. On first launch the app will load the shapefile, build the road graph in memory, and train the ML model — this takes a moment but only happens once.

---

## features

- shortest route between any two Pakistani cities using A* search
- travel cost prediction for bike, car, or bus/van
- rule-based chatbot for common travel queries
- trip history saved to MongoDB per user session
- fully offline after initial setup — no external APIs needed

---

## project structure

```
AILAB/
├── cities/                 # city data / geospatial files
├── hotels/                 # hotel/accommodation data
├── templates/              # HTML frontend templates
└── app.py                  # main Flask server — routes, A* search, ML model, chatbot
```

---

## future plans

- real-time traffic integration via Google Maps API
- LLM-powered chatbot for natural conversations
- user authentication with private trip histories
- web dashboard with route visualisation on a map
- support for more vehicle types and multi-stop trips

---

## project drive

All source files and assets: [Google Drive](https://drive.google.com/drive/folders/1FOUoPTgflZr9vqoH4sorvGS9wbBHKDdN?usp=sharing)

---

## team

| name | enrollment |
|------|------------|
| Huzaifa Ali | 02-235231-027 |
| M. Izhan Khan | 02-235231-045 |
| Huzaifa Nadeem | 02-235231-032 |

submitted to **Ms. Madiha Aslam** — AI Lab (CSL-411), BSIT 6A Fall 2025, Bahria University Karachi Campus
