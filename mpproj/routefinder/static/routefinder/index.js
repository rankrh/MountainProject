function ToggleGrade(style) {
    var grade_min = document.getElementById(style + "-min");
    var grade_max = document.getElementById(style + "-max");

    grade_min.disabled = !grade_min.disabled;
    grade_max.disabled = !grade_max.disabled;

    var label = document.getElementById(style + '-label')

    var color = window.getComputedStyle(document.body)
    var selected_color = color.getPropertyValue('--highlight');
    var unselected_color = color.getPropertyValue('--button-primary');

    if (grade_max.disabled) {
        label.style.background = unselected_color
    }

    else {
        label.style.background = selected_color
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

function NextSystem(this_style, system) {
    current_system = this_style.className

    var rope_systems = [
        'yds_rating',
        'french_rating',
        'ewbanks_rating',
        'uiaa_rating',
        'za_rating',
        'british_rating'];

    var boulder_systems = [
        'hueco_rating',
        'font_rating'];

    if (system == "rope") {
        next_system = rope_systems.indexOf(current_system) + 1;
        if (next_system == 6) {
            next_system = 0
        }

        next_system = rope_systems[next_system];

    } else if (system == 'boulder') {
        next_system = boulder_systems.indexOf(current_system) + 1;
        if (next_system == 2) {
            next_system = 0
        }

        next_system = boulder_systems[next_system];

    }
    
    next_system = document.getElementsByClassName(next_system);
    current_system = document.getElementsByClassName(current_system);
    var number_of_routes = current_system.length;

    for (var i=0; i<number_of_routes;i++){
        next_system[i].style.display = 'inline';
        current_system[i].style.display = 'none';
    }
}
