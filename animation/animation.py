#imports
import pygame as p
import pygame_gui
import numpy as np
import cv2
import os

from pygame_gui.elements import UIHorizontalSlider



# have to initialize Pygames
p.init()



#Constants
WIDTH = 930
HEIGHT = 930
MAX_FPS = 60
dir_path = os.path.dirname(os.path.realpath(__file__))
CORDSTEXTFILE = dir_path + '\\playersCoordinates.txt'



#Functions

# This function takes in two arrays of coordinates, one representing coordinates from a video frame and another representing coordinates 
# in a plane or surface, calculates the homography between the two sets of coordinates using the OpenCV library, and returns the resulting 
# homography matrix.

def getHomographyMatrix( videoCoordinates = [[13, 419], [70, 280], [189, 389],[183, 266], [269, 379], [233, 260], [345, 369], [284, 256], [479, 342], [380, 247]], planeCoordinate = [[239, 13],[689, 13],[239, 311],[689, 311], [239, 462], [689, 462], [239, 611], [689, 611], [239, 914], [689, 914]]):
    
    #Converts coordinate arrays into numpy arrays
    videoCoordinatesNP = np.array(videoCoordinates)
    planeCoordinatesNP = np.array(planeCoordinate)

    # calculate the homography
    homography, status = cv2.findHomography(videoCoordinatesNP, planeCoordinatesNP)

    return homography

# this function takes in a coordinate tuple and a homography matrix, performs a perspective transformation 
# on the coordinate tuple using the homography matrix, and returns the new coordinate tuple with the updated coordinates
def coordinateTranslation(coordTuple, homography):
    
    # The perspectiveTransformation function requires the array to be formatted like this
    videoCoordinate = np.array([[int(coordTuple[1]), int(coordTuple[2])]], dtype='float32')
    videoCoordinateNP = np.array([videoCoordinate])

    # translating the coordinateArray 
    translatedCoordinate = cv2.perspectiveTransform(videoCoordinateNP, homography)

    # recreating the coordTuple with the correct ID and translated coordinates
    newCoordTuple = (int(coordTuple[0]), int(translatedCoordinate[0][0][0]), int(translatedCoordinate[0][0][1]))

    return newCoordTuple

# This function takes in a Pygame display screen, an array of coordinates, a frame number, and a 
# homography matrix, translates the coordinates based on the homography matrix, and draws the corresponding 
# players on the screen

def drawFrame(screen, coordinateArray, frameNumber, homography): 
    
    # draws the court as the background
    drawCourt(screen)

    # gets all the players coordinates and translates them and then draws them
    for player in coordinateArray[frameNumber]:
        player.split(', ')
        cordTuple = tuple(player.split(', '))
        cordTuple = coordinateTranslation(cordTuple, homography)
        drawPlayer(screen, int(cordTuple[1]), int(cordTuple[2]), 0)

# This function is used to draw a player on a pygame screen. It takes in the screen object, 
# x and y coordinates of the player, team number (1 or 2), and player radius as inputs

def drawPlayer(screen, x, y, team, playerRadius = 15):
    
    # determine player color based on what side of the court they are on
    playerColor = p.Color("darkred")
    if team == 1:
        playerColor = p.Color("darkturquoise")

    # draw the player on the screen
    p.draw.circle(screen, playerColor, (x,y), playerRadius)

# This function is used to draw a volleyball court on a Pygame screen. It takes in the screen object, 
# courtWidth, courtHeight, lineWidth, and lineHeight as inputs

def drawCourt(screen, courtWidth=450, courtHeight=900, lineWidth=10, lineHeight=10):

    # Drawing a green background
    p.draw.rect(screen, p.Color("darkgreen"), p.Rect(0,0,WIDTH,HEIGHT))

    # Drawing the court
    p.draw.rect(screen, p.Color("tan"), p.Rect((WIDTH - courtWidth) / 2, (HEIGHT - courtHeight) / 2, courtWidth, courtHeight))

    # Drawing the center line
    p.draw.rect(screen, p.Color("black"), p.Rect((WIDTH - courtWidth) / 2, (HEIGHT - courtHeight) / 2 + (courtHeight / 2) - (lineHeight / 2), courtWidth, lineHeight))
    
    # Drawing the ten foot lines
    p.draw.rect(screen, p.Color("black"), p.Rect((WIDTH - courtWidth) / 2, ((HEIGHT - courtHeight) / 2) + (courtHeight / 3) - (lineHeight / 2), courtWidth, lineHeight))
    p.draw.rect(screen, p.Color("black"), p.Rect((WIDTH - courtWidth) / 2, ((HEIGHT - courtHeight) / 2) + ( 2 * courtHeight / 3) - (lineHeight / 2), courtWidth, lineHeight))



#Variables

