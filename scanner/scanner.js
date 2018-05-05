$(document).ready(function() {

  window.thisbook = "";

  var sounds_dir = "wavs/";
  var sounds_meow = ["meow1.wav", "meow2.wav", "meow3.wav", "meow4.wav", "meow5.mp3", "meow6.wav", "meow7.mp3", "meow8.wav", "meow9.wav", "meow10.wav",
    "meow11.wav", "meow12.wav", "meow13.wav", "meow14.wav", "meow15.mp3", "meow16.mp3"
  ];
  var sounds_bell = ["idea.wav"];

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
    if (s.match(/\d\d\d\d\d\d\d\d/)) {
      return true
    } else {
      return false;
    }
  }

  function isName(s) {
    return !isBook(s);
  }

  function bookUrlToId(s) {
    return s.split("/")[s.split("/").length - 1];
  }

  function parseQR(content) {
    var res = {};
    res.books = {};
    res.names = {};
    content.forEach(function(d, i) {
      if (isBook(d)) {
        res.books[bookUrlToId(d)] = d;
      }
      if (isName(d)) {
        res.names[d] = d;
      }
    });
    return res;
  }

  function updateIframe(content) {
    console.log("I see a QR code");
    var tinycaturl = "https://www.librarycat.org/lib/CyberneticsCon/item/";

    var res = parseQR(content);
    window.res = res;
    // console.log(window.res);
    objNames = window.res.names;

    // console.log(objNames);

    if (_.isEmpty({objNames}) == true){
      console.log("This is a book");
    } else {
      console.log("this is a plot");
      console.log(objNames);
      console.log("empty???? : " + _.isEmpty({objNames});
    }

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
