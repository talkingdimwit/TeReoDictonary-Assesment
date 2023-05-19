from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = 'C:/Users/19037/PycharmProjects/TeReoDictonary-Assesment/TeReo'
#
#"C:/Users/maxmo/PycharmProjects/TeReoDictonary-Assesment/TeReo"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = ("deeznutz42069")

#is_logged_in checks if there is an email it can grab to confirm user is logged in
def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

#is_teacher checks the account that is logged in permissions to see if it says "teacher"
def is_teacher():
    if session.get("permissions") == "teacher":
        print("is teacher")
        return True
    else:
        print("is not teacher")
        return False

#runs connection code for the database
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

#basic home page
@app.route('/')
def render_homepage():  # put application's code here
    if is_teacher():
        print("is teacher")
    return render_template('home.html', logged_in=is_logged_in(), is_teacher=is_teacher())

#after using search bar on home page this runs
@app.route('/search', methods=['GET', 'POST'])
def render_search():
    search = request.form['search'] #grabs requested search from user
    query = "SELECT maori, english, category, definition, level FROM Dictionary WHERE maori like ? OR english like ?  OR category like ? OR definition like ?  OR level like ?"
    search = "%" + search + "%"
    #above is the code checking the database for where is has to look
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search, search, search, search))
    definition_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('search.html', logged_in=is_logged_in(), definitions=definition_list, is_teacher=is_teacher())

#page that displays grid of words
@app.route('/words')
def render_words():  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level, editor FROM Dictionary" #grabing word information
    cur = con.cursor()
    cur.execute(query)
    definition_list = cur.fetchall()
    query = "SELECT id, category FROM categories" #this is grabing category names off a seperate database for the navbar
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('words.html', logged_in=is_logged_in(), definitions=definition_list, categories=category_list, is_teacher=is_teacher())

#displays grid for words in a category only
@app.route('/words/<category>')
def render_words_category(category):
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level, editor FROM Dictionary WHERE category=?" #the WHERE category=? is makeing it so only whatever category is = to is getting grabed by the database
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

#displays an individual word after clicking on it from the grid
@app.route('/<maori>')
def render_words_maori(maori):  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level, image, editor FROM Dictionary WHERE maori=?"
    cur = con.cursor()
    cur.execute(query, (maori, ))
    definition_list = cur.fetchall()
    query = "SELECT id, category FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('maori.html', logged_in=is_logged_in(), definitions=definition_list, categories=category_list, is_teacher=is_teacher())

#another oage for individual words that shows admin controls
@app.route('/<maori>/admin')
def render_words_maori_admin(maori):  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level FROM Dictionary WHERE maori=?"
    cur = con.cursor()
    cur.execute(query, (maori, ))
    definition_list = cur.fetchall()
    query = "SELECT id, category FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('maori_admin.html', logged_in=is_logged_in(), definitions=definition_list, categories=category_list, is_teacher=is_teacher())

