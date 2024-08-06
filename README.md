# How fly are you?

> Note: I totally stole a lot of the styling from [YC Vibe Check](https://github.com/thesephist/ycvibecheck)! (Planning on restyling eventually, but wanted to get something pretty quickly).

Not much to say here besides that I read a paper on a fly inspired bloom filter and was inspired to do something dumb with it. It semantically embeds submitted text, maps it onto a set of "neurons" through a sparse random matrix, and then returns the avg. value of those neurons for a novelty score. With my current parameters, it's able to differentiate between about 500 novel words before scores start dropping off.

Read the code at your own risk.

### Future TODOs

If I wanted to take this more seriously, I would have the server write a backup every 10/100 queries, so that it's persistent and can be scaled more easily. 

I'm also planning on adding dark mode in one of these days.

Oooh, and it'd be cool if there was more juice on submitting words (maybe screen shake or something), and you should be able to hover points on the graph and have it show you the word you submitted.

### Development

The frontend is React + D3, and the backend is Flask. I've setup a `wsgi.py` for Gunicorn to use on the server.