from tinydb import TinyDB, where, Query
import json
import random
from .db import DB
from .monuments import compute_monuments_state
from .pp import compute_pp_state
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
from .params import MONUMENT_NAMES, TOPICS
from colorhash import ColorHash
from collections import defaultdict
from .planets import name_from_id

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)
db = {
    table: DB(table)
    for table in ['checkouts']
}

plot_db = TinyDB('data/plot_db.json')
Group = Query()

@app.route('/book/<book_id>', methods=['GET'])
def book(book_id):
    resp = plot_db.search(where('book_id') == book_id)
    print(resp)


@app.route('/add_to_plot', methods=['POST'])
def addtoplot():
    #records a addtoplot for a plot and station
    # save new book ids
    data = request.get_json()
    print(data)
    plot_db.insert({
        'book_id': data['book_id'],
        'plot_id': data['plot_id'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    resp = plot_db.search(where('plot_id') == data['plot_id'])
    print(resp)
    return jsonify({})


@app.route('/books_in_plot/<plotid>')
def books_in_plot(plotid):
    resp = plot_db.search(where('plot_id') == plotid)
    books = [{"book_id": b} for b in set([c['book_id'] for c in resp])]
    return jsonify(books)


@app.route('/plots')
def plots():
    #returns all plots & their checkouts
    resp = plot_db.search(where('plot_id') == plotid)

    return jsonify(**plots)


# this is a public-facing url -- aka printed on the QR code
@app.route('/plot/<plotid>')
def plot_page(plotid):
    #forward to plot page because plot QR codes have this URL embedded in them 
    return render_template('plot.html', plotid=plotid)





