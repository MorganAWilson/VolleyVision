# Imports
import cv2
import os
from tracker import *



# Constants
DIRPATH = os.path.dirname(os.path.realpath(__file__))
DIRTYCORDSFILE = DIRPATH + "\\dirtyPlayerCoordinates.txt"
VIDEOFILE = DIRPATH + "\\TEST_PLAY_1.mov"
CLEANCORDSFILE = DIRPATH + "\\cleanPlayerCoordinates.txt"



# Variables

# distance tracker object used in the object tracking
tracker = EuclideanDistTracker()

#object detection object
object_detector = cv2.createBackgroundSubtractorMOG2(history=-100,varThreshold=40)

# openCV capture object shows the frames of the VIDEOFILE
cap = cv2.VideoCapture(VIDEOFILE)



# Functions

# cleans data from a file by parsing player positions in each frame, and keeping track of lost and 
# found players using distance formula to compare positions, it returns the cleaned data as a text file
def cleanDataFile():

    # get the player ids into an array and have a dictionary of their positions that use the ids as a key
    previousPlayerIDs = []
    previousPlayerPositions = {}

    # open the DIRTYCORDSFILE and read all it all onto the contents variable
    file = open(DIRTYCORDSFILE, 'r')
    contents = file.read()

    #delete everything until the first frame of all six players being detected and create a frames array
    newContents = contents[470:]
    frames = newContents.splitlines()

    # the first frame has the position of all six players and I create an array of just there coordinates and ids
    playerCords = frames[0].split('|')
    playerCords.pop()


    # go through each player in playerCords and add there position into the previousPlayerPositions dictionary using the id as a key and save the ids in an array
    for playerInformation in playerCords:
        indivualPlayerInfo = playerInformation.split(', ')
        playerID = int(indivualPlayerInfo[0])
        playerPosition = (int(indivualPlayerInfo[1]), int(indivualPlayerInfo[2]))
        previousPlayerIDs.append(playerID)
        previousPlayerPositions[playerID] = playerPosition

    # sort the array of ids 
    previousPlayerIDs.sort()

    # go through every frame of data and make sure we have exactly six player and that we are tracking the same six players
    for frame in frames:
        # creating a current playerID array and a playerPositions dictionary to keep track of the players
        playerIDs = []
        playerPositions = {}

        # taking the frame data and splitting each element into a single players data that we have tracked
        playerCords = frame.split('|')
        playerCords.pop()

        # go through the frame data and put each object we find into the playerPositions dictionary and the ids into the playerIDs array
        for playerInformation in playerCords:
            indivualPlayerInfo = playerInformation.split(', ')
            playerID = int(indivualPlayerInfo[0])
            playerPosition = (int(indivualPlayerInfo[1]), int(indivualPlayerInfo[2]))
            playerIDs.append(playerID)
            playerPositions[playerID] = playerPosition
        
        # sort the array of ids
        playerIDs.sort()
        previousPlayerIDs.sort()

        # turn the arrays into sets to get rid of duplicates the algorithm could have picked up and then back into an array
        playerIDs = list(set(playerIDs))
        previousPlayerIDs = list(set(previousPlayerIDs))

        # since the arrays are sorted and have no duplicates we can compare them to see if they are different and if they are something is wrong
        if playerIDs != previousPlayerIDs:


            # making sets out of the id arrays for set opertations
            setPreviousPlayerIDs = set(previousPlayerIDs)
            setPlayerIDs = set(playerIDs)

            # keeping track of the id and positions of the players in both sets
            copyArrayIDs = list(setPreviousPlayerIDs.intersection(setPlayerIDs))
            copyDictionaryPos = {}
            
            # keeping track of the id and positions of the players in playersIDs and not in previousPlayerIDs
            differenceArrayIDs = list(setPlayerIDs.difference(setPreviousPlayerIDs))
            differenceDictionaryPos = {}

            # keeping track of the players that were in previousPlayerIDs and not in playersIDs
            lostArrayIDs = list(setPreviousPlayerIDs.difference(setPlayerIDs))
            lostDictionaryPos = {}

            # updating the dictionaries to have the players positions and the id as the key
            for id in copyArrayIDs:
                copyDictionaryPos[id] = previousPlayerPositions[id]
            
            for id in differenceArrayIDs:
                differenceDictionaryPos[id] = playerPositions[id]

            for id in lostArrayIDs:
                lostDictionaryPos[id] = previousPlayerPositions[id]

            # for each player that is in previousPlayerIDs and not in the playersIDs we consider them lost and have to find them
            for lostID in lostArrayIDs:

                # found represents whether we found the player or not and the deleteID is for deleting the found player out of the differenceArrayIDs
                found = False
                deleteID = -1

                # searching in the differenceArrayIDs to find our lost player
                for differenceID in differenceArrayIDs:

                    # use the distance formula to see if the player was found in a similar spot that we lost our player in
                    point1 = lostDictionaryPos[lostID]
                    point2 = differenceDictionaryPos[differenceID]

                    dx = point1[0] - point2[0]
                    dy = point1[1] - point2[1]

                    distance = math.sqrt(dx**2 + dy**2)

                    # if the distance is within a the range we add the player to the copyArrayIDs and their position update found and set the deleteID
                    if distance < 25:
                        copyArrayIDs.append(differenceID)
                        copyDictionaryPos[differenceID] = differenceDictionaryPos[differenceID]
                        deleteID = differenceID
                        found = True
                        break
                        
                # if we did not find them we just add them back at the position we lost them at     
                if not found: 
                    copyArrayIDs.append(lostID)
                    copyDictionaryPos[lostID] = previousPlayerPositions[lostID]

                # if we found them we already added them to the copyArrayIDs and we have to delete them from differenceArrayIDs outside of the for loop as we are iterating on the array in the loop
                if found:
                    differenceArrayIDs.remove(deleteID)
                    differenceDictionaryPos.pop(deleteID)

            # set playerIDs to the copyArrayIDs and copy the dictionary of positions over as well
            playerIDs = copyArrayIDs
            playerPositions = copyDictionaryPos

        #set the previous players information to the player info we just collected
        previousPlayerIDs = playerIDs
        previousPlayerPositions = playerPositions

        # write all this data into a text file
        fileLine = ''
        file = open(CLEANCORDSFILE, 'a')
        for id in previousPlayerIDs:
            addOnTo = str(id) + ", " +str(previousPlayerPositions[id][0])+ ", " + str(previousPlayerPositions[id][1]) + "|"
            fileLine += addOnTo
        file.write(fileLine + "\n")
        file.close()
            
