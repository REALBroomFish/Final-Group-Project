from flask import Flask, render_template, request, redirect, url_for, session, flash
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import FinalMapping
from collections import defaultdict
import random
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import IntegerField, ValidationError
from wtforms.validators import DataRequired, NumberRange
import os

app = Flask(__name__)
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'
database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'LoginDB.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path.replace('\\', '/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/map2')
def heatmapInteract():
    data_points = 100
    date_1 = 2000
    date_2 = 2023
    clusters = 'c'
    return render_template('map2.html', data_points=data_points, date_1=date_1, date_2=date_2, clusters=clusters)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/home', methods=['GET', 'POST'])
def index():
    if not session.get("loggedin", False):
        return redirect(url_for("login"))
    form = Trendline_Form()
    profiles = load_profiles()
    selected_profiles = profiles[:9]
    current_country = session.get('current_country', "China")

    if request.method == 'POST':
        country_name = request.form.get('country_name', "China")  # Retrieve the country name from form input
        if country_name:  # Check if country name is provided
            session['current_country'] = country_name  
            with open("all_countries.json") as f:
                    all_countries = json.load(f) 
            trendline(all_countries)

        if form.validate_on_submit():
            FinalMapping.main(data_points=form.data_number.data, date_1=form.year1.data, date_2=form.year2.data, clusters='m' if form.toggle.data else 'c')
        else:
            flash("Invalid form data", "error")

    return render_template('index.html', profiles=selected_profiles, form=form, current_country=current_country)



@app.route('/', methods=['GET', 'POST'])
def startup():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("loggedin", False):
        return redirect(url_for("index"))
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = Account.query.filter_by(username=username, password=password).first()
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    if not session.get("loggedin", False):
        return redirect(url_for("startup"))
    try:
        # Remove session variables related to user login
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        flash('You have been logged out.', 'info')  # Using 'info' as the category for informational messages
        # Redirect to the login page
    except Exception as e:
        # Log the exception or handle it in an appropriate way
        print("An error occurred during logout:", e)
        flash('An error occurred during logout. Please try again later.', 'error')  # Using 'error' as the category for error messages
        # Redirect to an error page or display a message to the user
    return redirect(url_for('login'))  # Redirect to a safe page like the index or home page


 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("loggedin", False):
        return redirect(url_for("login"))
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = Account.query.filter_by(username=username).first()
        if existing_user:
            msg = 'Account already exists!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            new_user = Account(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)
    
class Trendline_Form(FlaskForm):
    data_number = IntegerField("Enter Number of Data Points", validators=[DataRequired(), NumberRange(min = 50)])
    year1 = IntegerField("Enter First Year", validators=[DataRequired(), NumberRange(min = 2000, max = 2022)])
    year2 = IntegerField("Enter Second Year", validators=[DataRequired(), NumberRange(min = 2001, max = 2023)])





def trendline(all_countries):
    trendline_country = session.get("current_country", "China")
# plots brand sentiment over time for each brand in each country

    if (len(all_countries[trendline_country]['Apple']) > 0):
        x_apple, y_apple = calc_plots(all_countries[trendline_country]['Apple'])
        plt.plot(x_apple, y_apple, 'g-', label='Apple')

    if (len(all_countries[trendline_country]['Samsung']) > 0):
        x_samsung, y_samsung = calc_plots(all_countries[trendline_country]['Samsung'])
        plt.plot(x_samsung, y_samsung, 'b-', label='Samsung')

    if (len(all_countries[trendline_country]['Huawei']) > 0):       
        x_huawei, y_huawei = calc_plots(all_countries[trendline_country]['Huawei'])
        plt.plot(x_huawei, y_huawei, 'r-', label='Huawei')

    # plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(range(2000,2025,2))
    plt.legend(loc='upper left')
    plt.xlabel('Date')
    plt.ylabel('Sentiment')
    plt.title(f'Average sentiment for {trendline_country} per year')
    plt.grid()
    plt.savefig('static/images/country_data_to_image.png')

    # plt.show()
    


def calc_plots(data_points):
    # Works out plot line for each brands sentiment over time

    # Separate scores and dates
    scores = data_points[::2]
    dates = data_points[1::2]

    # Pair scores with dates
    score_date_pairs = list(zip(scores, dates))

    # Sort the pairs based on dates
    sorted_pairs = sorted(score_date_pairs, key=lambda x: x[1])

    # creates dictionary out of sorted pairs
    sentiment_per_year = defaultdict(list)

    # loops thorugh sorted pairs, adds each year as a key in a dictionary and all the sentiment to each year 
    for sentiment, year in sorted_pairs:
        sentiment_per_year[year].append(sentiment)
    
    # loops through the dictionary and finds the average of the sentiments for each year
    for year, sentiments in sentiment_per_year.items():
        sentiment_per_year[year] = (sum(sentiments) / len(sentiments))

    # converts the dictionary into list
    sorted_pairs = list(sentiment_per_year.items())

    # Unpack the sorted pairs back into separate lists
    sorted_scores, sorted_dates = zip(*sorted_pairs)

    x1 = sorted_scores
    y1 = sorted_dates

    return x1, y1

def load_profiles():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'output_profiles.json')
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return []
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)