var poemgen = {};

poemgen.createPoem = function(data) {

  window.ddd = data;
  var s = ""
  var thismem = _.sample(data.memories)
  console.log(thismem);

  var poemarr = []
  var poems = ""
  
  for(let i = 0; i < 10; i++) {

    //s += thismem.memory + " -- " + thismem.book_id + "(" + data.books[thismem.book_id]['title'] + ", "
    poemarr.push(thismem.memory_from)
    s += thismem.memory_from + ", "
    if(i % 2 == 0) {
      var other_memories_by_same_book = _.filter(data.memories, {book_id:thismem.book_id})
      thismem = _.sample(other_memories_by_same_book)
    } else {
      var other_memories_by_same_memory= _.filter(data.memories, {memory:thismem.memory_from})
      thismem = _.sample(other_memories_by_same_memory)
    }
    if(thismem === undefined) {
      s += ";\n"
       thismem = _.sample(data.memories);
    }
    if(poemarr.length == 2) {
      poems += poemgen.tracepoem(poemarr) + "<br />";
      poemarr = [];
    }
  }

  console.log(s);
  return poems.replace(/[^a-zA-Z0-9]+$/g, "") + ".";
//  return s;
}

poemgen.tracery = function(data) {
    poemgen.grammar = tracery.createGrammar(poemgen.grammarSource);
    return poemgen.grammar.flatten("#greeting#");
}

poemgen.boo = function() {
  console.log("Fdfsd");
}

poemgen.tracepoem = function(poemarr) {
  console.log(poemarr);
  var narrator= poemarr[0]
  var subject  = poemarr[1]
  var grammarSource = {
    "narrator": poemarr[0],
    "subject": poemarr[1],
    "wonderadj": "quiet|solemn|contemplative|still|tender|harmonious".split("|"),
    "name": "fire|bother|wonder|winter".split("|"),
    "verbs": "dances around|thinks about|touches with|dreams of".split("|"),
    "lineending": ['','',',',';','--','.'],
    "poem": "#wonderadj# #narrator# #verbs# #subject##lineending#"
  }
  return tracery.createGrammar(grammarSource).flatten("#poem#");
}

poemgen.grammarSource = {
  "name": "fire|bother|wonder|winter".split("|"),
  "greeting": "hi #name#, how are you?"
}
poemgen.boo = function() {
  console.log("Fdfsd");
}

poemgen.grammarSource = {
  "name": "fire|bother|wonder|winter".split("|"),
  "greeting": "hi #name#, how are you?"
}
