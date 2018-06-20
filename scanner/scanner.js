

  window.thisbook = "";
  var globalQR;
  var memArray;
  var theme;

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
    // console.log(res);
    return res;
  }

  function sameBookTimer() {
      window.prevlink = {};
  };

  function handleScans(content) {

    setTimeout(sameBookTimer, 12000);
$("iframe").fadeIn(300);

    var res = parseQR(content);
    if(!(_.isEqual(window.prevlink, res))) {
        window.prevlink = res;
        console.log(res);
        console.log("new book");
        globalQR = content;
           displayModal();
      };
  };

  function submitLinkToApi(content) {
    var res = parseQR(content);
    window.restest = res;
    // var mem = $( "#mem-id" ).html();
    // var theme = document.getElementById("theme-id").value;
    // var memTo = document.getElementById("mem-to-id").value;
    var bookid = urlToId(res.books[Object.keys(res.books)[0]]);
    // var apiurl = "https://library.cybernetics.social/connect_book_to_memory";

    $.post("https://library.cybernetics.social/connect_book_to_memory",
    {
    "book_id": bookid,
    "station_id": "computer1",
    "timestamp": new Date().getTime() / 1000,
    "memory_from": $( "#mem-id" ).html(),
    "memory_to": document.getElementById("mem-to-id").value,
    "theme": theme
  },
    function (response) {
        console.dir(response);
      });
  };


  function displayModal() {
    $("#prompt-1").fadeOut(300).delay(2000);
    $("video").addClass( "blur grayscale" );
    $("#prompt-2").fadeIn(400).delay(2000);
    $("#mem-to-id").val('');
    // TODO:

    var apiurl = "https://library.cybernetics.social/memories/unique";
    $.ajax({
      type: "GET",
      url: apiurl,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(res) {
        console.log(res.memories_all);
        console.log("successfully submitted!")
        memArray = res.memories_all;
      }
    });


  }

  function updateIframe(content,res) {
    var tinycaturl = "https://www.librarycat.org/lib/CyberneticsCon/item/";


    // var url = objNames[Object.keys(objNames)[0]];
    // console.log("url: " + url);

    ///////////////////////////////////////
    var res = parseQR(content);
    var thisbookids = Object.keys(res.books).sort()
    console.log("This book id: " + thisbookids);

    var thisbooks = thisbookids.join("+");
    if ((thisbooks) && (window.prevbooks != thisbooks)) {

      // var s = "";
      // s += "\nBOOKs = " + thisbookids.join(", ");
      // s += "\nNAMEs = " + Object.keys(res.names).join(", ");
      // $("#output").html(s);

      // console.log(s);
      $("#iframe").attr("src", "https://www.librarycat.org/lib/CyberneticsCon/item/" + thisbookids[0]);
      window.prevbooks = thisbooks;
    }
  }


$(document).ready(function() {


  let scanner = new Instascan.Scanner({
    video: document.getElementById('preview')
  });

  scanner.addListener('scan', function(content) {
    handleScans(content)
    updateIframe(content);
  });

  function link() {
    console.log("Link Book to Plot");
  }

  Instascan.Camera.getCameras().then(function(cameras) {
    if (cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error('No cameras found.');
    }
  }).catch(function(e) {
    console.error(e);
  });


// TODO:
//random theme


randomTheme();

$.ajax({
  type: "GET",
  url: "https://library.cybernetics.social/memories/unique",
  contentType: "application/json; charset=utf-8",
  dataType: "json",
  success: function(res) {
    console.log(res.memories_all);
    console.log("successfully requested mem_from!")
    memArray = res.memories_all;
    var randomMem = memArray[Math.floor(Math.random()*memArray.length)];
    $('#mem-id').html(randomMem);
  }
});

var input = document.getElementById("mem-to-id");

// Execute a function when the user releases a key on the keyboard
input.addEventListener("keyup", function(event) {
  // Cancel the default action, if needed
  event.preventDefault();
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
    // Trigger the button element with a click
    sendMem();
  }
});


});

function randomTheme(){
themeArray = ["heart", "vision", "mouth", "body"];
var randomTheme = themeArray[Math.floor(Math.random()*themeArray.length)];
console.log(randomTheme);
theme = randomTheme
$('.theme').html(theme);
};

function sendMem() {
 submitLinkToApi(globalQR);
 randomTheme();
 $("#success").fadeIn(300).delay(2000);
  $("#success").fadeOut(300).delay(3400);


  setTimeout(showPrompt, 3400);
 $("#prompt-2").fadeOut(300).delay(2000);
 $("iframe").fadeOut(300);

};

function showPrompt(){
  $('#mem-id').clear;
  var randomMem = memArray[Math.floor(Math.random()*memArray.length)];
  $('#mem-id').html(randomMem);
  $("video").removeClass( "blur grayscale" );
  $("#prompt-1").fadeIn(300);
}
