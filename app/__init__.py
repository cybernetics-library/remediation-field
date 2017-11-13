import json
import random
from .db import DB
from .monuments import compute_monuments_state
from .pp import compute_pp_state
from flask import Flask, request, jsonify
from flask_cors import CORS
from .params import MONUMENT_NAMES
from colorhash import ColorHash
from collections import defaultdict

app = Flask(__name__)
CORS(app)
db = {
    table: DB(table)
    for table in ['checkouts']
}
LIBRARY = json.load(open('data/library.json', 'r'))


def get_questions(id):
    book = LIBRARY['books'][id]
    questions = book.get('questions')

    # if no questions for this book,
    # get questions for its topics
    if questions is None:
        topics = book['topics']
        questions = []
        for t in topics:
            questions.extend(LIBRARY['questions'][t])
    return questions


def sum_dicts(*dicts):
    sum = defaultdict(int)
    for d in dicts:
        for k, v in d.items():
            sum[k] += v
    return sum



def mix_topics(*topic_mixtures):
    """compute aggregate topic mixture"""
    topic_mixture = sum_dicts(*topic_mixtures)
    total = sum(topic_mixture.values())
    return {t: v/total for t, v in topic_mixture}



@app.route('/checkout/<id>', methods=['POST'])
def checkout(id):
    """records a checkout for a attendee and station"""
    # save new book ids
    data = request.json()
    db['checkouts'].append({
        'book_id': id,
        'attendee_id': data['attendee_id'],
        'station_id': data['station_id']
    })

    # return book info
    book = LIBRARY['books'][id]
    return jsonify(**book)


@app.route('/planets/<id>')
def planet(id):
    """returns attendee checkout planet info"""
    # get topic mixtures for books attendee has checked out
    topic_mixtures = []
    for checkout in db['checkouts'].all():
        if checkout['attendee_id'] == id:
            book_id = checkout['book_id']
            topic_mixture = LIBRARY['books'][book_id]['topics']
            topic_mixtures.append(topic_mixture)

    color = ColorHash(id)
    topic_mixture = mix_topics(*topic_mixtures)
    return jsonify(color=color.hex, topic_mixture=topic_mixture)


@app.route('/planets')
def planets():
    """returns checkout planet info for all attendees"""
    planets = defaultdict(lambda: {'topic_mixture': []})
    for checkout in db['checkouts'].all():
        book_id = checkout['book_id']
        topic_mixture = LIBRARY['books'][book_id]['topics']
        planets[checkout['attendee_id']]['topic_mixture'].append(topic_mixture)

    for id, d in planets.items():
        d['topic_mixture'] = mix_topics(*d['topic_mixture'])
        d['color'] = ColorHash(id).hex
    return jsonify(**planets)


@app.route('/books')
def books():
    """returns checked-out book ids"""
    return jsonify(checkouts=list(db['checkouts'].all()))


@app.route('/question')
def question():
    """returns a question based on what has been checked out"""
    questions = []
    for id in set(db['checkouts'].all()):
        questions.extend(get_questions(id))
    questions = list(set(questions))
    if questions:
        question = random.choice(questions)
    else:
        question = 'Hmm...'
    return jsonify(question=question)


@app.route('/questions/<id>')
def questions(id):
    """returns questions given a book id"""
    questions = get_questions(id)
    return jsonify(questions=questions)


@app.route('/monuments')
def monuments():
    state = db['monuments'].last()
    if state is None:
        state = compute_monuments_state([])
    return jsonify(state=state, names=MONUMENT_NAMES)


@app.route('/pp', methods=['GET', 'POST'])
def pp():
    """
    if request.method == 'POST':
        pp_state = request.form
        db['pp'].append(pp_state)
        return jsonify(**pp_state)
    """
    if request.method == 'GET':
        mstate = db['monuments'].last()
        if mstate is None:
            mstate = compute_monuments_state([])
        pp_state = compute_pp_state(mstate)
        return jsonify(**pp_state)

