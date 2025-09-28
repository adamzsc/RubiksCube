from copy import deepcopy
import pygame, sys
import time
from random import *
from pygame.locals import *
import math
BLACK = (30,30,30) #Setting (R,G,B) values for all colours
GRAY = (192,192,192)
W = (255,255,255)
Y = (255,255,0)
B = (0,200,255)
O = (255,140,0)
G = (0,255,0)
R = (255,0,0)
clock = pygame.time.Clock()

complete = False
pygame.init()

ROTATE_SIDE = { #When rotating a side
    (1,2) : (0,1), #Colour in pos (1,2) : Moved to pos (0,1)
    (2,0) : (2,2),
    (0,0) : (2,0),
    (2,2) : (0,2),
    (0,1) : (1,0),
    (1,0) : (2,1),
    (0,2) : (0,0),
    (2,1) : (1,2)
    }

SIDES = { #Used when either doing L,R or M movements
    0 : 1, #Any colours on side 0 : Are replaced by those on side 1
    1 : 2,
    2 : 3,
    3 : 0
    }
LEFT_PIECES = { #Used when doing the L movement
    0 : ((0,1,2),(0,0,0)), #On side 0, the colours that move are at pos (0,0), (1,0) and (2,0)
    1 : ((0,1,2),(0,0,0)),
    2 : ((0,1,2),(0,0,0)),
    3 : ((0,1,2),(0,0,0))
    }
RIGHT_PIECES = {
    0 : ((0,1,2),(2,2,2)),
    1 : ((0,1,2),(2,2,2)),
    2 : ((0,1,2),(2,2,2)),
    3 : ((0,1,2),(2,2,2))
    }
MIDDLE_PIECES = {
    0 : ((0,1,2),(1,1,1)),
    1 : ((0,1,2),(1,1,1)),
    2 : ((0,1,2),(1,1,1)),
    3 : ((0,1,2),(1,1,1))
    }
TOPSIDES = {
    1 : 5,
    3 : 4,
    4 : 1,
    5 : 3
    }
UP_PIECES = {
    1 : ((0,0,0),(0,1,2)),
    3 : ((2,2,2),(2,1,0)),
    4 : ((0,0,0),(0,1,2)),
    5 : ((0,0,0),(0,1,2)),
    }
DOWN_PIECES = {
    1 : ((2,2,2),(0,1,2)),
    3 : ((0,0,0),(2,1,0)),
    4 : ((2,2,2),(0,1,2)),
    5 : ((2,2,2),(0,1,2))
    }
AIDDLE_PIECES = {
    1 : ((1,1,1),(0,1,2)),
    3 : ((1,1,1),(2,1,0)),
    4 : ((1,1,1),(0,1,2)),
    5 : ((1,1,1),(0,1,2))
    }
FRONTSIDES = {
    0 : 4,
    2 : 5,
    4 : 2,
    5 : 0   
    }
FRONT_PIECES = {
    0 : ((2,2,2),(2,1,0)),
    2 : ((0,0,0),(0,1,2)),
    4 : ((0,1,2),(2,2,2)),
    5 : ((2,1,0),(0,0,0))
    }
BACK_PIECES = {
    0 : ((0,0,0),(0,1,2)),
    2 : ((2,2,2),(2,1,0)),
    4 : ((2,1,0),(0,0,0)),
    5 : ((0,1,2),(2,2,2))
    }
CIDDLE_PIECES = {
    0 : ((1,1,1),(0,1,2)),
    2 : ((1,1,1),(2,1,0)),
    4 : ((2,1,0),(1,1,1)),
    5 : ((0,1,2),(1,1,1))
    }

OLLOrder = [(1,1,1),(3,2,0),(3,2,1),(3,2,2),(1,1,1),
            (4,0,0),(0,0,0),(0,0,1),(0,0,2),(5,0,2),
            (4,0,1),(0,1,0),(0,1,1),(0,1,2),(5,0,1),
            (4,0,2),(0,2,0),(0,2,1),(0,2,2),(5,0,0),
            (1,1,1),(1,0,0),(1,0,1),(1,0,2),(1,1,1)]

sidePositions =     [ #Shows positions of every side piece
            [(0,1,2),(5,0,1)], 
            [(0,1,0),(4,0,1)], 
            [(0,0,1),(3,2,1)], 
            [(2,2,1),(3,0,1)], 
            [(0,2,1),(1,0,1)], 
            [(1,1,2),(5,1,0)], 
            [(1,2,1),(2,0,1)], 
            [(4,1,2),(1,1,0)], 
            [(5,1,2),(3,1,2)],  
            [(4,1,0),(3,1,0)], 
            [(2,1,0),(4,2,1)], 
            [(5,2,1),(2,1,2)]  
                ]

cornerPositions = [
            [(0,2,2),(1,0,2),(5,0,0)], 
            [(5,2,0),(1,2,2),(2,0,2)], 
            [(4,2,2),(1,2,0),(2,0,0)], 
            [(0,2,0),(1,0,0),(4,0,2)], 
            [(0,0,2),(5,0,2),(3,2,2)], 
            [(0,0,0),(4,0,0),(3,2,0)], 
            [(4,2,0),(2,2,0),(3,0,0)], 
            [(5,2,2),(2,2,2),(3,0,2)]  
                ]

colourOrder = [B,R,G,O,B,O] #The order in which the sides will be completed at each stage (colour of side centre-piece)

gameExit = False
myfont = pygame.font.SysFont('Calibri Body', 40)
gameDisplay = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

background = pygame.image.load("background.jpg").convert()

