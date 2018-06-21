from tinydb import TinyDB, where, Query
import json
import random
import requests
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
from collections import defaultdict
from operator import itemgetter
import copy
from flask_socketio import SocketIO, emit, send


#import cybersym_api


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)
socketio = SocketIO(app)


db = TinyDB('data/db.json')
plots_db = db.table('plots')
links_db = db.table('links')

memories_tinydb = TinyDB('data/memories_db.json', indent=4)
memories_db = memories_tinydb.table('memories')

poems_tinydb = TinyDB('data/poems_db.json', indent=4)
poems_db = poems_tinydb.table('poems')

Group = Query()

collection_name = 'Your library'

# utility for getting books from library thing and filtering by collection
def fetch_lib_thing(collection_name):
    lib_thing = requests.get("http://www.librarything.com/api_getdata.php?userid=cyberneticscon&showstructure=1&max=1000&showTags=10&booksort=title_REV&showCollections=1&responseType=json").json()['books']

    flat_lib_thing = [v for k,v in lib_thing.items()]

    def filter_dict_list(dictlist, key, value):
        return [d for d in dictlist if value in d[key].values()]

    lib_collection = filter_dict_list(flat_lib_thing, 'collections', collection_name)

    return lib_collection


# run book fetch on startup
lib_collection = fetch_lib_thing(collection_name)


# fetch from Library Thing, replace global variable & return current dictionary
@app.route('/fetch_thing', methods=['GET'])
def fetch_thing():
    global lib_collection
    lib_collection = fetch_lib_thing(collection_name)
    return jsonify(lib_collection)


@app.route('/collection_from_libthing', defaults={'collectionid': 'all'})
@app.route('/collection_from_libthing/<collectionid>')
def collection_from_libthing(collectionid):
    collectionurl = "https://www.librarything.com/catalog_bottom.php?view=CyberneticsCon&printable=1&collectionid=" + collectionid
    print(collectionurl)
    lib_thing = requests.get(collectionurl)
    print(lib_thing)

# return existing Libary Thing dictionary without fetch
@app.route('/book', methods=['GET'])
def all_books():
    #resp = links_db.all()
    #books = replay_books(resp)
    global lib_collection
    if lib_collection is None:
        lib_collection = []
    return jsonify(lib_collection)


@app.route('/book/<book_id>', methods=['GET'])
def books_one(book_id):
    #resp = links_db.search(where('book_id') == book_id)
    #books = replay_books(resp)
    book = filter(lambda d: d['book_id'] == book_id, lib_collection)
    return jsonify(book)


@app.route('/plot/link', methods=['POST'])
def plot_link():
    #records a link for a plot and station
    print(request.data)
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


app.route('/plot/rename', methods=['POST'])
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

def replay_plots(links):
    plots = defaultdict(lambda: defaultdict(dict))
    plotnames = plot_names()

    # could there not be some functional way to do this?

    # replay the linking/unlinking
    for link in sorted(links, key=itemgetter('timestamp')):
        l = copy.deepcopy(link)
        this_pid = l['plot_id']
        this_bid= l['book_id']

        if(l['action'] == "link"):
            plots[this_pid]["books"][this_bid] = l

        if(l['action'] == "unlink"):
            if (this_pid in plots) and (this_bid in plots[this_pid]["books"]):
                plots[this_pid]["books"].pop(this_bid)

    # add names
    for pid in plots:
        if pid in plotnames:
            plots[pid]["name"] = plotnames[pid]

    # remove 'action' key/value because it's confusing and will always be 'link'
    for pid in plots:
        for bid in plots[pid]['books']:
            plots[pid]['books'][bid].pop('action', None)

    return plots



@app.route('/plot/')
def plot_all_route():
    resp = links_db.all()
    return jsonify(replay_plots(resp))


@app.route('/plot/<plotid>')
def plot_books_linked(plotid):
    resp = links_db.search(where('plot_id') == plotid)
    return jsonify(replay_plots(resp))


def replay_books(links):
    books = defaultdict(lambda: defaultdict(dict))

    # replay the linking/unlinking
    for link in sorted(links, key=itemgetter('timestamp')):
        l = copy.deepcopy(link)
        this_pid = l['plot_id']
        this_bid= l['book_id']

        if(l['action'] == "link"):
            books[this_bid]["plots"][this_pid] = l

        if(l['action'] == "unlink"):
            if (this_bid in books) and (this_pid in books[this_bid]["plots"]):
                books[this_bid]["plots"].pop(this_pid)

    for bid in books:
        books[bid]['attributes'] = {}

    for bid in books:
        for pid in books[bid]['plots']:
            books[bid]['plots'][pid].pop('action', None)

    return books


