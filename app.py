from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Tarvitaan sessioiden käyttämiseen

@app.route('/')
def home():
    # Hae kaikki Euroopan maat, jos niitä ei ole jo haettu
    if 'countries' not in session:
        response = requests.get('https://restcountries.com/v3.1/region/europe')
        session['countries'] = response.json()
        session['score'] = 0
        session['asked_countries'] = []

    # Jos kaikki maat on kysytty, näytä tulossivu
    if len(session['asked_countries']) == len(session['countries']):
        max_score = len(session['countries'])
        score = session['score']
        session.clear()
        return render_template('final_result.html', score=score, max_score=max_score)

    # Valitse viisi satunnaista maata, joita ei ole vielä kysytty
    remaining_countries = [country for country in session['countries'] if country['name']['common'] not in session['asked_countries']]
    selected_countries = random.sample(remaining_countries, 5)

    # Valitse yksi maa oikeaksi vastaukseksi
    correct_country = random.choice(selected_countries)
    session['correct_country'] = correct_country['name']['common']
    session['asked_countries'].append(correct_country['name']['common'])

    # Hae tarvittavat tiedot
    countries_info = [{
        'name': country['name']['common'],
        'flag': country['flags']['png']
    } for country in selected_countries]

    # Laske current_question sen jälkeen, kun uusi kysymys on lisätty listaan
    current_question = len(session['asked_countries'])
    total_questions = len(session['countries'])

    return render_template('index.html', countries=countries_info, correct_country=correct_country['name']['common'], current_question=current_question, total_questions=total_questions)

@app.route('/check', methods=['POST'])
def check():
    if 'correct_country' not in session:
        return redirect(url_for('home'))
    
    selected_country = request.form['country']
    correct_country = session['correct_country']
    if selected_country == correct_country:
        session['score'] += 1
        result = "Correct!"
    else:
        result = "Wrong! The correct answer was " + correct_country
    
    return render_template('result.html', result=result)

@app.route('/next')
def next_question():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)