class Cube():
    def __init__(self):
        self.colourIndex = 0 #The current side that is being completed, as an index of the colourOrder list
        self.inputColours = True
        self.tutorial = pygame.image.load("tutorial.jpg").convert()
        self.tutorialBG = pygame.image.load("tutorialBG.png").convert_alpha()
        self.showTutorial = False
        self.tutorialOffset = 0
        self.solved = False
        self.stage = 0
        self.movements = []
        self.originalCube = [ #Net for the origian cube enetered in
            [[BLACK,BLACK,BLACK],[BLACK,Y,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,O,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,W,BLACK],[BLACK,BLACK,BLACK]],
            [[BLACK,BLACK,BLACK],[BLACK,R,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,G,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,B,BLACK],[BLACK,BLACK,BLACK]]
            ]

        self.cube = [ #Net for the cube, original copy
            [[BLACK,BLACK,BLACK],[BLACK,Y,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,O,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,W,BLACK],[BLACK,BLACK,BLACK]],
            [[BLACK,BLACK,BLACK],[BLACK,R,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,G,BLACK],[BLACK,BLACK,BLACK]],[[BLACK,BLACK,BLACK],[BLACK,B,BLACK],[BLACK,BLACK,BLACK]]
            ]
        
        self.newCube = [ #Net for the cube, the new copy, copies from original copy
            [
                [BLACK,BLACK,BLACK],
                [BLACK,Y,BLACK],
                [BLACK,BLACK,BLACK]
                ],
            [
                [BLACK,BLACK,BLACK],
                [BLACK,O,BLACK],
                [BLACK,BLACK,BLACK]
                ],
            [
                [BLACK,BLACK,BLACK],
                [BLACK,W,BLACK],
                [BLACK,BLACK,BLACK]
                ],
            [
                [BLACK,BLACK,BLACK],
                [BLACK,R,BLACK],
                [BLACK,BLACK,BLACK]
                ],
            [
                [BLACK,BLACK,BLACK],
                [BLACK,G,BLACK],
                [BLACK,BLACK,BLACK]
                ],
            [
                [BLACK,BLACK,BLACK],
                [BLACK,B,BLACK],
                [BLACK,BLACK,BLACK]
                ]
            ]

    def drawCube(self):
        for i in range(3):
                for t in range(3):
                    pygame.draw.rect(gameDisplay,Cube.newCube[1][i][t],[767 + (t * 132),348 + (i * 132),128,128])      
        pygame.draw.rect(gameDisplay,Cube.newCube[0][1][1],[768 ,311,390,16])
        pygame.draw.rect(gameDisplay,Cube.newCube[2][1][1],[768 ,760,390,16])
        pygame.draw.rect(gameDisplay,Cube.newCube[4][1][1],[730 ,349,16,390])
        pygame.draw.rect(gameDisplay,Cube.newCube[5][1][1],[1180,349,16,390])

    def drawTutorial(self):
        gameDisplay.blit(self.tutorial,[600,self.tutorialOffset])
        gameDisplay.blit(self.tutorialBG,[0,0])

    def displayTutorial(self):
        self.showTutorial = not self.showTutorial

    def scrollTutorial(self,val):
        if 600 <= pygame.mouse.get_pos()[0] <= 1320: #If mouse is over image
            if -1920 <= self.tutorialOffset + val <= 0: #If offset value in range
                self.tutorialOffset += val #Adjust offset
                
    def checkIntegrity(self):
        colours = [0,0,0,0,0,0] #Inital array of colours
        for i in range(6): #For each side
            for t in range(3): #For each row
                for s in range(3): #For each column
                    colours[self.findSide(self.cube[i][t][s])] += 1
                    #Increase respective colour count by 1
        if colours.count(9) == 6: #If 9 of each colour
            return True #Integrity is true
        return False #Integrity is false

    def updateCube(self,cube): #Updates cube by copying it from newCube
        return deepcopy(cube)

    def doAlgorithm(self,algorithm):
        for x in algorithm:
            movements[x][0](movements[x][1])
    
    def findSidePiece(self,col1,col2):  #Function to find location of any side piece given both its colours 
        for i in range(len(sidePositions)):
            localColours = [] #Array that will contain the colours of the side pieces that are checked
            for t in range(2):
                colour = self.cube[sidePositions[i][t][0]][sidePositions[i][t][1]][sidePositions[i][t][2]]
                localColours.append(colour)
            if col1 in localColours and col2 in localColours: #Checks if given colours are both in the array
                if self.stage == 0:                    
                    self.solveYellowWhite(sidePositions[i][localColours.index(col1)])
                elif self.stage == 3:
                    self.solveSecondLayer(sidePositions[i][localColours.index(col1)])
    
    def findCornerPiece(self,col1,col2,col3):  #Function to find location of any side piece given both its colours
        for i in range(len(cornerPositions)):
            localColours = [] #Array that will contain the colours of the side pieces that are checked
            for t in range(3):
                colour = self.cube[cornerPositions[i][t][0]][cornerPositions[i][t][1]][cornerPositions[i][t][2]]
                localColours.append(colour)
            if col1 in localColours and col2 in localColours and col3 in localColours: #Checks if given colours are both in the array
                if self.stage == 2:
                    self.solveWhiteFace(cornerPositions[i][localColours.index(col1)])

    def solveYellowWhite(self,pos): #Solve the daisy, pos is the position on the cube of the white face of the side piece // stage = 0
        if pos[0] == 0: #If it is on yellow side, it is complete  
            if self.colourIndex < 3:
                self.colourIndex += 1 #Go to next colour
            else:
                self.colourIndex = 0 #Reset colour index
                self.stage += 1 #From 0 to 1
                self.solveWhiteCross() #Next stage

        elif pos[0] == 1:
            if pos[1] == 1: #If on the middle row
                self.reserveSpot((0,1,pos[2]),self.U)
                if pos[2] == 0: 
                    self.L(3) #If on the left                    
                else: 
                    self.R(1) #If on the right
            else: #If on top/bottom row      
                self.reserveSpot((0,2,1),self.U)
                self.F(1) #Front turn to get it on middle row
                
        elif pos[0] == 2: #If it is on the white side
            self.reserveSpot((0,2 - pos[1],pos[2]),self.U)
            if pos[1:] == (0,1): self.F(2) #If on the front (bottom side)
            elif pos[1:] == (1,0): self.L(2) #If on the left (bottom side)
            elif pos[1:] == (1,2): self.R(2) #If on the right (bottom side)
            elif pos[1:] == (2,1): self.B(2) #If on the back (bottom side)

        else: #If it isnt on white/yellow/front
            self.rotateToSide(pos[0],Y) #Rotate to side which has the white side piece, yellow side on top
            
        self.findSidePiece(W,colourOrder[self.colourIndex]) #Find position of side piece     

    def solveWhiteCross(self): #Solve the white cross // stage = 1
        for i in range(4):
            for t in range(4):
                if self.cube[0][2][1] == W and (self.cube[1][0][1] == self.cube[1][1][1]): #If top colour is white and centre piece and side piece match
                    self.F(2) #Front movement twice, put on white side
                    break
                self.U(1) #If not, try next rotation
            if i != 3: #So that it doesnt rotate an extra time
                self.X(1) #Rotate to do the next side piece
        self.Z(2) #When complete, rotate cube so that the white side is on top
        self.stage += 1 #From 1 to 2
        self.findCornerPiece(W,colourOrder[self.colourIndex],colourOrder[self.colourIndex + 1])

    def solveWhiteFace(self,pos):
        if pos[0] == 0: #If it is on the white face alrady
            if self.cube[(pos[1] + 3) - (2 * pos[1])][2 - pos[1]][pos[2]] == self.cube[(pos[1] + 3) - (2 * pos[1])][1][1]: #It is in the correct place
                if self.colourIndex < 3: #If that wasnt the last colour
                    self.colourIndex += 1 #Go to next colour
                else:
                    self.colourIndex = 0 #Else reset the colour order
                    self.stage += 1 #From 2 to 3
                    self.findSidePiece(colourOrder[self.colourIndex],colourOrder[self.colourIndex + 1]) #Start next stage
            else: #If placed incorrectly on white face
                if pos[1] == 0: #If on the back row
                    self.X(2) #If it is on the back row, flip so that it is on the front row
                else:
                    if pos[2] == 0: #If it is on the left 
                        self.L(1),self.D(1),self.L(3) #Remove it                        
                    else: #If it is on the right
                        self.R(3),self.D(3),self.R(1) #Remove it 

        elif pos[0] == 2: #If it on the bottom side
            if self.cube[0][2][2] == W: #If bottom right piece on white side is white       
                self.reserveSpot((0,2,2),self.X) #Rotate the cube
            else:
                if pos == (2,2,0): #If position of white corner piece is at bottom left on bottom side
                    self.R(3),self.D(3),self.R(1) #Place corner piece on bottom row                  
                else:
                    self.D(1) 


        elif pos[0] == 1: #If on the front side
            if pos[2] == 0: #If on the left
                if pos[1] == 0: #If on the top row
                    self.L(1),self.D(3),self.L(3) #Put it on the bottom row
                else: #On the bottom row
                    col = self.cube[4][2][2] #Determine the second colour of the corner piece
                    self.rotateToSide(self.findSide(colourOrder[colourOrder.index(self.cube[4][2][2]) - 1]),W)
                    #Rotate to the side with this colour on the left
                    for i in range(4):
                        if self.cube[1][2][0] == W and self.cube[4][2][2] == col: #If the corner piece is correctly positioned
                            self.D(1),self.L(1),self.D(3),self.L(3) #Insert corner piece into white face
                            break #Break loop
                        self.D(1) #Down turn

            else: #If on the right
                if pos[1] == 0: #If on the top row
                    self.R(3),self.D(1),self.R(1) #Put it on the bottom row
                else: #On the bottom row
                    col = self.cube[5][2][0] #Determine the second colour of the corner piece
                    self.rotateToSide(self.findSide(colourOrder[colourOrder.index(self.cube[5][2][0]) + 1]),W)
                    #Rotate to the side with this colour on the right
                    for i in range(4):
                        if self.cube[1][2][2] == W and self.cube[5][2][0] == col: #If the corner piece is correctly positioned
                            self.D(3),self.R(3),self.D(1),self.R(1) #Insert corner piece into white face
                            break #Break loop
                        self.D(1) #Down turn

        else: #If it isnt on the top/bottom/front
            self.rotateToSide(pos[0],W) #Rotate to side which has the white side piece, yellow side on top

        self.findCornerPiece(W,colourOrder[self.colourIndex],colourOrder[self.colourIndex + 1]) #Find pos of next corner piece

    def solveSecondLayer(self,pos):

        if pos[0] == 2:
            self.rotateToSide(self.findSide(colourOrder[self.colourIndex + 1]),W)       
            
        elif pos[1] == 1: #Middle layer
            if pos[0] == 1: #Front face
                otherPos = math.floor(pos[2] / 2) + 4
                if self.cube[1][1][pos[2]] == self.cube[1][1][1] and self.cube[otherPos][1][2 - pos[2]] == self.cube[otherPos][1][1]: #It is in the correct place
                    if self.colourIndex < 3:
                        self.colourIndex += 1 #Go to next colour
                    else:
                        self.colourIndex = 0
                        self.stage += 1 #From 3 to 4
                        self.Z(2)
                        self.findOLLValue()
                else:
                    if pos[2] == 0:
                        self.L(1),self.D(3),self.L(3),self.X(3),self.D(3),self.R(3),self.D(1),self.R(1)
                    else:
                        self.R(3),self.D(1),self.R(1),self.X(1),self.D(1),self.L(1),self.D(3),self.L(3)
            else:
                self.rotateToSide(pos[0],W)

        else:
            self.rotateToSide(self.findSide(colourOrder[self.colourIndex]),W)        
        
        if self.stage < 4:
            for i in range(4):
                if self.cube[1][2][1] == self.cube[1][1][1] and self.cube[2][0][1] != Y:
                    if self.cube[2][0][1] == self.cube[4][1][1]:
                        self.D(1),self.L(1),self.D(3),self.L(3),self.X(3),self.D(3),self.R(3),self.D(1),self.R(1)
                    else:
                        self.D(3),self.R(3),self.D(1),self.R(1),self.X(1),self.D(1),self.L(1),self.D(3),self.L(3)
                self.D(1)
            self.findSidePiece(colourOrder[self.colourIndex],colourOrder[self.colourIndex + 1])

    def findOLLValue(self):
        for i in range(4):
            value = ''
            for x in OLLOrder:
                if self.cube[x[0]][x[1]][x[2]] == Y:
                    value += str(OLLOrder.index(x) + 1)
            try:
                OLL[value[:12]]
                self.doAlgorithm(OLL[value[:12]])              
                self.stage += 1 #From 4 to 5 
                self.findPLLValue()
                break
            except:
                self.U(1)

    def findPLLValue(self):
        for i in range(4):
            for s in range(4):
                value = ''
                for t in range(4):
                    for x in range(3):
                        value += str(self.findSide(self.cube[1][0][x]))
                    self.X(1)
                try: 
                    PLL[value[:6]]
                    self.doAlgorithm(PLL[value[:6]])
                    self.stage += 1
                    self.solved = True
                    self.cube = self.updateCube(self.originalCube)
                    self.newCube = self.updateCube(self.originalCube)
                    for i in range(3):
                        self.refineMovements(0,-1,self.movements[0])   
                    break
                except:
                    if not self.solved:
                        self.U(1)
            if not self.solved:
                self.X(1)

    def reserveSpot(self,pos,movement): #Reserves spot, ensures that a white piece is not already where the new piece will go // stage = 0
        while self.cube[pos[0]][pos[1]][pos[2]] == W: #While the position specified is white
            movement(1) #Perform the movement specified
                        
    def rotateToSide(self,pos,topCol): #Rotate to any side given the front and top colours
        if pos != 1: #If it is not already the front side
            rotateToSide[pos][0](rotateToSide[pos][1]) #Rotate to the side
        for i in range(4):
            if self.cube[0][1][1] == topCol: #If centre piece of top face == specified colour
                break #Stop loop
            self.Z(1) #Rotate

    def findSide(self,col):
        for i in range(6): #Checks through all sides
            if self.cube[i][1][1] == col: #If colours match
                return i #Return int value of side
    
    def moveSide(self,rotation,side,replace,rotateSide,ID): #Moves the individual colours to simulate the movement of the cube
        for i in range(rotation):
            if not self.solved:
                self.movements.append(ID)
            for t in range(6):
                try:
                    side[t]
                    for n in range(3):
                        self.newCube[t][replace[t][0][n]][replace[t][1][n]] = self.cube[side[t]][replace[side[t]][0][n]][replace[side[t]][1][n]] 
                        if StartStopButton.image ==  StartStopButton.solve:
                            self.originalCube[t][replace[t][0][n]][replace[t][1][n]] = self.cube[side[t]][replace[side[t]][0][n]][replace[side[t]][1][n]]
                except:
                    None
            if rotateSide != None: #Rotates a side
                for t in range(3):
                    for s in range(3):
                        if (t,s) != (1,1):
                            self.newCube[rotateSide][t][s] = self.cube[rotateSide][ROTATE_SIDE[(t,s)][0]][ROTATE_SIDE[(t,s)][1]]
                            if StartStopButton.image ==  StartStopButton.solve:
                                self.originalCube[rotateSide][t][s] = self.cube[rotateSide][ROTATE_SIDE[(t,s)][0]][ROTATE_SIDE[(t,s)][1]]

            self.cube = self.updateCube(self.newCube) #Updates the cube

    def changeMovements(self,count,val,startPos):
        if count % 4 == 3:
            val = val.swapcase()
            count = 1
        return val * (count % 4),startPos + (count % 4)

    def refineMovements(self,startPos,count,val):
        while (startPos + (count + 1)) < len(self.movements):
            count += 1
            if self.movements[startPos + count] != val:
                self.movements[startPos : startPos + count],startPos = self.changeMovements(count,val,startPos)
                count = 0        
            val = self.movements[startPos + count]
        self.movements[startPos : startPos + count + 1],startPos = self.changeMovements(count + 1,val,startPos)   
             
    def L(self,rotation):
        self.moveSide(rotation,{v: k for k, v in SIDES.items()},LEFT_PIECES,4,'L')
      
    def R(self,rotation):
        self.moveSide(rotation,SIDES,RIGHT_PIECES,5,'R')
     
    def M(self,rotation):
        self.moveSide(rotation,SIDES,MIDDLE_PIECES,None,'M')
     
    def U(self,rotation):
        self.moveSide(rotation,TOPSIDES,UP_PIECES,0,'U')
     
    def D(self,rotation):
        self.moveSide(rotation,{v: k for k, v in TOPSIDES.items()},DOWN_PIECES,2,'D')
     
    def A(self,rotation):
        self.moveSide(rotation,TOPSIDES,AIDDLE_PIECES,None,'A')
     
    def F(self,rotation):
        self.moveSide(rotation,FRONTSIDES,FRONT_PIECES,1,'F')
     
    def B(self,rotation):
        self.moveSide(rotation,{v: k for k, v in FRONTSIDES.items()},BACK_PIECES,3,'B')
     
    def C(self,rotation):
        self.moveSide(rotation,FRONTSIDES,CIDDLE_PIECES,None,'C')

    def X(self,rotation):
        self.moveSide(rotation,TOPSIDES,UP_PIECES,0,'X')                                
        self.moveSide(4 - rotation,{v: k for k, v in TOPSIDES.items()},DOWN_PIECES,2,'X')   
        self.moveSide(rotation,TOPSIDES,AIDDLE_PIECES,None,'X')                       

    def Y(self,rotation):
        self.moveSide(rotation,SIDES,RIGHT_PIECES,5,'Y')
        self.moveSide(4 - rotation,{v: k for k, v in SIDES.items()},LEFT_PIECES,4,'Y')
        self.moveSide(rotation,SIDES,MIDDLE_PIECES,None,'Y')

    def Z(self,rotation):
        self.moveSide(rotation,FRONTSIDES,FRONT_PIECES,1,'Z')
        self.moveSide(4 - rotation,{v: k for k, v in FRONTSIDES.items()},BACK_PIECES,3,'Z')
        self.moveSide(rotation,FRONTSIDES,CIDDLE_PIECES,None,'Z')
        
