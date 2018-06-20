var poemgen = {};

poemgen.createPoem = function(data) {

  var s = ""
  var thismem = _.sample(data)
  for(let i = 0; i < 10; i++) {
    s += thismem.memory + ", "
    var other_books_by_this = _.filter(data, {book_id:thismem.book_id})
    thismem = _.sample(other_books_by_this)
  }

  return s
}

poemgen.boo = function() {
  console.log("Fdfsd");
}


