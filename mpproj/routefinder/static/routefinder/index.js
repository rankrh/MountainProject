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


function initMap(location={lat: -25.344, lng: 131.036}) {
    var map = new google.maps.Map( document.getElementById('map'),
        {zoom: 6, center: location});
    var marker = new google.maps.Marker({position: location, map: map});}


