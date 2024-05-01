from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import matplotlib.pyplot as plt
import json
import FinalMapping
from collections import defaultdict
app = Flask(__name__)

#templates stuff
#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/map2')
def heatmapInteract():
    data_points = 100
    date_1 = 2000
    date_2 = 2023
    clusters = 'c'
    return render_template('map2.html', data_points=data_points, date_1=date_1, date_2=date_2, clusters=clusters)


#database stuff (mysql) from geeks-to-geeks:   https://www.geeksforgeeks.org/login-and-registration-project-using-flask-and-mysql/
#1
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wBbazXHBCTr0@x^7LSwrn8#0'
app.config['MYSQL_DB'] = 'projectlogin'
mysql = MySQL(app)

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    try:
        # Remove session variables related to user login
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        # Redirect to the login page
        return redirect(url_for('login'))
    except Exception as e:
        # Log the exception or handle it in an appropriate way
        print("An error occurred during logout:", e)
        # Redirect to an error page or display a message to the user
        return "An error occurred during logout. Please try again later."
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (% s, % s, % s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


#taking input from text file
@app.route('/analyse_country', methods=['POST'])
def analyse_country():
    # Retrieve the country name from the form data
    country_name = request.form['country_name']
    with open("all_countries.json") as f:
        all_countries = json.load(f)


    # where calculations go so  

    print(f" country name: {country_name}")
    trendline(country_name, all_countries)   
    print("done")

    # Return a JSON response indicating success
    #country = "Japan"
    #return render_template('index.html', country = country)
    return render_template('index.html')



def trendline(trendline_country, all_countries):
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
    #plt.show()
    


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



#taking input from 4 inputs
@app.route('/handle_input', methods=['POST'])
def handle_input():
    # Retrieve the country name from the form data
    input1 = request.form['input1']
    input2 = request.form['input2']
    input3 = request.form['input3']
    toggle = request.form.get('toggle')
    input4 = 'm' if toggle == 'on' else 'c'

    print(f" input1:  {input1}")
    print(f" input2:  {input2}")
    print(f" input3:  {input3}")
    print(f" input4:  {input4}")
    #return render_template('map2.html')
    FinalMapping.main(data_points=input1, date_1=input2, date_2=input3, clusters=input4)
    
    return render_template('map2.html')

if __name__ == '__main__':
    app.run(debug=True)
