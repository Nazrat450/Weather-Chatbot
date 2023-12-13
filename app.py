from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import sqlite3




######MatthewHill#####################
##                                  ##   
##  101139468@student.swin.edu.au   ##
##                                  ##
######################################


# Define the function to initialize the database
def init_db():
    conn = sqlite3.connect('mattbot.db')
    cursor = conn.cursor()


# Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('mattbot.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create table for predefined responses
cursor.execute('''CREATE TABLE IF NOT EXISTS responses
                  (id INTEGER PRIMARY KEY, query TEXT, response TEXT)''')

# Create table for logging chat sessions
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_log
                  (id INTEGER PRIMARY KEY, user_input TEXT, bot_response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

 # Create a table for response templates
cursor.execute('''CREATE TABLE IF NOT EXISTS response_templates (
                        id INTEGER PRIMARY KEY,
                        template TEXT)''')



# Insert a default template if not exists
cursor.execute('''INSERT INTO response_templates (id, template)
                      SELECT 1, 'Hi I am the channel 42 Weather man bringing you the Weather. The weather in {location} is {condition} with a temperature of {temperature}°C.'
                      WHERE NOT EXISTS(SELECT 1 FROM response_templates WHERE id = 1);''')
# Insert a greeting response template into the database
cursor.execute("INSERT INTO responses (query, response) VALUES (?, ?)", 
               ("greeting", "G'day! I am the Channel 42 weather bot here to help."))
# Commit the changes and close the connection
conn.commit()
conn.close()

init_db()

#42c10c6eeff25fdb9a2e1ae45c758f7f

# Create a chatbot instance
chatbot = ChatBot('WeatherBot')

# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the English corpus
trainer.train("chatterbot.corpus.english")




app = Flask(__name__)

@app.route("/get-response", methods=['POST'])
def get_bot_response():
    user_input = request.form.get('text').lower()

    
     # Check for greeting in the user input
    if user_input in ['hello', 'hi', 'greetings', 'hey']:
        # Fetch greeting response from database
        conn = sqlite3.connect('mattbot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM responses WHERE query = 'greeting'")
        data = cursor.fetchone()
        conn.close()

        if data:
            bot_response = data[0]
        else:
            bot_response = "Hello! How can I assist you?"

    elif 'weather' in user_input.lower():
        city_name = user_input.split()[-1]  # Simple method to get city name
        api_key = "42c10c6eeff25fdb9a2e1ae45c758f7f"
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"

        # Fetch weather data from API
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            condition = weather_data['weather'][0]['description']

            # Fetch response template from database
            conn = sqlite3.connect('mattbot.db')
            cursor = conn.cursor()
            cursor.execute("SELECT template FROM response_templates WHERE id = 1")  # Assuming 1 is the ID of your template
            template = cursor.fetchone()[0]
            conn.close()

            # Fill in the template
            bot_response = template.format(location=city_name, temperature=temperature, condition=condition)
        else:
            bot_response = "Sorry, I couldn't find the weather for that location."
    else:
        # Normal chatbot response
        bot_response = str(chatbot.get_response(user_input))

    return jsonify(bot_response=bot_response)



weather_data = []  # Global variable to store weather data
error_message = None  # Variable to store the error message
@app.route('/', methods=['GET', 'POST'])
def index():
    global weather_data  # Use the global variable
    # Locations defined by assignment
    locations = [
        {"name": "Lake District National Park", "lat": 54.4609, "lon": -3.0886},
        {"name": "Corfe Castle", "lat": 50.6395, "lon": -2.0566},
        {"name": "The Cotswolds", "lat": 51.8330, "lon": -1.8433},
        {"name": "Cambridge", "lat": 52.2053, "lon": 0.1218},
        {"name": "Bristol", "lat": 51.4545, "lon": -2.5879},
        {"name": "Oxford", "lat": 51.7520, "lon": -1.2577},
        {"name": "Norwich", "lat": 52.6309, "lon": 1.2974},
        {"name": "Stonehenge", "lat": 51.1789, "lon": -1.8262},
        {"name": "Watergate Bay", "lat": 50.4429, "lon": -5.0553},
        {"name": "Birmingham", "lat": 52.4862, "lon": -1.8904}
    ]
    #Search bar
    existing_locations = {entry['location'] for entry in weather_data} 
    if request.method == 'POST':
        user_location = request.form.get('location')
        if user_location and user_location not in existing_locations:
            api_url = f"https://api.openweathermap.org/data/2.5/weather?q={user_location}&appid=42c10c6eeff25fdb9a2e1ae45c758f7f&units=metric"
            response = requests.get(api_url)
            if response.status_code == 200:
                current_weather = response.json()
                weather_data.append({
                    'location': user_location,
                    'temperature': current_weather['main']['temp'],
                    'condition': current_weather['weather'][0]['description']
                })
        return render_template('index.html', weather_data=weather_data)
    #Using lat and lon to pull locations
    if request.method == 'GET':
        for location in locations:
            if location['name'] not in existing_locations:
                lat, lon = location['lat'], location['lon']
                api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=42c10c6eeff25fdb9a2e1ae45c758f7f&units=metric"
                response = requests.get(api_url)
                if response.status_code == 200:
                    current_weather = response.json()
                    weather_data.append({
                        'location': location['name'],
                        'temperature': current_weather['main']['temp'],
                        'condition': current_weather['weather'][0]['description']
                    })
                    

    return render_template('index.html', weather_data=weather_data)

@app.route('/clear', methods=['GET'])
def clear_data():
    global weather_data
    weather_data.clear()
    return redirect(url_for('index'))







if __name__ == "__main__":
    app.run(debug=True)
