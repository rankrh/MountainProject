# All climbing styles
climbing_styles = ['sport', 'trad', 'tr', 'boulder', 'mixed', 'aid', 'ice', 'snow']
climbing_styles_formatted = {
    'sport': 'Sport', 'trad': 'Trad', 'tr': 'Top Rope',
    'boulder': 'Boulder', 'mixed': 'Mixed', 'aid': 'Aid',
    'ice': 'Ice', 'alpine': 'Alpine'}

sort_methods = {
    'area_group': True,
    'distance': True,
    'style': False,
    'bayes': False,
    'value': False}

# Styles that support multipitch routes
multipitch_styles = ['sport', 'trad', 'mixed', 'aid', 'ice', 'snow']

terrain_types = ['arete', 'chimney', 'slab', 'overhang', 'crack']

# Ordered list of route difficulties in human readable format. Used for sport,
# trad, and tr routes.  Only Yosemite Decimal System (YDS) is supported right
# now.

yds_rating = [
    '3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3', '5.4', '5.5',
    '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+',
    '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10', '5.10b/c', '5.10c',
    '5.10+', '5.10c/d', '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b',
    '5.11', '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d', '5.12a',
    '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+',
    '5.12c/d', '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13',
    '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d', '5.14a', '5.14-',
    '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c', '5.14+', '5.14c/d',
    '5.14d', '5.15a', '5.15-', '5.15a/b', '5.15b', '5.15', '5.15c',
    '5.15+', '5.15c/d', '5.15d']

french_rating = [
    '1-', '1', '1+', '2-', '2', '3', '3+', '4a', '4b', '4c', '5a', '5a',
    '5b', '5b', '5b', '5c', '5c', '5c', '6a', '6a', '6a+', '6a+', '6b',
    '6b', '6b', '6b+', '6b+', '6b+', '6c', '6c', '6c', '6c', '6c+', '6c+',
    '6c+', '7a', '7a', '7a', '7a+', '7a+', '7b', '7b', '7b+', '7b+', '7b+',
    '7c', '7c', '7c', '7c+', '7c+', '8a', '8a', '8a', '8a+', '8a+', '8b',
    '8b', '8b', '8b+', '8b+', '8c', '8c', '8c+', '8c+', '8c+', '9a', '9a',
    '9a', '9a+', '9a+', '9a+', '9b', '9b', '9b+', '9b+', '9c', '9c']

ewbanks_rating = [
    '1', '2', '3', '4', '6', '8', '10', '12', '13', '14', '15','15', '16',
    '16', '16', '17', '17', '17', '18', '18', '19', '19', '20', '20', '20',
    '21', '21', '21', '22', '22', '23', '23', '23', '23', '24', '24', '24',
    '24', '25', '25', '26', '26', '27', '27', '27', '28', '28', '28', '29',
    '29', '29', '29', '29', '29', '30', '30', '31', '31', '32', '32', '33',
    '33', '34', '34', '34', '35', '35', '35', '36', '36', '37', '37', '37',
    '38', '38', '38', '39']
    
uiaa_rating = [
    'I', 'I', 'I', 'I', 'II', 'II', 'III', 'IV', 'IV+', 'V', 'V+', 'V+',
    'VI-', 'VI-', 'VI-', 'VI', 'VI', 'VI', 'VI+', 'VI+', 'VI+', 'VII-',
    'VII-', 'VII', 'VII', 'VII+', 'VII+', 'VII+', 'VII+', 'VIII+', 'VIII-',
    'VIII-', 'VIII-', 'VIII-', 'VIII-', 'VIII', 'VIII', 'VIII', 'VIII+',
    'VIII+', 'VIII+', 'VIII+', 'VIII+', 'IX-', 'IX-', 'IX', 'IX', 'IX',
    'IX+', 'IX+', 'IX+', 'IX+', 'X-', 'X-', 'X-', 'X-', 'X', 'X', 'X+',
    'X+', 'X+', 'X+', 'XI-', 'XI-', 'XI-', 'XI', 'XI', 'XI', 'XI+', 'XI+',
    'XII-', 'XII-', 'XII', 'XII', 'XII+', 'XIII-', 'XIII-']

za_rating = [
    '1', '2', '5', '6', '7', '8', '9', '10', '11', '12', '13', '13', '14',
    '15', '15', '16', '17', '17', '18', '18', '19', '19', '19', '20', '20',
    '20', '21', '21', '22', '22', '23', '23', '23', '24', '24', '24', '25',
    '25', '25', '25', '26', '26', '26', '27', '27', '27', '28', '28', '29',
    '29', '29', '30', '30', '30', '31', '31', '31', '32', '32', '32', '33',
    '33', '34', '34', '35', '35', '36', '36', '37', '37', '38', '38', '38',
    '39', '39', '40', '41']