Cube = Cube()

class ArrowButton():
    def __init__(self,x,y,image,move):
        self.x = x
        self.y = y
        self.image = image
        self.move = move
        self.hitbox = pygame.Rect(self.x,self.y,84,84)
        self.onScreen = False
        
    def draw(self):
        if self.onScreen:
            gameDisplay.blit(self.image,[self.x,self.y])

    def function(self):
        if self.onScreen:
            self.move[0](self.move[1])

UpArrow = ArrowButton(918,200,pygame.image.load("upArrow.jpg").convert(),(Cube.Y,3))
DownArrow = ArrowButton(918,800,pygame.image.load("downArrow.jpg").convert(),(Cube.Y,1))
RightArrow = ArrowButton(1220,498,pygame.image.load("rightArrow.jpg").convert(),(Cube.X,1))
LeftArrow = ArrowButton(620,498,pygame.image.load("leftArrow.jpg").convert(),(Cube.X,3))
Arrows = [UpArrow,DownArrow,RightArrow,LeftArrow]

class ColourPalette():
    def __init__(self):
        self.enterIndex = 0 #Which front piece is selected (0 = top left, 8 = bottom right)
        self.sideIndex = 0 #Which side is it on
        self.image = pygame.image.load("colourPalette.jpg").convert() #Image file
        self.pos = (0,0) #The coordinate position of the selected piece
        self.onScreen = True #If currently on screen

    def draw(self):
        if self.onScreen: #If supposed to be on screen
            gameDisplay.blit(self.image,[1380,274]) #Draw image         
            pygame.draw.rect(gameDisplay,W,[767 + (self.pos[1] * 132),348 + (self.pos[0] * 132),128,128],2) #Draw white rectangle

    def clickedOn(self,pos): #If one of the piece buttons are clicked on (after colour input process)
        if self.onScreen: #If currently on screen
            if pos == self.pos: #If clicking on piece thats already selected
                self.onScreen = False #Close 
        else:
            self.onScreen = True #Otherwise appear on screen

