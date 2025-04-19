from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Normally, this should be a random secret

# Simulated user database
users = {}
todos = {}

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('todo.html', todos=todos.get(username, []))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users[username] = password
        # Initialize todo list for the new user
        todos[username] = []
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_todo', methods=['POST'])
def add_todo():
    if 'username' in session:
        todo = request.form['todo']
        username = session['username']
        todos[username].append(todo)
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)