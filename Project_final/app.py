from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import sqlite3
from init_db import init_db
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'key'
DATABASE = 'database.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=20)
init_db()

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def register(self):
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username, self.password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (self.username,))
        record = cursor.fetchone()
        conn.close()
        if record and check_password_hash(record[0], self.password):
            return True
        return False

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.login():
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.register():
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.')
    return render_template('register.html')


@app.route("/add_meal", methods=['GET', 'POST'])
def add_meal():
    if 'username' not in session:
        flash("You need to be logged in to add a meal.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            calories = request.form['calories']
            price = request.form['price']

            conn = sqlite3.connect( 'database.db' )
            cur = conn.cursor()
            cur.execute("INSERT INTO meals (name, description, calories, price) VALUES (?,?,?,?)",
                        (name, description, calories, price))
            conn.commit()
            msg = "Meal successfully added to database"
            conn.close()
        except Exception as e:
            msg = f"Error in the INSERT: {str(e)}"
        return render_template('result.html', msg=msg)
    return render_template("add_meal.html")



@app.route("/add_meal", methods=['POST'])
def add_meal_post():
    try:
        name = request.form['name']
        description = request.form['description']
        calories = request.form['calories']
        price = request.form['price']

        conn = sqlite3.connect( 'database.db' )
        cur = conn.cursor()
        cur.execute("INSERT INTO meals (name, description, calories, price) VALUES (?,?,?,?)",
                    (name, description, calories, price))
        conn.commit()
        msg = "Meal successfully added to database"
        conn.close()
    except Exception as e:
        msg = f"Error in the INSERT: {str(e)}"
    return render_template('result.html', msg=msg)

@app.route('/list_meals')
def list_meals():
    con = sqlite3.connect( "database.db" )
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM meals")
    rows = cur.fetchall()
    con.close()
    return render_template("list_meals.html", rows=rows)

@app.route("/edit_meal/<int:rowid>", methods=['GET', 'POST'])
def edit_meal(rowid):
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            calories = request.form['calories']
            price = request.form['price']

            with sqlite3.connect( 'database.db' ) as con:
                cur = con.cursor()
                cur.execute("UPDATE meals SET name=?, description=?, calories=?, price=? WHERE rowid=?",
                            (name, description, calories, price, rowid))
                con.commit()
                msg = "Meal successfully edited in the database"
        except Exception as e:
            msg = f"Error in the Edit: {str(e)}"
        return render_template('result.html', msg=msg)
    else:
        with sqlite3.connect( 'database.db' ) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM meals WHERE rowid=?", (rowid,))
            meal = cur.fetchone()
            if not meal:
                msg = "Meal not found"
                return render_template('result.html', msg=msg)
        return render_template('edit_meal.html', meal=dict(meal))

@app.route("/delete_meal", methods=['POST'])
def delete_meal():
    try:
        rowid = request.form['rowid']
        with sqlite3.connect( 'database.db' ) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM meals WHERE rowid=?", (rowid,))
            con.commit()
            msg = "Meal successfully deleted from the database"
    except Exception as e:
        msg = f"Error in the DELETE: {str(e)}"
    return render_template('result.html', msg=msg)


@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/about')
def aboutus():
    return render_template('aboutus.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')


if __name__ == '__main__':
    app.run(debug=True)