ColourPalette = ColourPalette()

class ColourButton():
    def __init__(self,x,y,col):        
        self.x = x #x position
        self.y = y #y position
        self.col = col #The colour that it holds
        self.hitbox = pygame.Rect(self.x,self.y,150,150) #Hitbox that will detect if it is clicked       

    def function(self): #Function that is called when clicked
        if ColourPalette.onScreen: #If the colour selection panel is on the screen
            Cube.cube[1][ColourPalette.pos[0]][ColourPalette.pos[1]] = self.col #Set the new colour
            Cube.newCube[1][ColourPalette.pos[0]][ColourPalette.pos[1]] = self.col #Set the new colour
            Cube.originalCube[1][ColourPalette.pos[0]][ColourPalette.pos[1]] = self.col #Set the new colour

        if Cube.inputColours: #If on the colour input process
            if ColourPalette.enterIndex == 7: #If on final front piece
                ColourPalette.enterIndex = 0 #Go to first front piece
                ColourPalette.sideIndex += 1 #Next side
                if ColourPalette.sideIndex <= 3: #If less than 3 sides have been completed
                    Cube.X(3) #Rotate to next side
                elif ColourPalette.sideIndex == 4: # If 4 sides have been completed
                    Cube.Y(3) #Rotate to next side
                elif ColourPalette.sideIndex == 5: #If 5 sides have been completed
                    Cube.Y(2) #Rotate to next side
                
                elif ColourPalette.sideIndex == 6: #If on final side
                    Cube.Y(3) #Go back to original position
                    ColourPalette.sideIndex = 0 #Reset 
                    ColourPalette.onScreen = False #Turn off            
                    Cube.inputColours = False #No longer in colour input process
                    
                    for x in Arrows: #Arrows appear on screen
                        x.onScreen = True

            else:
                ColourPalette.enterIndex += 1 #If not on final front piece, go to next
            ColourPalette.pos = Pieces[ColourPalette.enterIndex].pos #Coordinate position of next front piece is set here           
                
