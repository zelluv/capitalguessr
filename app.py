from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

@app.route('/')
def home():
    # Hae kaikki Euroopan maat
    response = requests.get('https://restcountries.com/v3.1/region/europe')
    countries = response.json()
    
    # Valitse viisi satunnaista maata
    selected_countries = random.sample(countries, 5)

    # Valitse yksi maa oikeaksi vastaukseksi
    correct_country = random.choice(selected_countries)
    
    # Hae tarvittavat tiedot
    countries_info = [{
        'name': country['name']['common'],
        'flag': country['flags']['png']
    } for country in selected_countries]
    
    return render_template('index.html', countries=countries_info, correct_country=correct_country['name']['common'])

@app.route('/check', methods=['POST'])
def check():
    selected_country = request.form['country']
    correct_country = request.form['correct_country']
    if selected_country == correct_country:
        result = "Correct!"
    else:
        result = "Wrong! The correct answer was " + correct_country
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)