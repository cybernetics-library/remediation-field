from tinydb import TinyDB, where
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


@app.route('/book/<id>', methods=['GET'])
def book(id):
    if(id) in LIBRARY['books']:
        # return book info
        book = LIBRARY['books'][id]
        return jsonify(**book)


@app.route('/addtoplot', methods=['POST'])
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



@app.route('/plots')
def plots():
    #returns checkout planet info for all attendees
    plots = defaultdict(lambda: {'topic_mixture': [], 'checkouts': 0})
    for checkout in db['checkouts'].all():
        book_id = checkout['book_id']
        topic_mixture = LIBRARY['books'][book_id]['topics']
        plots[checkout['attendee_id']]['topic_mixture'].append(topic_mixture)
        plots[checkout['attendee_id']]['checkouts'] += 1

    for id, d in plots.items():
        d['topic_mixture'] = mix_topics(*d['topic_mixture'])
        d['color'] = ColorHash(id).hex
        d['name'] = name_from_id(id)
    return jsonify(**plots)


@app.route('/plot/<plotid>')
def plot_page(plotid):
    #forward to plot page because plot QR codes have this URL embedded in them 
    return render_template('plot.html', plotid=plotid)





