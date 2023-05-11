VolleyVision by Morgan Wilson

Setup

You must have python installed and have the Pygames, Pygames_GUI, and openCV-python libraries installed for this project to run.


Basic Documentation

Animation
    If you are just here to see how the animation engine runs I already have a playerCoordinate.txt file in and you just need to run the python file. You can put in new file of coordinates and all you have to do is follow this formating ID, X, Y|ID, X, Y| ect and have it in the same directory. Each new line is considered one frame of player data and you can have as many players on a frame as you choose. Please note that since I am translating the coordinates from the video that the animation engine is only compatible with coordinates from my own test footage. 

Object Tracking
    In the object tracking code you need two files: objectTracking.py and tracker.py. They must be in the same directory. Also need to have volleyball footage. The VIDEOFILE constant is the path to the footage and is the only thing that must be changed to run new video through the tracker.
    After you have your video file path ready you must run the program once. Then go into the dirtyPlayerCoordinates.txt file and count all the characters until you read all the players you want to track for the first time. On line 44 use the character count you have and put it in the contents[:]. 
    ###
    Example: newContents = contents[HERE:] 
    ###
    This object tracker will track for any footage and record the coordinates unlike the animation engine.

How to Use?
    After you have setup all the code you can start to use VolleyVision. You first run whatever volleyball footage you have by running objectTracking.py file. After that take the cleanPlayerCoordinates.txt and copy the contents into the playerCoordinates.txt file in the animation folder. Then run animation.py.

How to Make the Animation Engine Work with Your Footage?
    To do this you will need to find the coordinates of all the intersections of the endlines of your volleyball court in your footage. Once you have all ten coordinates you can put them into videoCoordinates parameter in the getHomographyMatrix function. This will make a new homography matrix so your coordinates translate properly.

