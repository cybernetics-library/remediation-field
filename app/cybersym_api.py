import json
from .db import DB


def setup():
    global db, LIBRARY
    db = {
        table: DB(table)
        for table in ['checkouts']
    }
    LIBRARY = json.load(open('data/library.json', 'r'))
    # add missing topics as 0
    for id, book in LIBRARY['books'].items():
        for t in TOPICS:
            book['topics'][t] = book['topics'].get(t, 0)



def checkout(id):
    if request.method == 'GET':
        return render_template('book.html', id=id)
        #return redirect("http://www.example.com?id=" + id, code=302)
    else:
        """records a checkout for a attendee and station"""
        # save new book ids
        data = request.get_json()
        db['checkouts'].append({
            'book_id': id,
            'attendee_id': data['attendee_id'],
            'station_id': data['station_id'],
            'timestamp': data['timestamp']
        })

        if(id) in LIBRARY['books']:
            # return book info
            book = LIBRARY['books'][id]
            return jsonify(**book)


def planet(id):
    """returns attendee checkout planet info"""
    # get topic mixtures for books attendee has checked out
    checkouts = []
    topic_mixtures = []
    for checkout in db['checkouts'].all():
        if checkout['attendee_id'] == id:
            book_id = checkout['book_id']
            book = LIBRARY['books'][book_id]
            topic_mixture = book['topics']
            topic_mixtures.append(topic_mixture)
            checkout['topics'] = book['topics']
            checkout['title'] = book['title']
            checkouts.append(checkout)

    color = ColorHash(id)
    topic_mixture = mix_topics(*topic_mixtures)
    return jsonify(
        color=color.hex,
        checkouts=checkouts,
        topic_mixture=topic_mixture,
        name=name_from_id(id)
    )

def planets():
    """returns checkout planet info for all attendees"""
    planets = defaultdict(lambda: {'topic_mixture': [], 'checkouts': 0})
    for checkout in db['checkouts'].all():
        book_id = checkout['book_id']
        topic_mixture = LIBRARY['books'][book_id]['topics']
        planets[checkout['attendee_id']]['topic_mixture'].append(topic_mixture)
        planets[checkout['attendee_id']]['checkouts'] += 1

    for id, d in planets.items():
        d['topic_mixture'] = mix_topics(*d['topic_mixture'])
        d['color'] = ColorHash(id).hex
        d['name'] = name_from_id(id)
    return jsonify(**planets)


