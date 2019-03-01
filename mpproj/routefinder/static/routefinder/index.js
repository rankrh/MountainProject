function ToggleGrade(style) {
    var grade_min = document.getElementById(style + "-min");
    var grade_max = document.getElementById(style + "-max");

    grade_min.disabled = !grade_min.disabled;
    grade_max.disabled = !grade_max.disabled;

    var label = document.getElementById(style + '-label')

    if (grade_max.disabled) {
        label.style.background = "#d9dee2"

    }
    else {
        label.style.background = "#677e91"
    }
}

function ToggleSystem(chosen_system, style) {
    var rope_grades =  document.getElementsByClassName(style);
    var number_of_grades = rope_grades.length;

    for (var i=0; i<number_of_grades; i++) {
        rope_grades[i].style.display = 'none'
    }

    var chosen = document.getElementById(chosen_system);

    chosen.style.display = "inline";
}

function initMap(location={'lat': -25.344, 'lng': 131.036}) {
    var map = new google.maps.Map( document.getElementById('map'),
        {zoom: 6, center: location});
    var marker = new google.maps.Marker({position: location, map: map});
}

var map;
function maps() {
    lats = 53.430967;
    longs = -2.960835;

    var mapProp = {
        center: new google.maps.LatLng(lats, longs),
        zoom: 17,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };

    map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}