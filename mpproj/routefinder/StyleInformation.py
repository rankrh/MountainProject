# All climbing styles
climbing_styles = ['sport', 'trad', 'tr', 'boulder', 'mixed', 'aid', 'ice', 'snow']

# Styles that support multipitch routes
multipitch_styles = ['sport', 'trad', 'mixed', 'aid', 'ice', 'snow']

terrain_types = ['arete', 'chimney', 'slab', 'overhang', 'crack']
# Ordered list of route difficulties in human readable format. Used for sport,
# trad, and tr routes.  Only Yosemite Decimal System (YDS) is supported right
# now.
rope_conv = [
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

# Ordered list of route difficulties in human readable format. Used for
# bouldering routes. Only Hueco rating system is supported
boulder_conv  = [
    'V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2',
    'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4',
    'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+', 'V6-7',
    'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9',
    'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
    'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+',
    'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+',
    'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']

# Ordered list of route difficulties in human readable format.  Used for mixed
# routes.
mixed_conv = [
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11',
    'M12']

# Ordered list of route difficulties in human readable format. Used for Aid
# routes
aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3', 'A3+', 'A4', 'A4+', 'A5','A6']
# Ordered list of route difficulties in human readable format. Used for snow
# routes.
snow_conv = ['Easy', 'Mod', 'Steep']
# Ordered list of route difficulties in human readable format. Used for ice
# routes.
ice_conv = [
    '1', '1+', '1-2', '2', '2+', '2-3', '3', '3+', '3-4', '4','4+', '4-5',
    '5', '5+', '5-6', '6', '6+', '6-7', '7', '7+', '7-8', '8']

nccs_conv = ['I', 'II', 'III', 'IV', 'V']


# Conversion between style and grade system
climb_style_to_grade = {
    'sport': rope_conv,
    'trad': rope_conv,
    'tr': rope_conv,
    'boulder': boulder_conv,
    'mixed': mixed_conv,
    'aid': aid_conv,
    'ice': ice_conv,
    'snow': snow_conv}

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

climbing_systems = {
    'rope_conv': rope_conv,
    'boulder_conv': boulder_conv,
    'mixed_conv': mixed_conv,
    'aid_conv': aid_conv,
    'ice_conv': ice_conv,
    'snow_conv': snow_conv,
    'nccs_conv': nccs_conv}