WHITE  = ColourButton(1400,294,W)
YELLOW = ColourButton(1570,294,Y)
BLUE   = ColourButton(1400,464,B)
GREEN  = ColourButton(1570,464,G)
RED    = ColourButton(1400,634,R)
ORANGE = ColourButton(1570,634,O)
Colours = [WHITE,YELLOW,BLUE,GREEN,RED,ORANGE]

class PieceButton():
    def __init__(self,pos):
        self.x = 769 + (pos[1] * 128) #x position of each piece
        self.y = 348 + (pos[0] * 128) #y position of each piece
        self.pos = pos #Coordinate position of each piece
        self.hitbox = pygame.Rect(self.x,self.y,128,128) #Hitbox to check if clicked on
        self.onScreen = True #If currently on screen / True as default 

    def function(self): #Subroutine if clicked on
        if self.onScreen: #If currently on screen            
            ColourPalette.clickedOn(self.pos) #
            ColourPalette.pos = self.pos #Set coordinate position 

TL = PieceButton((0,0))
TM = PieceButton((0,1))
TR = PieceButton((0,2))
ML = PieceButton((1,0))
MR = PieceButton((1,2))
BL = PieceButton((2,0))
BM = PieceButton((2,1))
BR = PieceButton((2,2))
Pieces = [TL,TM,TR,ML,MR,BL,BM,BR]

class BannerButton():
    def __init__(self):
        self.x = 0
        self.hitbox = pygame.Rect(self.x,248,80,600)
        self.closed = pygame.image.load("movementBannerClosed.png").convert_alpha() #Image for closed
        self.open = pygame.image.load("movementBannerOpen.png").convert_alpha() #Image for opened
        self.progressBar = pygame.image.load("progressBar.jpg").convert() #Progress bar image
        self.image = self.closed #Closed by default
        self.motionOffset  = 0 #Current offset 
        self.motionSpeed = 1 #Speed of scrolling
        self.totalMoves = None #Total moves in array
        self.maxOffset = None #Maximum offset from all movements
        self.finished = False #If scrolling has finished
        
    def changeMotion(self,val):
        self.motionSpeed = val #Change speed value

    def checkOffset(self,speed):        
        pos1 = math.floor((self.motionOffset - 315) / 330) #See current value of top move
        pos2 = math.floor(((self.motionOffset - 315) - speed) / 330) #See value of top move in previous cycle
        if 0 <= (self.motionOffset + speed) <= self.maxOffset: #If next cycle doesnt go over offset limit
            self.motionOffset += speed #Add offset to current offset
            if pos1 != pos2 and pos1 >= 0: #If current value is not equal to previous value 
                if speed < 0: #If manually scrolling backwards
                    if pos1 > 0: #If movement is still in range
                        movements[Cube.movements[pos1 - 1].swapcase()][0](movements[Cube.movements[pos1 - 1].swapcase()][1])
                        #Perform the inverse of the previous movement in list
                else: #If scrolling forwards (manually or not)
                    if pos1 < self.totalMoves: #If movement is still in range
                        movements[Cube.movements[pos1]][0](movements[Cube.movements[pos1]][1]) 
                        #Perform next movement in list
                Cube.drawCube() #Update the cube to show the movement performed
                
    def drawMovements(self):
        self.draw() #Draw banner
        if self.image == self.open: #If the banner is open
            if Cube.solved: #If the cube is solved
                gameDisplay.blit(self.progressBar,[430,950]) #Display the progress bar image
                pygame.draw.rect(gameDisplay,G,[440,960,math.floor(1440 * (self.motionOffset/self.maxOffset)),80])
                #Display the progress bar rectangle
                for i in range(len(Cube.movements)): #For every movement 
                    if -300 < (345 + (330 * i)) - self.motionOffset < 1080: #If the movement is on the screen
                        gameDisplay.blit(movements[Cube.movements[i]][2],[50,(345 + (330 * i)) - self.motionOffset]) 
                        #Display the movement 
                if not self.finished: #If the scrolling mechanism is not finished
                    if self.motionOffset + self.motionSpeed >= self.maxOffset: #If the next cycle will go over the offset limit
                        self.finished = True #They scrolling process is complete
                        StartStopButton.image = StartStopButton.reset #Change button to reset
                        StartStopButton.draw() #Update the button now that its image has changed
                        self.motionOffset = self.maxOffset #Set it to max so that it doesnt go over
                    elif StartStopButton.image == StartStopButton.pause: #Else if it is not finished but also not paused                
                        self.checkOffset(self.motionSpeed) #Check to see if a movement has occured
                            
    def draw(self):
        gameDisplay.blit(self.image,[0,0])        

    def changeButtons(self):
        for x in (Arrows + Pieces + PlayButtons):
            if Cube.solved == True and x not in PlayButtons:
                x.onScreen = False
            else:
                x.onScreen = not x.onScreen
        ColourPalette.onScreen = False

    def function(self): #When clicked on
        if self.x == 0: #If 
            self.x = 360
            self.image = self.open
            self.changeButtons()
        else:
            self.x = 0
            if StartStopButton.image == StartStopButton.pause:
                StartStopButton.function()
            self.image = self.closed
            self.changeButtons()
        self.hitbox = pygame.Rect(self.x,248,80,600)
