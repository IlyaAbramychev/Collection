from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='templates')

# Пример данных для статей
articles = [
    {'id': 1, 'title': 'Статья 1', 'summary': 'Краткое описание статьи 1'},
    {'id': 2, 'title': 'Статья 2', 'summary': 'Краткое описание статьи 2'},
    {'id': 3, 'title': 'Статья 3', 'summary': 'Краткое описание статьи 3'},
]

@app.route('/')
def index():
    return render_template('index.html', recommended_articles=articles[:2], latest_articles=articles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверка логина и пароля
        # ...
        return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)