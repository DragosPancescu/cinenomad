import re

file_name = "Solo.A.Star.Wars.Story.2018.720p.BluRay.x264-[YTS.AM]"
movie_name = re.sub("[^a-zA-Z]", " ", file_name)
movie_name = " ".join([word.title() for word in movie_name.split() if word != ""][0:3])

if len(movie_name.split()[-1]) <= 2:
    movie_name = " ".join(movie_name.split()[0:-1])

print(movie_name)