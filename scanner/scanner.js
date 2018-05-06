$(document).ready(function() {

  window.thisbook = "";

  var sounds_dir = "wavs/";
  var sounds_meow = ["meow1.wav", "meow2.wav", "meow3.wav", "meow4.wav", "meow5.mp3", "meow6.wav", "meow7.mp3", "meow8.wav", "meow9.wav", "meow10.wav",
    "meow11.wav", "meow12.wav", "meow13.wav", "meow14.wav", "meow15.mp3", "meow16.mp3"
  ];
  var sounds_bell = ["idea.wav"];

  window.prevlink = {};

  function hashCode(str) {
    var hash = 0;
    if (str.length == 0) return hash;
    for (i = 0; i < str.length; i++) {
      char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
  }


  function isBook(s) {
//    console.log(s);
    if (s.includes('checkout') || s.includes('object')) {
//      console.log("BOOK");
      return true;
    } else {
      //console.log("PLOT");
      return false;
    }
  }

  window.isBook = isBook;

  function isName(s) {
    return !isBook(s);
  }

  function urlToId(s) {
    return s.split("/")[s.split("/").length - 1];
  }
  window.urlToId = urlToId;

  function parseQR(content) {
    var res = {};
    res.books = {};
    res.names = {};
    res.type = {};


    content.forEach(function(d, i) {
      if (isBook(d)) {
        res.books[urlToId(d)] = d;
        res.type = "book";
//        console.log(res.type);
      }
      if (isName(d)) {
        res.names[urlToId(d)] = d;
        res.type = "name";
//            console.log(res.type);
      }
    });
    return res;
  }

  function handleScans(content) {
    /* see what's in the scans, how many we have
     and decide what to do */

    if(content.length == 2) {
      if(isBook(content[0]) && isName(content[1])) {  makeLink(content); }
      if(isBook(content[1]) && isName(content[0])) { makeLink(content);  }
    }
  }

  function makeLink(content) {
    var res = parseQR(content);
    if(!(_.isEqual(window.prevlink, res))) {
      window.prevlink = res;
      console.log(res);
      console.log("MADEL INK!!!");
      submitLinkToApi(res);
    }
  }

  function submitLinkToApi(res) {
    //plot/link [POST]: Link a plot to a book. Needs book_id, plot_id, station_id, timestamp.
    window.restest = res;
    var bookid = urlToId(res.books[Object.keys(res.books)[0]]);
    var plotid = urlToId(res.names[Object.keys(res.names)[0]]);
    var apiurl = "https://library.cybernetics.social/plot/link";
    var data = {
      'book_id':  bookid,
      'plot_id':  plotid,
      'station_id': "webscanner",
      'timestamp': new Date().getTime() / 1000
    };
    console.log(data);
    $.ajax({
      type: "POST",
      url: apiurl,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      dataType: "json",
      success: function(res) {
        console.log(res);
        console.log("successfully linked!")
        displayModal()
      }
    });



  }


  function displayModal() {
    $("#link_success").fadeIn(400).delay(2000).fadeOu(300);
  }

  function updateIframe(content) {
    var tinycaturl = "https://www.librarycat.org/lib/CyberneticsCon/item/";

    var res = parseQR(content);
    window.res = res;
    //
    // if (window.res.type = "book") {
    //   console.log("This is a book");
    //   objNames = window.res.names;
    // } else {
    //   console.log("this is a plot");
    // }
    // console.log(window.res);


    // console.log(objNames);



    // var url = objNames[Object.keys(objNames)[0]];
    // console.log("url: " + url);

    ///////////////////////////////////////

    var thisbookids = Object.keys(res.books).sort()

    var thisbooks = thisbookids.join("+");
    if ((thisbooks) && (window.prevbooks != thisbooks)) {

      var s = "";
      s += "\nBOOKs = " + thisbookids.join(", ");
      s += "\nNAMEs = " + Object.keys(res.names).join(", ");
      $("#output").html(s);

      // console.log(s);
      $("#iframe").attr("src", "https://www.librarycat.org/lib/CyberneticsCon/item/" + thisbookids[0]);
      window.prevbooks = thisbooks;
      sound = sounds_meow[hashCode(thisbookids[0]) % sounds_meow.length]
      //          var sound = _.sample(sounds_meow);
      var sound = _.sample(sounds_meow);
      var snd = new Audio(sounds_dir + sound); // buffers automatically when created
      snd.play();
    }
  }





  let scanner = new Instascan.Scanner({
    video: document.getElementById('preview')
  });
  scanner.addListener('scan', function(content) {
    handleScans(content)
    updateIframe(content);
  });
  Instascan.Camera.getCameras().then(function(cameras) {
    if (cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error('No cameras found.');
    }
  }).catch(function(e) {
    console.error(e);
  });


});
