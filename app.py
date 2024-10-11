from flask import Flask, render_template
import requests
import random

app = Flask(__name__)

@app.route('/')
def home():
    # Hae kaikki Euroopan maat
    response = requests.get('https://restcountries.com/v3.1/region/europe')
    countries = response.json()
    
    # Valitse satunnainen maa
    country = random.choice(countries)
    
    # Hae tarvittavat tiedot
    country_info = {
        'name': country['name']['common'],
        'capital': country['capital'][0] if 'capital' in country and country['capital'] else 'N/A',
        'population': country['population'],
        'flag': country['flags']['png']
    }
    
    return render_template('index.html', country=country_info)

if __name__ == '__main__':
    app.run(debug=True)