from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Tarvitaan sessioiden käyttämiseen

def get_countries():
    response = requests.get('https://restcountries.com/v3.1/subregion/Northern Europe')
    # response = requests.get('https://restcountries.com/v3.1/region/europe')
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

def write_score(score):
    with open('scores.txt', 'a') as file:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f'{date},{score}\n')

@app.route('/')
def home():
    # Hae kaikki Euroopan maat
    countries = get_countries()

    # Jos sessio ei ole aloitettu, alusta se
    if 'score' not in session:
        session['score'] = 0
        session['asked_countries'] = []

    # Jos kaikki maat on kysytty, näytä tulossivu
    if len(session['asked_countries']) == len(countries):
        max_score = len(countries) * 2  # Each country has a flag and a capital question
        score = session['score']
        write_score(score)
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
    total_questions = len(countries)

    return render_template('index.html', countries=countries_info, correct_country=correct_country['name']['common'], correct_capital=session['correct_country_capital'], current_question=current_question, total_questions=total_questions)

@app.route('/check', methods=['POST'])
def check():
    if 'correct_country' not in session:
        return redirect(url_for('home'))
    
    selected_country = request.form['country']
    selected_capital = request.form['capital']
    correct_country = session['correct_country']
    correct_country_flag = session['correct_country_flag']
    correct_country_capital = session['correct_country_capital']
    
    country_result = "Correct!" if selected_country == correct_country else f"Wrong! The correct flag is <img src='{correct_country_flag}' alt='Flag of {correct_country}' width='100'>."
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
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)