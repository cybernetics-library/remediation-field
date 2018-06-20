var poemgen = {};

poemgen.createPoem = function(data) {

  window.ddd = data;
  var s = ""
  var thismem = _.sample(data.memories)
  console.log(thismem);
  for(let i = 0; i < 20; i++) {

    //s += thismem.memory + " -- " + thismem.book_id + "(" + data.books[thismem.book_id]['title'] + ", "
    s += thismem.memory_from + " -> "
    if(i % 2 == 0) {
      var other_memories_by_same_book = _.filter(data.memories, {book_id:thismem.book_id})
      thismem = _.sample(other_memories_by_same_book)
    } else {
      var other_memories_by_same_memory= _.filter(data.memories, {memory:thismem.memory_from})
      thismem = _.sample(other_memories_by_same_memory)
    }
  }

  return s
}

poemgen.boo = function() {
  console.log("Fdfsd");
}