BannerButton = BannerButton()

class StartStopButton():
    def __init__(self):
        self.hitbox = pygame.Rect(460,20,84,84) #Image hitbox
        self.solve = pygame.image.load("solveButton.jpg").convert() #Button to solve
        self.play = pygame.image.load("playButton.jpg").convert() #Button to start
        self.pause = pygame.image.load("pauseButton.jpg").convert() #Button to pause
        self.reset = pygame.image.load("resetButton.jpg").convert() #Button to reset cube
        self.image = self.solve #Button image is set to solve by default
        self.onScreen = False #Not on screen by default

    def draw(self): 
        if self.onScreen: #If currently on screen
            gameDisplay.blit(self.image,[460,20]) #Draw image

    def restartCube(self): #Reset cube at the end
        Cube.rotateToSide(Cube.findSide(O),Y)
        for i in range(6): #For every side on the cube
            for t in range(3): #For every row
                for s in range(3): #For every column
                    if (t,s) != (1,1): #If not a centrepiece
                        Cube.cube[i][t][s] = BLACK #Reset to black 
                        Cube.newCube[i][t][s] = BLACK #Reset to black
                        Cube.originalCube[i][t][s] = BLACK  #Reset to black
        Cube.colourIndex = 0 
        Cube.inputColours = True #Input colour process now true
        Cube.solved = False #Cube no longer solved
        Cube.stage = 0 #Stage of cube set to 0
        BannerButton.finished = False
        BannerButton.function()
        BannerButton.motionOffset  = 0
        ColourPalette.pos = (0,0)
        ColourPalette.onScreen = True
        for x in Arrows: #Arrows no longer visible on screen
            x.onScreen = False

    def function(self): #When button is clicked on
        if self.image == self.solve: #If cube is unsolved
            if Cube.checkIntegrity(): #Check integrity of cube
                Cube.rotateToSide(Cube.findSide(B),Y) #Ensure starting orientation is correct
                Cube.movements = [] #Reset movements array
                self.image = self.play #Button is changed to play/pause
                Cube.findSidePiece(W,colourOrder[Cube.colourIndex]) #Initiate solution process
                BannerButton.maxOffset = (len(Cube.movements) + 1) * 330 #Maxmimum offset defined here
                BannerButton.totalMoves = len(Cube.movements) #Total moves defined here
        elif self.image == self.play: #If scrolling is paused
            BannerButton.changeMotion(math.floor(SpeedBarButton.barLength/45) + 1) 
            #Scrolling process starts/continues with original speed
            self.image = self.pause #Change image to show it is on
        elif self.image == self.pause: #If scrolling in on
            BannerButton.changeMotion(0) #Scrolling process is paused by changing speed to 0                       
            self.image = self.play #Change image to show it is paused
        else: #If the image is reset 
            self.image = self.solve #Set image back to original
            self.restartCube() #Restart the cube 
StartStopButton = StartStopButton()

class SpeedBarButton():
    def __init__(self):
        self.barLength = 10 #Length of initial bar
        self.hitbox = pygame.Rect(465,129,240,74) #Button hitbox
        self.image = pygame.image.load("speedBar.jpg").convert() #Image for button
        self.onScreen = False #If currently on screen
        self.clickedOn = False #If button is clicked on

    def changeValues(self):
        if self.clickedOn: #If button is clicked on
            if self.hitbox.collidepoint(pygame.mouse.get_pos()): #If mouse is still hovering over the button
                self.barLength = pygame.mouse.get_pos()[0] - 460 #Change bar length            
                BannerButton.changeMotion(math.floor(self.barLength/45) + 1) #Change motion speed
                
    def draw(self):
        if self.onScreen: #If currently on screen
            gameDisplay.blit(self.image,[460,124]) #Draw base of button
            pygame.draw.rect(gameDisplay,GRAY,[465,129,self.barLength,74]) #Draw rectangle representing speed

    def function(self): #When clicked on (or click is released)
        self.clickedOn =  not self.clickedOn #Change clickedOn value
SpeedBarButton = SpeedBarButton()

PlayButtons = [StartStopButton,SpeedBarButton]

Buttons = [UpArrow,DownArrow,RightArrow,LeftArrow,TL,TM,TR,ML,MR,BL,BM,BR,WHITE,YELLOW,BLUE,GREEN,RED,ORANGE,BannerButton,StartStopButton,SpeedBarButton]

rotateToSide = {
    0 : (Cube.Y,3),
    2 : (Cube.Y,1),
    3 : (Cube.X,2),
    4 : (Cube.X,3),
    5 : (Cube.X,1)
    }

