# Smart Travel Planner (AI-Based Intelligent Trip Planning System)

A Flask web app for Pakistan trip planning that combines:
- rule-based trip conversation
- A* route search over a predefined intercity graph
- ML-based hotel price estimation using linear regression
- user login and trip history storage in MongoDB

## What The Current Code Actually Does

The core application is in `AILAB/app.py`.

1. Authenticates users with username/password (hashed via Werkzeug).
2. Stores users and conversation history in MongoDB (`travel_planner` database).
3. Detects source/destination cities from user text (supported city set is hardcoded in `app.py`).
4. Computes route + total road distance with A* using Haversine heuristic.
5. Estimates transport cost based on selected mode (`car`, `bike`, `bus`).
6. Predicts hotel nightly price from `AILAB/hotels/hotel.csv` using a trained `LinearRegression` model on:
   - `Customer_Rating`
   - `Amenities_Count`
7. Returns a formatted response in the chat UI and saves the message pair to trip history.

## Important Clarification

Previous README content mentioned Geopy, KDTree, NetworkX, shapefiles, and Random Forest. Those are **not** used in the current codebase.

Current implementation uses:
- custom graph dictionary + `heapq` for A*
- `math` Haversine distance
- `sklearn.linear_model.LinearRegression`
- Flask templates + vanilla JS frontend

## Tech Stack

- Backend: Python, Flask
- Auth/session: Flask-Login, Werkzeug security
- Database: MongoDB (PyMongo)
- Data/ML: pandas, scikit-learn (Linear Regression)
- Frontend: HTML, CSS, Bootstrap, vanilla JavaScript

## Project Structure

```text
.
├─ README.md
└─ AILAB/
   ├─ app.py
   ├─ cities/
   │  └─ city.csv
   ├─ hotels/
   │  └─ hotel.csv
   └─ templates/
      ├─ index.html
      ├─ login.html
      └─ signup.html