british_rating = [
    'M 1a', 'M 1b', 'M 1c', 'MM 1c', 'MD 2a', 'D 2c', 'VD 3a', 'VD 3c',
    'MS 4a', 'S 4b', 'MVS 4b', 'MVS 4b', 'VS 4c', 'HVS 4c', 'HVS 4c',
    'HVS 4c', 'HVS 5a', 'E1 5a', 'E1 5a', 'E1 5a', 'E2 5b', 'E2 5b', 'E2 5b',
    'E2 5b', 'E2 5b', 'E3 5b', 'E3 5b', 'E3 5b', 'E3 5c', 'E3 5c', 'E3 5c',
    'E3 5c', 'E4 5c', 'E4 6a', 'E4 6a', 'E4 6a', 'E4 6a', 'E5 6a', 'E5 6a',
    'E5 6a', 'E5 6a', 'E5 6b', 'E6 6b', 'E6 6b', 'E6 6b', 'E6 6b', 'E6 6b',
    'E6 6b', 'E6 6c', 'E7 6c', 'E7 6c', 'E7 6c', 'E7 6c', 'E7 6c', 'E7 7a',
    'E7 7a', 'E8 7a', 'E8 7a', 'E8 7a', 'E8 7a', 'E9 7b', 'E9 7b', 'E9 7b',
    'E9 7b', 'E9 7b', 'E10 7b', 'E10 7b', 'E10 7c', 'E11 7c', 'E11 7c', 'E11 7c',
    'E11 8a', 'E11 8a', 'E11 8a', 'E11 8b', 'E11 8c', 'E11 8c']

hueco_rating  = [
    'V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2',
    'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4',
    'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+', 'V6-7',
    'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9',
    'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
    'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+',
    'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+',
    'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']

font_rating = [
    '3', '4-', '4', '4+', '4+', '5-', '5', '5', '5', '5+', '5+', '5+', '5+',
    '6A', '6A', '6A+', '6A+', '6B', '6B', '6B+', '6B+', '6C', '6C', '6C+',
    '6C+', '7A', '7A', '7A', '7A+', '7A+', '7A+', '7A+', '7B', '7B', '7B',
    '7B+', '7B+', '7C', '7C', '7C', '7C+', '7C+', '7C+', '7C+', '8A', '8A',
    '8A', '8A', '8A+', '8A+', '8A+', '8A+', '8B', '8B', '8B', '8B', '8B+',
    '8B+', '8B+', '8B+', '8C', '8C', '8C', '8C', '8C+', '8C+', '8C+', '8C+',
    '9A', '9A', '9A']

mixed_rating = [
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11',
    'M12']

aid_rating = [
    '0', '0+', '0-1', '1-', '1', '1+', '1-2', '2-', '2', '2+', '2-3', '3-', '3', '3+', '3-4',
    '4-', '4', '4+', '4-5', '5-', '5', '5+', '5-6', '6-', '6', '6+']

snow_rating = ['Easy', 'Mod', 'Steep']

ice_rating = [
    '1', '1+', '1-2', '2-', '2', '2+', '2-3', '3-', '3', '3+', '3-4', '4-', '4','4+', '4-5',
    '5-', '5', '5+', '5-6', '6-', '6', '6+', '6-7', '7', '7+', '7-8', '8']

nccs_rating = ['I', 'II', 'III', 'IV', 'V', 'VI']

danger_rating = ['G', 'PG13', 'R', 'X']

# Conversion between style and grade system
climb_style_to_system = {
    'sport': 'rope_conv',
    'trad': 'rope_conv',
    'tr': 'rope_conv',
    'boulder': 'boulder_conv',
    'mixed': 'mixed_conv',
    'aid': 'aid_conv',
    'ice': 'ice_conv',
    'snow': 'snow_conv',
    'alpine': 'nccs_conv'}

rope_systems = [
    'yds_rating',
    'french_rating',
    'ewbanks_rating',
    'uiaa_rating',
    'za_rating',
    'british_rating']

boulder_systems = [
    'hueco_rating',
    'font_rating']

system_to_grade = {
    'yds_rating': yds_rating,
    'french_rating': french_rating,
    'ewbanks_rating': ewbanks_rating,
    'uiaa_rating': uiaa_rating,
    'za_rating': za_rating,
    'british_rating': british_rating,
    'hueco_rating': hueco_rating,
    'font_rating': font_rating,
}

misc_system_to_grade = {
    'mixed': {
        'rating': 'mixed_rating',
        'grades': mixed_rating,
        'conversion': 'mixed_conv'},
    'aid': {
        'rating': 'aid_rating',
        'grades': aid_rating,
        'conversion': 'aid_conv'},
    'snow': {
        'rating': 'snow_rating',
        'grades': snow_rating,
        'conversion': 'snow_conv'},
    'ice': {
        'rating': 'ice_rating',
        'grades': ice_rating,
        'conversion': 'ice_conv'},
    'alpine': {
        'rating': 'alpine_rating',
        'grades': nccs_rating,
        'conversion': 'nccs_conv'},
}