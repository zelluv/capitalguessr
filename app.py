from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random
import datetime
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Tarvitaan sessioiden käyttämiseen

def get_countries(region_url):
    response = requests.get(region_url)
    countries = response.json()
    # Valitaan vain itsenäiset maat
    independent_countries = [country for country in countries if country.get('independent', False)]
    return independent_countries

def read_scores():
    try:
        with open('scores.txt', 'r') as file:
            scores = [line.strip().split(',') for line in file.readlines()]
            return scores
    except FileNotFoundError:
        return []

def write_score(score, start_time, region, max_score):
    end_time = time.time()
    duration = end_time - start_time
    minutes, seconds = divmod(int(duration), 60)
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    with open('scores.txt', 'a') as file:
        file.write(f'{date},{minutes}:{seconds:02d},{score},{region} ({max_score} points)\n')

@app.route('/')
def home():
    selected_region = session.get('selected_region', 'https://restcountries.com/v3.1/region/europe')
    countries = get_countries(selected_region)

    # Jos sessio ei ole aloitettu, alusta se
    if 'score' not in session:
        session['score'] = 0
        session['asked_countries'] = []
        session['start_time'] = time.time()
        session['selected_region_name'] = selected_region.split('/')[-1].replace('%20', ' ')

    # Jos kaikki maat on kysytty, näytä tulossivu
    if len(session['asked_countries']) == len(countries):
        max_score = len(countries) * 2  # Each country has a flag and a capital question
        score = session['score']
        write_score(score, session['start_time'], session['selected_region_name'], max_score)
        session.clear()
        recent_scores = read_scores()[-10:]  # Read the 10 most recent scores
        return render_template('final_result.html', score=score, max_score=max_score, recent_scores=recent_scores)

    # Valitse jäljellä olevat maat, joita ei ole vielä kysytty
    remaining_countries = [country for country in countries if country['name']['common'] not in session['asked_countries']]

    # Valitse yksi maa oikeaksi vastaukseksi
    correct_country = random.choice(remaining_countries)
    session['correct_country'] = correct_country['name']['common']
    session['correct_country_flag'] = correct_country['flags']['png']
    session['correct_country_capital'] = correct_country['capital'][0] if 'capital' in correct_country and correct_country['capital'] else 'Unknown'
    session['asked_countries'].append(correct_country['name']['common'])

    # Valitse muut vaihtoehdot kaikista maista, varmistaen, että ne eivät ole sama kuin oikea vastaus
    other_options = [country for country in countries if country['name']['common'] != correct_country['name']['common']]
    selected_countries = random.sample(other_options, 4) + [correct_country]

    # Sekoita valitut maat
    random.shuffle(selected_countries)

    # Hae tarvittavat tiedot
    countries_info = [{
        'name': country['name']['common'],
        'flag': country['flags']['png'],
        'capital': country['capital'][0] if 'capital' in country and country['capital'] else 'Unknown'
    } for country in selected_countries]

    # Laske current_question sen jälkeen, kun uusi kysymys on lisätty listaan
    current_question = len(session['asked_countries'])
    total_questions = len(countries)  # Each country has a flag and a capital question

    return render_template('index.html', countries=countries_info, correct_country=correct_country['name']['common'], correct_capital=session['correct_country_capital'], current_question=current_question, total_questions=total_questions)

@app.route('/select_region')
def select_region():
    regions = {
        'Northern Europe': 'https://restcountries.com/v3.1/subregion/Northern Europe',
        'Southern Europe': 'https://restcountries.com/v3.1/subregion/Southern Europe',
        'Europe': 'https://restcountries.com/v3.1/region/europe'
    }
    region_counts = {}
    for region, url in regions.items():
        countries = requests.get(url).json()
        independent_countries = [country for country in countries if country.get('independent', False)]
        region_counts[region] = len(independent_countries)
    return render_template('select_region.html', regions=regions, region_counts=region_counts)

@app.route('/check', methods=['POST'])
def check():
    if 'correct_country' not in session:
        return redirect(url_for('home'))
    
    selected_country = request.form['country']
    selected_capital = request.form['capital']
    correct_country = session['correct_country']
    correct_country_flag = session['correct_country_flag']
    correct_country_capital = session['correct_country_capital']
    
    country_result = "Correct!" if selected_country == correct_country else f"Wrong! The correct flag of {correct_country} is <img src='{correct_country_flag}' alt='Flag of {correct_country}' width='100'>."
    capital_result = "Correct!" if selected_capital == correct_country_capital else f"Wrong! The capital of {correct_country} is {correct_country_capital}."
    
    if selected_country == correct_country:
        session['score'] += 1
    if selected_capital == correct_country_capital:
        session['score'] += 1
    
    return render_template('result.html', country_result=country_result, capital_result=capital_result)

@app.route('/next')
def next_question():
    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('select_region'))

@app.route('/set_region', methods=['POST'])
def set_region():
    selected_region = request.form['region']
    session['selected_region'] = selected_region
    return redirect(url_for('home'))

@app.route('/recent_scores')
def recent_scores():
    scores = read_scores()[-10:]  # Read the 10 most recent scores
    return render_template('recent_scores.html', recent_scores=scores)

if __name__ == '__main__':
    app.run(debug=True)