#page to login to account
@app.route('/login', methods=['POST', 'GET'])
def render_login():  # put application's code here
    if is_logged_in():
        return redirect('/')
    print("logging in")
    if request.method == "POST": #POST means that we will be sending data to the database
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        print(email)
        query = """SELECT id, fname, lname, password, permission FROM user WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchone()
        con.close

        #checks that the email and password that were intered match with the one held in the database
        try:
            user_id = user_data[0]
            first_name = user_data[1]
            last_name = user_data[2]
            db_password = user_data[3]
            permissions = user_data[4]
        except IndexError:
            return redirect("/login?error=Email+or+invalid+password+incorrect")

        if not bcrypt.check_password_hash(db_password, password): #does a double check on the password checking if it matchs the incripted one held in the database
            return redirect(request.referrer, "?error=Email+or+invalid+password+inncorrect")

        # this is storeing the user info server side and not in the database so we can easily grabed it as they are logged in
        session['email'] = email
        session['firstname'] = first_name
        session['lastname'] = last_name
        session['user_id'] = user_id
        session['permissions'] = permissions

        print(session)
        return redirect('/')
    return render_template('login.html', is_teacher=is_teacher())

#page to make account
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

        #checks if the user put in the correct teacher code if not user gets redirected to try again, if let blank user is a student
        if permission == '1111':
            permission = 'teacher'
        elif permission == '':
            permission = 'student'
        else:
            return redirect("\signup?error=Teacher+code+incorrect")

        if password != password2:
            return redirect("\signup?error=Password+do+not+match")

        if len(fname) > 20:
            return redirect("\signup?error=fname+must+be+at+less+than+20+characters")
        if len(lname) > 20:
            return redirect("\signup?error=lname+must+be+at+less+than+20+characters")
        if len(email) > 320:
            return redirect("\signup?error=email+must+be+at+less+than+320+characters")
        if len(password) < 8:
            return redirect("\signup?error=Password+must+be+at+least+8+characters")
        if len(password) > 20:
            return redirect("\signup?error=Password+must+be+at+less+than+20+characters")


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

#page to logout
@app.route('/logout')
def logout():
    #session.pop is releasing the info we had on the user server side, logging them out
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=see+you+next+time!')

#page to access admin controlles
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

#page that allows the user to add a word to the full dictionary
@app.route("/add_word", methods=['POST'])
def add_word():
    if not is_logged_in():
        redirect('/?message=need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        #request.form.get is grabing the inputs from the html pages given by the user
        word_maori = request.form.get('maori')
        word_english = request.form.get('english')
        word_category = request.form.get('category')
        word_definition = request.form.get('definition')
        word_level = request.form.get('level')
        word_image = "noImage.jpg"
        word_editor = session.get("firstname")
        print(word_maori, word_english, word_category, word_definition, word_level,delete_word_confirm, word_editor)
        con = create_connection(DATABASE)
        #inserts all varibles given by user into the dictionary makeing a word
        query = "INSERT INTO Dictionary (maori, english, category, definition, level, image, editor) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (word_maori, word_english, word_category, word_definition, word_level, word_image, word_editor))
        con.commit()
        con.close()
        return redirect("/admin")

#page to delete words
@app.route('/delete_word/<maori>', methods=['POST'])
def delete_word(maori):
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    if request.method == "POST":
        maori = maori
        con = create_connection(DATABASE)
        query = "SELECT id FROM Dictionary WHERE maori=?" #this is grabing the primary key for the word to prepare to delete it
        cur = con.cursor()
        cur.execute(query, (maori,))
        word = cur.fetchone()
        con.close()
        return render_template("delete_confirm.html", word=word)
    return redirect("/admin")

#confrims with user they want to delete a word and then deletes it
@app.route('/delete_word_confirm/<maori>')
def delete_word_confirm(maori):
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "DELETE FROM Dictionary WHERE id = ?" #deletes the priamry key given by the last page only
    temp_word_id = int(maori)
    cur = con.cursor()
    cur.execute(query, (temp_word_id, ))
    con.commit()
    con.close()
    print("below is: word details")
    print(maori)
    print(temp_word_id)
    return redirect("/words")

#lets user add new category (same as add word just for category)
@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        category = request.form.get('name').lower().strip()
        print(category)
        con = create_connection(DATABASE)
        query = "INSERT INTO categories ('category') VALUES (?)"
        cur = con.cursor()
        cur.execute(query, (category, ))
        con.commit()
        con.close()
        return redirect("/admin")

#lets user delete a category (same as delete word just for category)
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
        return render_template("delete_cat_confirm.html", id=cat_id, name=cat_name, type="category")
    return redirect("/admin")

#confrims with user they want to delete a category and then deletes it (same as delete word confirm)
@app.route('/delete_category_confirm/<id>')
def delete_category_confirm(id):
    if not is_logged_in():
        return redirect('/?message=need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "DELETE FROM categories WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (id, ))
    con.commit()
    con.close()
    return redirect("/admin")

if __name__ == '__main__':
    app.run()
