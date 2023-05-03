from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = "C:/Users/maxmo/PycharmProjects/TeReoDictonary-Assesment/TeReo"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = ("deeznutz42069")

def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

def is_teacher():
    if session.get("permissions") == "teacher":
        print("is teacher")
        return True
    else:
        print("is not teacher")
        return False

def create_connection(db_file):
    """
    create a connection with a database
    :parameter name of the database
    :return a connection to the file
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_homepage():  # put application's code here
    if is_teacher():
        print("is teacher")
    return render_template('home.html', logged_in=is_logged_in(), is_teacher=is_teacher())

@app.route('/search', methods=['GET', 'POST'])
def render_search():
    search = request.form['search']
    query = "SELECT maori, english, category, definition, level FROM Dictionary WHERE maori like ? OR english like ?  OR category like ? OR definition like ?  OR level like ?"
    search = "%" + search + "%"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search, search, search, search))
    definition_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('search.html', logged_in=is_logged_in(), definitions=definition_list, is_teacher=is_teacher())

@app.route('/words')
def render_words():  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level FROM Dictionary"
    cur = con.cursor()
    cur.execute(query)
    definition_list = cur.fetchall()
    query = "SELECT id, category FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('words.html', logged_in=is_logged_in(), definitions=definition_list, categories=category_list, is_teacher=is_teacher())

@app.route('/words/<category>')
def render_words_category(category):  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level FROM Dictionary WHERE category=?"
    cur = con.cursor()
    cur.execute(query, (category, ))
    definition_list = cur.fetchall()
    query = "SELECT id, category FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('words.html', logged_in=is_logged_in(), definitions=definition_list, categories=category_list, is_teacher=is_teacher())

@app.route('/login', methods=['POST', 'GET'])
def render_login():  # put application's code here
    if is_logged_in():
        return redirect('/')
    print("logging in")
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email)
        query = """SELECT id, fname, password, permission FROM user WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchone()
        con.close

        try:
            user_id = user_data[0]
            first_name = user_data[1]
            db_password = user_data[2]
            permissions = user_data[3]
        except IndexError:
            return redirect("/login?error=Email+or+invalid+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer, "?error=Email+or+invalid+password+inncorrect")

        session['email'] = email
        session['firstname'] = first_name
        session['user_id'] = user_id
        session['permissions'] = permissions
        print(session)
        return redirect('/')
    return render_template('login.html', is_teacher=is_teacher())

@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():  # put application's code here
    if is_logged_in():
        return redirect('/menu/1')
    if request.method == "POST":
        print(request.form)
        fname = request.form.get("fname").title().strip()
        lname = request.form.get("lname").title().strip()
        email = request.form.get("email").lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        permission = request.form.get('code')

        if permission == '1111':
            permission == 'teacher'
        elif permission == '':
            permission == 'student'
        else:
            return redirect("\signup?error=Teacher+code+inncorrect")

        if password != password2:
            return redirect("\signup?error=Password+do+not+match")

        if len(password) < 8:
            return redirect("\signup?error=Password+must+be+at+least+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DATABASE)
        query = "INSERT INTO user (fname, lname, email, password, permission) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (fname, lname, email, hashed_password, permission))
        except sqlite3.IntegrityError:
            con.close
            return redirect("\signup?error=Email+is+already+used")

        con.commit()
        con.close

        return redirect("\login")

    return render_template('signup.html', logged_in=is_logged_in(), is_teacher=is_teacher())

@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=see+you+next+time!')

@app.route('/admin')
def admin():
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "SELECT id, category FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return render_template("admin.html", logged_in=is_logged_in(), categories=category_list, is_teacher=is_teacher())

@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        cat_name = request.form.get('name').lower().strip()
        print(cat_name)
        con = create_connection(DATABASE)
        query = "INSERT INTO categories ('category') VALUES (?)"
        cur = con.cursor()
        cur.execute(query, (cat_name, ))
        con.commit()
        con.close()
        return redirect("/admin")

@app.route('/delete_category', methods=['POST'])
def delete_category():
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    if request.method == "POST":
        category = request.form.get('cat_id')
        print(category)
        category = category.split(", ")
        cat_id = category[0]
        cat_name = category[1]
        return render_template("delete_confirm.html", id=cat_id, name=cat_name, type="category")
    return redirect("/admin")

@app.route('/delete_category_confirm/<category>')
def delete_category_confirm(category):
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "DELETE FROM categories WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (category, ))
    con.commit()
    con.close()
    return redirect("/admin")

if __name__ == '__main__':
    app.run()
