from tinydb import TinyDB, where, Query
import json
import random
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
from collections import defaultdict
from operator import itemgetter

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

db = TinyDB('data/db.json')
plots_db = db.table('plots')
links_db = db.table('links')

Group = Query()

@app.route('/plot/link', methods=['POST'])
def plot_link():
    #records a link for a plot and station
    data = request.get_json()
    print(data)
    links_db.insert({
        'action': 'link',
        'book_id': data['book_id'],
        'plot_id': data['plot_id'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    resp = plots_db.search(where('plot_id') == data['plot_id'])
    print(resp)
    return jsonify({})


@app.route('/plot/unlink', methods=['POST'])
def plot_unlink():
    #records an unlink for a plot and station
    data = request.get_json()
    print(data)
    links_db.insert({
        'action': 'unlink',
        'book_id': data['book_id'],
        'plot_id': data['plot_id'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    resp = plots_db.search(where('plot_id') == data['plot_id'])
    print(resp)
    return jsonify({})


@app.route('/plot/books_linked/<plotid>')
def plot_books_linked(plotid):
    resp = links_db.search(where('plot_id') == plotid)
    books = [{"book_id": bid} for bid in set([link['book_id'] for link in resp])]
    return jsonify(books)

@app.route('/plot/rename', methods=['POST'])
def plot_rename():
    #records a addtoplot for a plot and station
    # save new book ids
    data = request.get_json()
    print(data)
    plots_db.insert({
        'plot_id': data['plot_id'],
        'plot_name': data['plot_name'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    resp = plots_db.search(where('plot_id') == data['plot_id'])
    print(resp)
    return jsonify({})


def plot_names():
    #returns all plots & their checkouts
    result = sorted(plots_db.all(), key=itemgetter('timestamp'), reverse=True)

    plots = {}
    for r in result:
        if r['plot_id'] not in plots:
            plots[r['plot_id']] = r
    # could there not be some functional way to do this?

    return plots

@app.route('/plot/names')
def plot_names_route():
    return jsonify(plot_names())


def plot_all():
    plots = defaultdict(lambda: defaultdict(dict))
    plotnames = plot_names()

    # could there not be some functional way to do this?

    # replay the linking/unlinking
    for l in sorted(links_db.all(), key=itemgetter('timestamp')):
        this_pid = l['plot_id']
        this_bid= l['book_id']

        if(l['action'] == "link"):
            plots[this_pid]["links"][this_bid] = l

        if(l['action'] == "unlink"):
            if (this_pid in plots) and (this_bid in plots[this_pid]["links"]):
                plots[this_pid]["links"].pop(this_bid)


    # add names
    for pid in plots:
        if pid in plotnames:
            plots[pid]["name"] = plotnames[pid]

    return plots

@app.route('/plot/all')
def plot_all_route():
    return jsonify(plot_all())




@app.route('/book/<book_id>', methods=['GET'])
def book(book_id):
    resp = links_db.search(where('book_id') == book_id)
    data = {}
    data["plots"] = list(set([link['plot_id'] for link in resp]))
    return jsonify(data)



# this is a public-facing url -- aka printed on the QR code
@app.route('/plot/<plotid>')
def plot_page(plotid):
    #forward to plot page because plot QR codes have this URL embedded in them 
    return render_template('plot.html', plotid=plotid)