OLL = { 
    '289121314161' : ('L','U','l','U','L','U','U','l'), #L U L' U [L U2 L']
    '478121314182' : ('r','u','R','u','r','U','U','R'), #R' U' R U' R' U2 R
    '248121314182' : ('R','U','U','r','u','R','U','r','u','R','u','r'), #R U2 R' U' R U R' U' R U' R'
    '468121314161' : ('R','U','U','R','R','u','R','R','u','R','R','U','U','R'), #R U2' [R2 U'] [R2 U'] R2 U2' R
    '789121314182' : ('R','R','D','r','U','U','R','d','r','U','U','r'), #R2 D [R' U2 R] D' [R' U2 R']
    '478121314171' : ('l','M','u','L','U','R','u','r','m','F'), #l' U' L U R U' [r' F]
    '781012131418' : ('r','F','R','b','r','f','R','B'), #[R' F R B'] [R' F' R B]
    '361011131516' : ('R','U','U','R','R','F','R','f','U','U','r','F','R','f'), #R U2 [R2' F R F'] U2' [R' F R F']
    '346111315162' : ('F','R','U','r','u','C','R','U','r','u','f','c'), #[F R U R' U' F'] [f R U R' U' f']
    '231011131516' : ('F','C','R','U','r','u','f','c','u','F','R','U','r','u','f'), #(f R U R' U' f') U' (F R U R' U' F')
    '369111315202' : ('F','C','R','U','r','u','f','c','U','F','R','U','r','u','f'), #(f R U R' U' f') U (F R U R' U' F')
    '347111315161' : ('R','U','r','U','r','F','R','f','U','U','r','F','R','f'), #[R U R' U] [R' F R F'] U2 [R' F R F']
    '379111315171' : ('m','U','R','U','r','u','M','M','U','R','u','r','m'), #M U R U R' U' M2 [U R U' r']
    '234111315171' : ('F','R','U','r','U','x','r','U','U','r','F','R','F'), #	[F R U R' U] y' R' U2 [R' F R F']
    '379111315162' : ('m','U','R','U','r','u','M','r','F','R','f'), #M U [R U R' U'] M' [R' F R F'] 
    '781011131517' : ('r','u','r','F','R','f','U','R'), #R' U' [R' F R F'] U R
    '361012131417' : ('R','U','R','R','u','r','F','R','U','R','u','f'), #R U R2 U' R' F R U R U' F'
    '681011131516' : ('R','U','U','R','R','u','R','u','r','U','U','F','R','f'),  #R U2 R2 U' R U' R' U2 F R F',m
    '281011131518' : ('R','U','r','U','R','d','A','R','u','r','f'), #R U R' U R d' R U' R' F'   
    '346121314162' : ('F','C','R','U','r','u','R','U','r','u','f','c'), #f [R U R' U'] [R U R' U'] f'
    '361012131416' : ('F','R','U','r','u','R','f','R','M','U','r','u','r','m'), #[F R U R' U' R] F' [r U R' U'] r'
    '468121315162' : ('F','R','U','r','u','R','U','r','u','f'), #F [R U R' U'] [R U R' U'] F'
    '281011131420' : ('r','u','r','F','R','f','r','F','R','f','U','R'), #R' U' [R' F R F'] [R' F R F'] U R
    '681011131416' : ('R','M','U','r','U','R','u','r','U','R','U','U','r','m'), #[r U R' U] [R U' R' U] [R U2' r']
    '681012131516' : ('l','M','u','L','u','l','U','L','u','l','U','U','L','m'), #[l' U' L U'] [L' U L U'] [L' U2 l]
    '468111314162' : ('r','F','r','f','R','R','U','U','X','r','F','R','f'), #[R' F R' F'] R2 U2' y [R' F R F']	  
    '281012131520' : ('r','F','R','R','b','R','R','f','R','R','B','r'), #R' F R2 B' R2' F' R2 B R'  
    '369111314161' : ('F','C','R','U','r','u','f','c'), #f [R U R' U'] f'
    '371012131517' : ('f','c','l','u','L','U','F','C'), #f' (L' U' L U) f
    '239111314181' : ('R','U','b','u','r','U','R','B','r'), #R U B' U' R' U R B R'
    '289111314192' : ('r','u','F','U','R','u','r','f','R'), #[R' U'] F [U R U' R'] F' R
    '369121314161' : ('F','R','U','r','u','f'), #F [R U R' U'] F'
    '239121314192' : ('R','U','r','u','r','F','R','f'), #[R U R' U'] [R' F R F']
    '289121315172' : ('R','U','r','U','R','u','r','u','r','F','R','f'), #[R U R' U] [R U' R' U'] [R' F R F']
    '478111314161' : ('l','u','L','u','l','U','L','U','L','f','l','F'), #[L' U' L U'] [L' U L U] [L F' L' F]
    '379111314161' : ('R','R','U','r','b','R','u','R','R','U','R','B','r'), #R2 U R' B' R U' R2 U R B R'
    '379121315161' : ('m','U','R','U','r','u','r','F','R','f','M'), #M U [R U R' U'] [R' F R F'] M'
    '379111314182' : ('R','u','r','U','U','R','U','X','R','u','r','u','f'), #[R U' R' U2] R U y R U' R' U' F'
    '689121315161' : ('r','U','U','R','U','r','U','R','X','F','R','U','r','u','f'), #R' U2 [R U R' U] R y [F R U R' U' F']  
    '781012131519' : ('F','R','u','r','u','R','U','r','f'), #F R U' R' U' R U R' F'
    '371011131418' : ('R','U','U','R','R','F','R','f','R','U','U','r'), #R U2' [R2 F R F'] [R U2 R']
    '239121315161' : ('R','U','r','U','r','F','R','f','R','U','U','r'), #[R U R' U] [R' F R F'] [R U2 R'] 
    '468121315192' : ('R','U','r','u','r','F','R,R','U','r','u','f'), #[R U R' U' R' F] R2 U R' U' F'
    '231012131417' : ('R','M','u','r','m','u','R','M','u','r','m','x','r','U','R'), #r U' r' U' r U r' y' [R' U R]         
    '346121314192' : ('r','F','R','U','r','f','R','x','R','u','r'), #R' F R U R' F' R y' [R U' R'] 
    '369121314202' : ('R','M','U','r','m','R','U','r','u','R','M','u','r','m'), #[r U r'] [R U R' U'] [r U' r']
    '371012131416' : ('l','M','u','L','m','l','u','L','U','l','M','U','L','m'), #[l' U' l] [L' U' L U] [l' U l]
    '347121314161' : ('r','F','R','U','r','u','f','U','R'), #[R' F R U R' U' F'] U R
    '239121314172' : ('L','f','l','u','L','U','F','u','l'), #[L F' L' U' L U F] U' L'
    '468111314192' : ('R','U','U','r','U','U','r','F','R','f'), #R U2' R' U2 R' F R F'
    '281012131517' : ('R','M','U','r','U','R','U','U','r','m'), #[r U R' U] [R U2' r']
    '369111314182' : ('F','R','U','r','u','f','U','F','R','U','r','u','f'), #[F R U R' U' F'] U [F R U R' U' F']
    '371012131516' : ('f','l','u','L','U','F','X','F','R','U','r','u','f'), #[F' L' U' L U F] y [F R U R' U' F']
    '689111314202' : ('R','M','U','U','r','u','R','u','r','m'), #r U2' R' U' R U' r'
    '781012131516' : ('l','M','U','U','L','U','l','U','L','m'), #l' U2 L U L' U l
    '379111314171' : ('M','U','m','U','U','M','U','m'), #M' U M U2 M' U M
    '379121314171' : ('R','U','r','u','M','U','R','u','r','m') #[R U R' U'] M' [U R U' r']
    }