#  function resizes an input frame by a given scale factor. It calculates the new dimensions 
# of the frame based on the original dimensions and the scale factor, and then resizes the frame
def rescaleFrame(frame, scale=0.25):
    # works for images video and live images
    width = frame.shape[1] * scale
    height = frame.shape[1] * scale
    dimensions = (int(width), int(height)) #tuple

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


# Object Tracking

# emptying the data files before we use them
with open(CLEANCORDSFILE, "w") as f:
    pass
with open(DIRTYCORDSFILE, "w") as f:
    pass

# main object tracking loop
while cap.isOpened():

    # reading the video file and rescaling the frame and if ret is false we break the loop
    ret, frame = cap.read()
    if not ret:
        break
    frame = rescaleFrame(frame)
    height, width, _ = frame.shape

    # creating a mask on the frame
    mask = object_detector.apply(frame)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # array of all the objects we detect
    detections = []

    # iterate through all the contours in the mask and through out bad ones
    for cntr in contours:

        # calculate the area of the contour and if it is too small I do not track it
        area = cv2.contourArea(cntr)
        if area > 50:
            # draw pink circle to show the coordinates I am tracking 
            x,y,w,h = cv2.boundingRect(cntr)
            centerCoordinates = (int((x+(x+w))/2), y+h)
            radius = 5
            color = (255, 0, 255)
            thickness = 2
            cv2.circle(frame, centerCoordinates, radius, color, thickness)

            # adding the object to the detections array
            detections.append([x,y,w,h])

    # whenever detections array gets a new item we add it to boxesIDs
    cordText = ''
    boxesIds = tracker.update(detections)

    # go through all the boxesIDs and draw the bounding box and print the ID on the object
    for boxId in boxesIds:
        x,y,w,h,id = boxId
        cv2.putText(frame, str(id), (x,y-15), cv2.FONT_HERSHEY_PLAIN,1,(255,0,0), 2)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0))
        cordText = cordText + str(id) + ', ' +str(int((x+(x+w))/2)) + ', ' + str(y+h) + '|'
     
    # write the coordinates and ID to a file
    file = open(DIRTYCORDSFILE, "a")
    file.write(cordText +'\n')
    file.close()

    # show the frame and the mask
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    # openCV stuff that needs to be here I don't know why
    key = cv2.waitKey(30)
    if key == 27:
        break

# properly destroying objects in openCV
cap.release()
cv2.destroyAllWindows()

# after all data is collected clean the data
cleanDataFile()