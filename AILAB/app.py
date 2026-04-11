from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from sklearn.linear_model import LinearRegression 
import pandas as pd 
import math
import heapq

app = Flask(__name__)
app.secret_key = 'f858e7f6ac4e33bb36a291b547fbaf7d' 

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["travel_planner"]
    users_col = db["users"]
    chats_col = db["conversations"] 
    print("Connected to MongoDB!")
except Exception as e:
    print(f"MongoDB Error: {e}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']

@login_manager.user_loader
def load_user(user_id):
    user_data = users_col.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None

cities_df = pd.read_csv('cities/city.csv')
hotels_df = pd.read_csv('hotels/hotel.csv')

def train_hotel_model():
    X = hotels_df[['Customer_Rating', 'Amenities_Count']].values
    y = hotels_df['Room_Rate_PKR'].values
    model = LinearRegression()
    model.fit(X, y)
    return model

hotel_price_model = train_hotel_model()

def predict_hotel_price(city_name):
    """Predicts a hotel price for a city using the trained ML model."""
    city_data = hotels_df[hotels_df['City'].str.lower() == city_name.lower()]
    if not city_data.empty:
        avg_rating = city_data['Customer_Rating'].mean()
        avg_amenities = city_data['Amenities_Count'].mean()
    else:
        avg_rating, avg_amenities = 3.5, 10  
        
    prediction = hotel_price_model.predict([[avg_rating, avg_amenities]])
    return max(2500, int(prediction[0])) 

city_coords = {
    'karachi': (24.8607, 67.0011), 'hyderabad': (25.3960, 68.3578),
    'sukkur': (27.7244, 68.8228), 'multan': (30.1575, 71.5249),
    'lahore': (31.5204, 74.3587), 'islamabad': (33.6844, 73.0479),
    'peshawar': (34.0151, 71.5249), 'quetta': (30.1798, 66.9750)
}

roads = [
    ('karachi', 'hyderabad', 160), ('hyderabad', 'sukkur', 330),
    ('sukkur', 'multan', 440), ('multan', 'lahore', 350),
    ('lahore', 'islamabad', 380), ('islamabad', 'peshawar', 180),
    ('quetta', 'multan', 600), ('sukkur', 'quetta', 400)
]

graph = {}
for u, v, w in roads:
    graph.setdefault(u, []).append((v, w))
    graph.setdefault(v, []).append((u, w))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def a_star(start, goal):
    if start not in city_coords or goal not in city_coords: return None, 0
    pq = [(haversine(*city_coords[start], *city_coords[goal]), 0, start, [])]
    visited = {}
    while pq:
        f, g, current, path = heapq.heappop(pq)
        if current == goal: return path + [current], g
        if current in visited and visited[current] <= g: continue
        visited[current] = g
        for neighbor, weight in graph.get(current, []):
            g_new = g + weight
            h = haversine(*city_coords[neighbor], *city_coords[goal])
            heapq.heappush(pq, (g_new + h, g_new, neighbor, path + [current]))
    return None, 0

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users_col.find_one({"username": username}):
            return "Username already exists!"
        hashed_pw = generate_password_hash(password)
        users_col.insert_one({"username": username, "password": hashed_pw})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = users_col.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(user_data)
            login_user(user_obj)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    history = list(chats_col.find({"user_id": current_user.id}).sort("last_updated", -1))
    active_id = session.get('current_trip_id')
    current_chat_messages = []
    
    if active_id:
        chat_data = chats_col.find_one({"_id": ObjectId(active_id)})
        if chat_data:
            current_chat_messages = chat_data.get('messages', []) 
            
    return render_template('index.html', 
                           user=current_user, 
                           history=history, 
                           current_chat_messages=current_chat_messages)

@app.route('/get_history/<chat_id>')
@login_required
def get_history(chat_id):
    chat = chats_col.find_one({"_id": ObjectId(chat_id), "user_id": current_user.id})
    session['current_trip_id'] = chat_id 
    if chat:
        return jsonify({"messages": chat['messages']})
    return jsonify({"error": "Not found"}), 404

@app.route('/new_chat')
@login_required
def new_chat():
    session.pop('current_trip_id', None)  
    session.pop('last_start', None)
    session.pop('last_goal', None)
    return jsonify({"status": "success"})

@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        result = chats_col.delete_one({"_id": ObjectId(chat_id), "user_id": current_user.id})
        if result.deleted_count > 0:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Chat not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_input = request.json.get("message", "").lower()
    current_trip_id = session.get('current_trip_id')

    prev_start = session.get('last_start')
    prev_goal = session.get('last_goal')
    mentioned_cities = [c for c in city_coords.keys() if c in user_input]
    
    if len(mentioned_cities) >= 2:
        start, goal = (mentioned_cities[0], mentioned_cities[1]) if user_input.find(mentioned_cities[0]) < user_input.find(mentioned_cities[1]) else (mentioned_cities[1], mentioned_cities[0])
        session['last_start'], session['last_goal'] = start, goal
        context_msg = f"Got it! Planning a new trip from {start.title()} to {goal.title()}."
    elif prev_start and prev_goal:
        start, goal = prev_start, prev_goal
        context_msg = f"Looking at your trip to {goal.title()} again..."
    else:
        return jsonify({"reply": "I'd love to help! Please tell me your starting city and destination."})

    mode = session.get('last_mode', 'car')
    if 'bike' in user_input or 'motorcycle' in user_input: mode = 'bike'
    elif 'car' in user_input: mode = 'car'
    elif any(word in user_input for word in ['bus', 'cheap', 'budget', 'faisal movers', 'daewoo']): mode = 'bus'
    session['last_mode'] = mode

    route, dist = a_star(start, goal)
    if not route: return jsonify({"reply": "I couldn't find a route for that trip."})

    if mode == 'bus':
        transport_cost = dist * 5.5
        vendor = "via Daewoo Express or Faisal Movers"
    else:
        mileage = 14 if mode == 'car' else 45
        tolls = len(route) * (200 if mode == 'car' else 0)
        transport_cost = (dist / mileage * 280) + tolls
        vendor = f"based on {mode} fuel average"
    hotel_pred = predict_hotel_price(goal)
    total_est = transport_cost + hotel_pred

    reply_content = (f"{context_msg}<br><br>"
                     f"✅ <b>Updated Plan:</b> Traveling by <b>{mode.upper()}</b>.<br>"
                     f"🛣️ <b>Route:</b> {' ➔ '.join([c.title() for c in route])}<br>"
                     f"📏 <b>Distance:</b> {dist:.0f} km<br>"
                     f"💰 <b>Transport Cost:</b> Rs. {transport_cost:,.0f} ({vendor})<br>"
                     f"🏨 <b>AI-Predicted Hotel ({goal.title()}):</b> Rs. {hotel_pred:,.0f}/night<br>"
                     f"💵 <b>Estimated Total:</b> Rs. {total_est:,.0f}")

    message_pair = {
        "prompt": user_input,
        "reply": reply_content,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if current_trip_id:
        chats_col.update_one(
            {"_id": ObjectId(current_trip_id), "user_id": current_user.id},
            {
                "$push": {"messages": message_pair},
                "$set": {"last_updated": pd.Timestamp.now(), "title": goal.title()}
            }
        )
    else:
        new_chat = {
            "user_id": current_user.id,
            "username": current_user.username,
            "title": goal.title(),
            "messages": [message_pair],
            "last_updated": pd.Timestamp.now()
        }
        inserted = chats_col.insert_one(new_chat)
        current_trip_id = str(inserted.inserted_id)
        session['current_trip_id'] = current_trip_id

    return jsonify({
        "reply": reply_content,
        "trip_id": current_trip_id,
        "title": goal.title()
    })

if __name__ == '__main__':
    app.run(debug=True)