I orginally had the idea for this project back when I was taking a databases course and I was creating a runners database using TFRRS but had difficulty because I could not find an api. 

<a href="https://www.tfrrs.org/">TFRRS</a> is a track and field reporting website where I would check the results of races or look at my current personal bests. Their website is rather old and they do not have a current public api(to my knowledge) and I would like to try and remedy this by creating one. I am going to attempt doing this with webscraping, which I know is not a great idea because if TFRRS changes their website(which they probably will), this repo will break and will have to be either updated or scrapped.

Nonetheless, I want to attempt this to get experience creating my very own library and maybe an api in the future.

Plans:

  Create a python library with beautiful soup to retrieve data from TFRRS, so if anyone wants to use the python framework they can.
  Also create a webserver with flask to have api endpoints to allow people using other frame works and languages to use the api.
