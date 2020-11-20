# Mountain Project
Scrapes Mountain Project (MP) and helps find the best areas for your climbing preferences.

The ultimate purpose of the program is to help users optimize their time by finding climbing areas based on their preferences.  By combining metrics such as distance to user, type/difficulty of routes, and concentration of routes, we can find where climbers can make best use of their time.  MP lets users search by a variety of different metrics, including route quality, number of pitches, route type, and difficulty, as well as by geographic location.  This approach has limitations.  This program not only improves upon some of these metrics, such as the way that route quality is measured, but also adds new functionality.

## Ratings
MP rates routes by a simple user-average of up to four stars.  This is an easy number to calculate but has drawbacks when sorting by quality as highly rated routes with few ratings tend to appear higher than they should.  It seems like there is some inner-working in MP that mitigates this, but calculating a quality explicitly works too.  This program caclulates quality using Bayesian statistics, essentially adding 'phantom voters' to each route that move all ratings towards the mean.

## Clustering
By clustering routes based on geographic area and similarity of styles, this program helps to promote routes that are near other routes similar to them.  This helps by ignoring routes that are exactly what you want - but 50 miles from any other route you might want to do.

## Terrain
Climbers often have a type of route - e.g. overhangs, slab, cracks - that they like more than others.  Using natural language processing of route descriptions and comments, this program attempts to categorize each climb into one or more of these terrain styles. This is another metric by which users can select their preferred type of climbing.

## Other Metrics
### Styles
MP's search function only allows users to search by one climbing style at a time - bouldering, sport, etc.  This program allows users to select any number of routes that they like, and finds the best areas that have any of these styles.  For example, I may enjoy sport climbing and bouldering, and would want to find nearby areas that have either.  Additionally, in general the grade people can climb changes depending on the type of route, and this function allows users to specify grade in a style-specific way.  

### Danger and Commitment
The program also lets users weed-out routes that are too risky or require too much time commitment.  (NB Commitment isn't supported yet, but will soon.)


##Desktop Version(Beta)
A kivy-based desktop application not fully fleshed out.
https://youtu.be/N_6gbT_i4VY