# this is a public-facing url -- aka printed on the QR code
@app.route('/plots/<plotid>')
def plot_page(plotid):
    #forward to plot page because plot QR codes have this URL embedded in them 
    return render_template('plot.html', plotid=plotid)


"""
######### LEGACY API
cybersym_api.setup()

@app.route('/checkout/<id>', methods=['POST', 'GET'])
def cybersym_checkout(id):
    return cybersym_api.checkout(id)

@app.route('/planets/<id>')
def cybersym_planet(id):
    return cybersym_api.planet(id)

@app.route('/planets')
def cybersym_planets(id):
    return cybersym_api.planets(id)
"""


@app.route('/connect_book_to_memory', methods=['POST'])
def connect_book_to_memory():
    if (request.is_json):
        data = request.get_json(force=True)
    else:
        data = {k:v for k, v in request.form.items()}

    # bookid, memorystring, theme)
    memories_db.insert({
        'action': 'connect',
        'book_id': data['book_id'],
        'memory_from': data['memory_from'],
        'memory_to': data['memory_to'],
        'theme': data['theme'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    socketio.emit('newdata', {}, namespace="/socket")
    return jsonify({})

@app.route('/poem/save', methods=['POST'])
def save_poem():
    if (request.is_json):
        data = request.get_json(force=True)
    else:
        data = {k:v for k, v in request.form.items()}

    poems_db.insert({
        'poem': 'poem',
        'timestamp': data['timestamp']
    })

    return jsonify({})

@app.route('/memories/dump')
def get_memories_dump():
    resp = memories_db.all()
    sorteddump = sorted(resp, key=lambda k: k['timestamp']) 

    return jsonify(sorteddump)

@app.route('/memories/unique')
def get_memories_unique():
    resp = memories_db.all()
    dump = sorted(resp, key=lambda k: k['timestamp']) 
    memories_to = list(set([m['memory_to'] for m in dump]))
    memories_from = list(set([m['memory_from'] for m in dump]))

    returndata = {}
    returndata['memories_to'] = memories_to
    returndata['memories_from'] = memories_from
    returndata['memories_all'] = list(set(memories_from + memories_to))

    return jsonify(returndata)

    
@app.route('/memories/by/<bykey>')
def get_memories_by(bykey):
    print(bykey)
    data = memories_db.all()

    if(bykey not in data[0]):
        return jsonify({ "error": "key does not exist in db!" })
    else:
        res = defaultdict(list)
        for d in data:
            res[d[bykey]].append(d)
        return jsonify(res)


@app.route('/refresh')
def refresh():
    socketio.emit('refresh', {}, namespace="/socket")
    return jsonify({})

memories_tinydb = TinyDB('data/memories_db.json', indent=4)
memories_db = memories_tinydb.table('memories')

Group = Query()

collection_name = 'Your library'

# utility for getting books from library thing and filtering by collection
def fetch_lib_thing(collection_name):
    lib_thing = requests.get("http://www.librarything.com/api_getdata.php?userid=cyberneticscon&showstructure=1&max=1000&showTags=10&booksort=title_REV&showCollections=1&responseType=json").json()['books']

    flat_lib_thing = [v for k,v in lib_thing.items()]

    def filter_dict_list(dictlist, key, value):
        return [d for d in dictlist if value in d[key].values()]

    lib_collection = filter_dict_list(flat_lib_thing, 'collections', collection_name)

    return lib_collection


# run book fetch on startup
lib_collection = fetch_lib_thing(collection_name)


# fetch from Library Thing, replace global variable & return current dictionary
@app.route('/fetch_thing', methods=['GET'])
def fetch_thing():
    global lib_collection
    lib_collection = fetch_lib_thing(collection_name)
    return jsonify(lib_collection)


@app.route('/collection_from_libthing', defaults={'collectionid': 'all'})
@app.route('/collection_from_libthing/<collectionid>')
def collection_from_libthing(collectionid):
    collectionurl = "https://www.librarything.com/catalog_bottom.php?view=CyberneticsCon&printable=1&collectionid=" + collectionid
    print(collectionurl)
    lib_thing = requests.get(collectionurl)
    print(lib_thing)

# return existing Libary Thing dictionary without fetch
@app.route('/book', methods=['GET'])
def all_books():
    #resp = links_db.all()
    #books = replay_books(resp)
    global lib_collection
    if lib_collection is None:
        lib_collection = []
    return jsonify(lib_collection)


@app.route('/book/<book_id>', methods=['GET'])
def books_one(book_id):
    #resp = links_db.search(where('book_id') == book_id)
    #books = replay_books(resp)
    book = filter(lambda d: d['book_id'] == book_id, lib_collection)
    return jsonify(book)


@app.route('/plot/link', methods=['POST'])
def plot_link():
    #records a link for a plot and station
    print(request.data)
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


app.route('/plot/rename', methods=['POST'])
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

def replay_plots(links):
    plots = defaultdict(lambda: defaultdict(dict))
    plotnames = plot_names()

    # could there not be some functional way to do this?

    # replay the linking/unlinking
    for link in sorted(links, key=itemgetter('timestamp')):
        l = copy.deepcopy(link)
        this_pid = l['plot_id']
        this_bid= l['book_id']

        if(l['action'] == "link"):
            plots[this_pid]["books"][this_bid] = l

        if(l['action'] == "unlink"):
            if (this_pid in plots) and (this_bid in plots[this_pid]["books"]):
                plots[this_pid]["books"].pop(this_bid)

    # add names
    for pid in plots:
        if pid in plotnames:
            plots[pid]["name"] = plotnames[pid]

    # remove 'action' key/value because it's confusing and will always be 'link'
    for pid in plots:
        for bid in plots[pid]['books']:
            plots[pid]['books'][bid].pop('action', None)

    return plots



@app.route('/plot/')
def plot_all_route():
    resp = links_db.all()
    return jsonify(replay_plots(resp))


@app.route('/plot/<plotid>')
def plot_books_linked(plotid):
    resp = links_db.search(where('plot_id') == plotid)
    return jsonify(replay_plots(resp))


def replay_books(links):
    books = defaultdict(lambda: defaultdict(dict))

    # replay the linking/unlinking
    for link in sorted(links, key=itemgetter('timestamp')):
        l = copy.deepcopy(link)
        this_pid = l['plot_id']
        this_bid= l['book_id']

        if(l['action'] == "link"):
            books[this_bid]["plots"][this_pid] = l

        if(l['action'] == "unlink"):
            if (this_bid in books) and (this_pid in books[this_bid]["plots"]):
                books[this_bid]["plots"].pop(this_pid)

    for bid in books:
        books[bid]['attributes'] = {}

    for bid in books:
        for pid in books[bid]['plots']:
            books[bid]['plots'][pid].pop('action', None)

    return books


# this is a public-facing url -- aka printed on the QR code
@app.route('/plots/<plotid>')
def plot_page(plotid):
    #forward to plot page because plot QR codes have this URL embedded in them 
    return render_template('plot.html', plotid=plotid)


"""
######### LEGACY API
cybersym_api.setup()

@app.route('/checkout/<id>', methods=['POST', 'GET'])
def cybersym_checkout(id):
    return cybersym_api.checkout(id)

@app.route('/planets/<id>')
def cybersym_planet(id):
    return cybersym_api.planet(id)

@app.route('/planets')
def cybersym_planets(id):
    return cybersym_api.planets(id)
"""


@app.route('/connect_book_to_memory', methods=['POST'])
def connect_book_to_memory():
    if (request.is_json):
        data = request.get_json(force=True)
    else:
        data = {k:v for k, v in request.form.items()}

    # bookid, memorystring, theme)
    memories_db.insert({
        'action': 'connect',
        'book_id': data['book_id'],
        'memory_from': data['memory_from'],
        'memory_to': data['memory_to'],
        'theme': data['theme'],
        'station_id': data['station_id'],
        'timestamp': data['timestamp']
    })

    socketio.emit('newdata', {}, namespace="/socket")
    return jsonify({})

@app.route('/poem/save', methods=['POST'])
def save_poem():
    if (request.is_json):
        data = request.get_json(force=True)
    else:
        data = {k:v for k, v in request.form.items()}

    poems_db.insert({
        'poem_text': 'poem_text',
        'timestamp': data['timestamp']
    })

    return jsonify({})

@app.route('/memories/dump')
def get_memories_dump():
    resp = memories_db.all()
    sorteddump = sorted(resp, key=lambda k: k['timestamp']) 

    return jsonify(sorteddump)

@app.route('/memories/unique')
def get_memories_unique():
    resp = memories_db.all()
    dump = sorted(resp, key=lambda k: k['timestamp']) 
    memories_to = list(set([m['memory_to'] for m in dump]))
    memories_from = list(set([m['memory_from'] for m in dump]))

    returndata = {}
    returndata['memories_to'] = memories_to
    returndata['memories_from'] = memories_from
    returndata['memories_all'] = list(set(memories_from + memories_to))

    return jsonify(returndata)

    
@app.route('/memories/by/<bykey>')
def get_memories_by(bykey):
    print(bykey)
    data = memories_db.all()

    if(bykey not in data[0]):
        return jsonify({ "error": "key does not exist in db!" })
    else:
        res = defaultdict(list)
        for d in data:
            res[d[bykey]].append(d)
        return jsonify(res)


@app.route('/refresh')
def refresh():
    socketio.emit('refresh', {}, namespace="/socket")
    return jsonify({})

