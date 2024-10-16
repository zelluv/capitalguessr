from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Tarvitaan sessioiden käyttämiseen

def get_countries():
    response = requests.get('https://restcountries.com/v3.1/region/europe')
    countries = response.json()
    # Valitaan vain itsenäiset maat
    independent_countries = [country for country in countries if country.get('independent', False)]
    return independent_countries

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
        max_score = len(countries)
        score = session['score']
        session.clear()
        return render_template('final_result.html', score=score, max_score=max_score)

    # Valitse jäljellä olevat maat, joita ei ole vielä kysytty
    remaining_countries = [country for country in countries if country['name']['common'] not in session['asked_countries']]

    # Valitse yksi maa oikeaksi vastaukseksi
    correct_country = random.choice(remaining_countries)
    session['correct_country'] = correct_country['name']['common']
    session['correct_country_flag'] = correct_country['flags']['png']
    session['asked_countries'].append(correct_country['name']['common'])

    # Lista tietyistä maista
    specific_countries = ['Slovenia', 'Slovakia', 'Croatia', 'Serbia', 'Netherlands']

    # Jos oikea maa on yksi tietyistä maista, aseta vaihtoehdoiksi nämä viisi maata
    if correct_country['name']['common'] in specific_countries:
        selected_countries = [country for country in countries if country['name']['common'] in specific_countries]
    else:
        # Valitse muut vaihtoehdot kaikista maista, varmistaen, että ne eivät ole sama kuin oikea vastaus
        other_options = [country for country in countries if country['name']['common'] != correct_country['name']['common']]
        selected_countries = random.sample(other_options, 4) + [correct_country]

    # Sekoita valitut maat
    random.shuffle(selected_countries)

    # Hae tarvittavat tiedot
    countries_info = [{
        'name': country['name']['common'],
        'flag': country['flags']['png']
    } for country in selected_countries]

    # Laske current_question sen jälkeen, kun uusi kysymys on lisätty listaan
    current_question = len(session['asked_countries'])
    total_questions = len(countries)

    return render_template('index.html', countries=countries_info, correct_country=correct_country['name']['common'], current_question=current_question, total_questions=total_questions)

@app.route('/check', methods=['POST'])
def check():
    if 'correct_country' not in session:
        return redirect(url_for('home'))
    
    selected_country = request.form['country']
    correct_country = session['correct_country']
    correct_country_flag = session['correct_country_flag']
    if selected_country == correct_country:
        session['score'] += 1
        result = "Correct!"
    else:
        result = f"Wrong! The flag of {correct_country} is <img src='{correct_country_flag}' alt='Flag of {correct_country}' width='100'>"
    
    return render_template('result.html', result=result)

@app.route('/next')
def next_question():
    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)