# takes the coordinates from the text file and put them into the playerCoordinate array
playerCoordinates = []

with open(CORDSTEXTFILE, 'r') as file:
    for line in file:
        allPlayerInformation = line.split("\n")
        allPlayerInformation.pop()
        for player in allPlayerInformation:
            singlePlayerInformation = player.split('|')
            singlePlayerInformation.pop()
            playerCoordinates.append(singlePlayerInformation)

# homography matrix that is used to translate coordinates from the video to the animation
homography = getHomographyMatrix()

# for the animatiop -1 means rewind, 0 means paused, 1 means playing
isPlaying = 0

# keeps track of the frame timing for the animation. We count the frames and whenever we hit a multiple of animationFPS we update the animation
frameCounter = 0
animationFPS = 5

# Pygames GUI elements
manager = pygame_gui.UIManager((WIDTH,HEIGHT))
frameSlider = UIHorizontalSlider(p.Rect(WIDTH/2 - 250,10,500,40), 0, (0,len(playerCoordinates) - 1), manager)
playButton = pygame_gui.elements.UIButton(p.Rect((0, 0), (100, 50)), 'Play', manager)
pauseButton = pygame_gui.elements.UIButton(p.Rect((0, 50), (100, 50)),'Pause',manager)
rewindButton = pygame_gui.elements.UIButton(p.Rect((0, 100), (100, 50)),'Rewind', manager)

# Pygames elements
screen = p.display.set_mode((WIDTH, HEIGHT))
background = p.Surface((WIDTH,HEIGHT))
clock = p.time.Clock()
running = True



# main game loop
while running:
    
    # handles all the events that come in
    for e in p.event.get():

        # checks to see if someone has quit the program and terminates the loop if they did
        if e.type == p.QUIT:
            running = False
        
        # checks to see if the frameSlider has been moved and sets the frame to the value of the slider
        elif e.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            drawFrame(screen, playerCoordinates, e.value, homography)

        # checks to see if a button has been pressed
        elif e.type == pygame_gui.UI_BUTTON_PRESSED:

            # checks to see if the playButton has been pressed and if it has we disble the button pressed and make sure the other buttons are enabled and set isPlaying to 1
            if e.ui_element == playButton:
                isPlaying = 1
                playButton.disable()
                rewindButton.enable()
                pauseButton.enable()
            
            # checks to see if the rewindButton has been pressed and if it has we disble the button pressed and make sure the other buttons are enabled and set isPlaying to -1
            elif e.ui_element == rewindButton:
                rewindButton.disable()
                playButton.enable()
                pauseButton.enable()
                isPlaying = -1

            # checks to see if the rewindButton has been pressed and if it has we disble the button pressed and make sure the other buttons are enabled and set isPlaying to 0
            elif e.ui_element == pauseButton:
                pauseButton.disable()
                rewindButton.enable()
                playButton.enable()
                isPlaying = 0

        # at the end of the event loop we process the events so we know we have dealt with them
        manager.process_events(e)
    
    # updates the animation every animationFPS frame
    if frameCounter % animationFPS == 0:

        # checking to see if the animation is set to be pause and if it is we do not update the animation
        if isPlaying != 0:

            # checking to see if the animation is set to play and if it is we move the frameSlider by 1, check to make sure we do not go past the last frame, and draw the frame
            if isPlaying == 1:
                newValue = frameSlider.get_current_value() + 1

                # checking to see if we went past the last frame and if we do we set the animation to be paused and disable the play button
                if newValue > frameSlider.value_range[1]:
                    newValue -= 1
                    isPlaying = 0
                    pauseButton.disable()
                    rewindButton.enable()
                    playButton.enable()

                # after we check to make sure we do not go past the last frame we update the frameSliders position and draw the frame
                frameSlider.set_current_value(newValue)
                drawFrame(screen, playerCoordinates, frameSlider.get_current_value(), homography)

            # since we checked to see if the animation was playing if it not playing it must be rewinding
            else:
                newValue = frameSlider.get_current_value() - 1

                # checking to see if we went past the first frame and if we do we set the animation to be paused and disable the rewind button
                if newValue > frameSlider.value_range[1]:
                    newValue += 1
                    isPlaying = 0
                    pauseButton.disable()
                    rewindButton.enable()
                    playButton.enable()

                # after we check to make sure we do not go past the first frame we update the frameSliders position and draw the frame
                frameSlider.set_current_value(newValue)
                drawFrame(screen, playerCoordinates, frameSlider.get_current_value(), homography)
    
    # to make sure that the animation runs at a consistent speed
    timeDelta = clock.tick(MAX_FPS)/1000.0

    # update the GUI manager and the Pygames screen with the new frame data
    manager.update(timeDelta)
    manager.draw_ui(screen)
    p.display.update()

    # counting the number of frames we have drawn
    frameCounter += 1