PLL = {
    '151131' : ('R','u','R','U','R','U','R','u','r','u','R','R'), #[R U' R] U R U R U' R' U' R2
    '141141' : ('R','R','U','R','U','r','u','r','u','r','U','r'), #R2 U R U R' U' R' U' R' U R'
    '151141' : ('U','r','u','R','u','R','U','R','u','r','U','R','U','R','R','u','r','U'), #[U R' U'] R U' R U R U' R' U R U [R2 U' R' U]
    '131131' : ('M','M','U','M','M','U','U','M','M','U','M','M'), #M2 U M2 U2 M2 U M2    
    '113314' : ('l','M','U','r','D','D','R','u','r','D','D','R','R'), #l' U R' D2 R U' R' D2 R2
    '515513' : ('L','m','u','R','D','D','r','U','R','D','D','R','R'), #l U' R D2 R' U R D2 R2
    '415514' : ('y','R','u','r','D','R','U','r','d','R','U','r','D','R','u','r','d'), #x' [R U' R' D] [R U R' D'] [R U R' D] [R U' R' D']
    '115534' : ('R','U','r','u','r','F','R','R','u','r','u','R','U','r','f'), #[R U R' U'] R' F R2 U' R' U' [R U R' F']    
    '111135' : ('r','U','R','u','R','R','x','r','u','R','U','X','Y','R','U','r','u','R','R','y','u'), #[R' U R U'] R2 y' [R' U' R U] y x [R U R' U'] [R2 x U']
    '111115' : ('r','U','l','U','U','R','u','r','U','U','L','R','u'), #[R' U L'] U2 [R U' R' U2] [L R U']
    '155544' : ('R','U','r','f','R','U','r','u','r','F','R','R','u','r','u'), #[R U R' F'] [R U R' U' R' F] [R2 U' R' U']
    '141115' : ('L','U','U','l','U','U','L','f','l','u','L','U','L','F','L','L','U'), #[L U2' L' U2'] L F' L' U' L U L F L2' U
    '151145' : ('r','U','U','R','U','U','r','F','R','U','r','u','r','f','R','R','u'), #[R' U2 R U2] R' F R U R' U' R' F' R2 U'    
    '113351' : ('r','U','r','u','Y','Y','x','r','U','r','u','L','m','R','u','r','U','R','U'), #[R' U R' U'] [x2 y'] [R' U R' U'] [l R U'] [R' U R] U
    '113311' : ('F','R','u','r','u','R','U','r','f','R','U','r','u','r','F','R','f'), #[F R U' R' U' R U R' F'] [R U R' U'] [R' F R F']
    '133311' : ('L','u','R','U','U','l','U','r','L','u','R','U','U','l','U','r','U'), #{L U' R U2 L' U R'} {L U' R U2 L' U R'} U
    '331113' : ('r','U','l','U','U','R','u','L','r','U','l','U','U','R','u','L','u'), #{R' U L' U2 R U' L} {R' U L' U2 R U' L} U'
    '411153' : ('R','R','U','A','r','U','r','u','R','u','a','R','R','x','r','U','R'), #[R2 u] R' U R' U' R u' R2 y' [R' U R]
    '135545' : ('l','u','L','x','R','R','U','A','r','U','R','u','R','u','a','R','R'), #[L' U' L] y' {R2 u R' U R U' R u' R2}
    '543341' : ('R','R','u','a','R','u','R','U','r','U','A','R','R','X','R','u','r'), #[R2 u'] R U' R U R' u R2 y [R U' R']
    '431113' : ('R','U','r','x','R','R','u','a','R','u','r','U','r','U','A','R','R') #[R U R'] y' R2 u' R U' R' U R' u R2
    }

movements = {
    'L' : (Cube.L,1,pygame.image.load("L1.jpg").convert()),
    'l' : (Cube.L,3,pygame.image.load("L3.jpg").convert()),
    'R' : (Cube.R,1,pygame.image.load("R1.jpg").convert()),
    'r' : (Cube.R,3,pygame.image.load("R3.jpg").convert()),
    'M' : (Cube.M,1,pygame.image.load("M1.jpg").convert()),
    'm' : (Cube.M,3,pygame.image.load("M3.jpg").convert()),
    'U' : (Cube.U,1,pygame.image.load("U1.jpg").convert()),
    'u' : (Cube.U,3,pygame.image.load("U3.jpg").convert()),
    'D' : (Cube.D,1,pygame.image.load("D1.jpg").convert()),
    'd' : (Cube.D,3,pygame.image.load("D3.jpg").convert()),
    'A' : (Cube.A,1,pygame.image.load("A1.jpg").convert()),
    'a' : (Cube.A,3,pygame.image.load("A3.jpg").convert()),
    'F' : (Cube.F,1,pygame.image.load("F1.jpg").convert()),
    'f' : (Cube.F,3,pygame.image.load("F3.jpg").convert()),
    'B' : (Cube.B,1,pygame.image.load("B1.jpg").convert()),
    'b' : (Cube.B,3,pygame.image.load("B3.jpg").convert()),
    'C' : (Cube.C,1,pygame.image.load("C1.jpg").convert()),
    'c' : (Cube.C,3,pygame.image.load("C3.jpg").convert()),
    'X' : (Cube.X,1,pygame.image.load("X1.jpg").convert()),
    'x' : (Cube.X,3,pygame.image.load("X3.jpg").convert()),
    'Y' : (Cube.Y,1,pygame.image.load("Y1.jpg").convert()),
    'y' : (Cube.Y,3,pygame.image.load("Y3.jpg").convert()),
    'Z' : (Cube.Z,1,pygame.image.load("Z1.jpg").convert()),
    'z' : (Cube.Z,3,pygame.image.load("Z3.jpg").convert())
    }

while not gameExit:  
    for event in pygame.event.get():             
        gameDisplay.blit(background,[0,0])         
        Cube.drawCube()
        ColourPalette.draw()
        for x in Arrows:
                x.draw()              
        StartStopButton.draw()
        SpeedBarButton.draw()
        BannerButton.draw()
        if BannerButton.image == BannerButton.open:
            SpeedBarButton.changeValues()  
        if Cube.showTutorial and BannerButton.image == BannerButton.closed:
            Cube.drawTutorial()
        
        if event.type == pygame.KEYDOWN:           
            if event.key == pygame.K_ESCAPE:
                gameExit = True  
            elif event.key == pygame.K_t:
                Cube.displayTutorial()

            elif event.key == pygame.K_r:
                StartStopButton.restartCube()

        elif event.type == pygame.MOUSEBUTTONDOWN: 
            if event.button == 1:   
                Cube.showTutorial = False
                for x in Buttons:
                    if x.hitbox.collidepoint(pygame.mouse.get_pos()):    
                        if not Cube.inputColours or x in Colours:
                            x.function()

            elif event.button == 4: #Scroll up
                if BannerButton.finished and pygame.mouse.get_pos()[0] <= 360: #If on manual scroll
                    BannerButton.checkOffset(-330) #Perform inverse of previous move                
                elif Cube.showTutorial: #If tutorial is on the screen
                    Cube.scrollTutorial(120) #Increase offset


            elif event.button == 5: #Scroll down
                if BannerButton.finished and pygame.mouse.get_pos()[0] <= 360: #If on manual scroll
                    BannerButton.checkOffset(330) #Perform next move                
                elif Cube.showTutorial: #If tutorial is on the screen
                    Cube.scrollTutorial(-120) #Decrease offset

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            SpeedBarButton.clickedOn = False

    if Cube.solved and BannerButton.image == BannerButton.open:
        BannerButton.drawMovements()
 
    pygame.display.update()         
    clock.tick(120)
pygame.quit()

