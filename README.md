# Infringer 2

Infringer 2 is the rebuild of [Infringer](https://github.com/bharnett/Infringer).  The goal is to scan and search particular web sites to pull media for the user.  The focus of the rebuild was around usability, creating a richer and easier experience for the user, and improving back end searching and scanning.  



Infringer 2 is built on Cherrypy and runs locally accessible as a website.  It was written for Python 3 and not tested with Python 2.  It uses jQuery, Bootstrap, Animate.css and a few other libraries on the front end and gets the show information from [The Movie Database](https://www.themoviedb.org/?language=en)  If you want to run this locally straight from the command line, it does require a few Python libraries:

* Cherrypy
* Mako
* MechanicalSoup
* SQLAlchemy
* APScheduler
* JsonPickle
* tmdbsimple



The output of Infringer 2 is a .crawljob file in a directory of your choosing.  These are processed by [JDownloader 2](http://board.jdownloader.org/showthread.php?t=54725).  This program can be set up to automatically scan for .crawljob files as well.  The download location of the individual files will be included in the .crawljob file.  

Initial setup can be a bit of a pain, so I've included several forum sources for the user to get going.  These just require a user name and password to be entered by the user.  The sites are free to sign up for and I suggest donating if you can.  

For automation, I recommend [Launch Control for Mac](http://www.soma-zone.com/LaunchControl/) or Task Scheduler for Windows. The config allows you to configure a scan interval and weekly refresh of TVDB stuff automatically. Updating those requires a restart of the program. Make sure to use the working directory argument in LauncControl/Launchd in OS X that points to the parent directory of the infringe.py file.



### Things I plan to add

* Cleaning up and isolating the sources.  The user would not be able to add any sources, they would be in the code itself.  
* A movie search functionality.  Actively search sites for a movie of the user's choosing.  
* More logging.  This has been a pain for me, so it should be easier for users to read and provide more actions in context of the log messages.
* CSS updates.  I'm not a CSS wiz and the main index page has issues on smaller view ports.  Anyone who wants to help is welcome to fiddle with it!

