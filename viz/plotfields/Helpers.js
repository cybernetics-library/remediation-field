var Helpers = {};


Helpers.pRandom = (seed) => {
    var r = (seed * 116593 % 1000) / 1000
    return r;
}


Helpers.randomColor = () => {
  var cssHSL = "hsl(" + Math.round(360 * Math.random()) + ',' +
                    Math.round(25 + 70 * Math.random()) + '%,' +
                     Math.round(45 + 10 * Math.random()) + '%)';
//  return new THREE.Color("hsl(0, 100%, 50%)");
  return new THREE.Color(cssHSL);
}


Helpers.pRandomColor = (seed) => {
  var cssHSL = "hsl(" + Math.round(360 * Helpers.pRandom(seed)) + ',' +
                    Math.round(25 + 70 * Helpers.pRandom(seed+1)) + '%,' +
                     Math.round(45 + 10 * Helpers.pRandom(seed+2)) + '%)';
//  return new THREE.Color("hsl(0, 100%, 50%)");
  return new THREE.Color(cssHSL);
}


export default Helpers;
