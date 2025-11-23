from flask import Flask, render_template

app = Flask(__name__)


DB_TABLES = [
    "Appearances",
    "club_games",
    "clubs",
    "competitions",
    "players",
    "playervaluations"
]


@app.route('/')
def index():
    return render_template('index.html', tables=DB_TABLES)


@app.route('/table/<table_name>')
def show_table(table_name):

    if table_name not in DB_TABLES:
        return "Table not found", 404

    return render_template('table.html', table_name=table_name)


@app.route('/table/<table_name>/add')
def add_record(table_name):
    if table_name not in DB_TABLES:
        return "Table not found", 404
    return f"<h1>Add to {table_name} table</h1>"


if __name__ == '__main__':
    app.run(debug=True)