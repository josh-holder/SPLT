"""
Replay a sequence, with visual cues about where it and the algorithm differ.
"""

from weighting import findWeights
from weighting_new import doesPointBlockCauseNewHalving, doesUnexpectedClusterForm
import core_update as core
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen,QBrush
from PyQt5.QtCore import QRect, Qt


##########################################
class gameBoardDisplay(QWidget):
##########################################
    
    def __init__(self,gameBoard):
        super().__init__()

        self.minimumTileSize=40
        self.initUI(gameBoard)
        self.gameBoard=gameBoard
        self.nextHighlightedBox=0
        self.algoHighlightedBoxes=[]
        self.newHalvingBoxes = []
        self.newUnexpectedClusterBoxes = []
        
    def initUI(self,gameBoard):      

        self.setGeometry(300, 300, self.minimumTileSize*gameBoard.width, self.minimumTileSize*gameBoard.height)
        self.setWindowTitle('Score: {0}\tSplits:{1}'.format(gameBoard.score,len(gameBoard.splitRecord)))
        self.show()
        
    def Update(self,gameBoard):
        self.gameBoard=gameBoard
        self.setWindowTitle('Score: {0}\tSplits:{1}'.format(gameBoard.score,len(gameBoard.splitRecord)))
        self.update()

    def HighlightNextBox(self,nextHighlightedBox):
        self.nextHighlightedBox=nextHighlightedBox

    def HighlightAlgoBoxes(self,algoHighlightedBoxes):
        self.algoHighlightedBoxes=algoHighlightedBoxes

    def PaintBoxesWhichCauseNewHalvings(self, newHalvingBoxes):
        self.newHalvingBoxes = newHalvingBoxes
    
    def PaintBoxesWhichCauseUnexpectedClusters(self, newUnexpectedClusterBoxes):
        self.newUnexpectedClusterBoxes = newUnexpectedClusterBoxes

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)

        self.drawBackground(qp)

        for boxIndex,box in enumerate(self.gameBoard.box):
            if (boxIndex in self.newHalvingBoxes) and (boxIndex in self.newUnexpectedClusterBoxes):
                self.drawBox(qp,box.x,box.y,box.width,box.height,boxIndex,box.points,QColor(150, 150, 0))
            elif (boxIndex in self.newHalvingBoxes):
                self.drawBox(qp,box.x,box.y,box.width,box.height,boxIndex,box.points,QColor(0, 150, 0))
            elif (boxIndex in self.newUnexpectedClusterBoxes):
                self.drawBox(qp,box.x,box.y,box.width,box.height,boxIndex,box.points,QColor(150, 0, 0))
            else:
                self.drawBox(qp,box.x,box.y,box.width,box.height,boxIndex,box.points,QColor(150, 150, 150))

            if (boxIndex==self.nextHighlightedBox) and (boxIndex in self.algoHighlightedBoxes):
                self.drawBoxHighlight(qp,box.x,box.y,box.width,box.height,Qt.green)
            elif boxIndex==self.nextHighlightedBox:
                self.drawBoxHighlight(qp,box.x,box.y,box.width,box.height,Qt.red)
            elif boxIndex in self.algoHighlightedBoxes:
                self.drawBoxHighlight(qp,box.x,box.y,box.width,box.height,Qt.blue)

        qp.end()
    
    def drawBackground(self,qp):

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor(230, 230, 230))
        qp.setBrush(brush)

        rect1=QRect(0, 0, self.minimumTileSize*self.gameBoard.width, self.minimumTileSize*self.gameBoard.height)
        qp.drawRect(rect1)  

    def drawBox(self,qp,x,y,width,height,index,points,color):
        
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(color)
        qp.setBrush(brush)

        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)

        rect1=QRect(x*self.minimumTileSize, y*self.minimumTileSize, width*self.minimumTileSize, height*self.minimumTileSize)

        if points>0:
            brush.setStyle(Qt.Dense2Pattern)
            qp.setBrush(brush)
            qp.drawRect(rect1)             
            qp.drawText(rect1, Qt.AlignCenter,"[{0}]\n{1}".format(index,points))    
        else:
            qp.drawRect(rect1) 
            qp.drawText(rect1, Qt.AlignCenter,"[{0}]".format(index)) 
   
    def drawBoxHighlight(self,qp,x,y,width,height,color):

        brush = QBrush()
        brush.setStyle(Qt.NoBrush)
        qp.setBrush(brush)

        pen = QPen(color, 8, Qt.DashLine)
        qp.setPen(pen)

        rect1=QRect(x*self.minimumTileSize, y*self.minimumTileSize, width*self.minimumTileSize, height*self.minimumTileSize)
        qp.drawRect(rect1)

##########################################
def replaySequence(graphicalDisplay,sequence):
##########################################
    gameBoard=core.Board(8,16)
    
    while 1:

        moveOptions=gameBoard.getMoveOptions()

        if len(moveOptions)==0:
            return gameBoard.score,gameBoard.splitRecord
            break

        try: nextMove=sequence[len(gameBoard.splitRecord)]
        except IndexError: pass
        
        print("Move {0} of {1}: Split box #{2}".format(len(gameBoard.splitRecord),len(sequence),nextMove))

        #determine best moves
        best_indices = [i for i, x in enumerate(gameBoard.weights) if x == max(gameBoard.weights)]

        graphicalDisplay.HighlightNextBox(nextMove)
        graphicalDisplay.HighlightAlgoBoxes(best_indices)
        newHalvingOptions = []
        unexpectedClusterOptions = []
        for boxIndex in moveOptions:
            if doesPointBlockCauseNewHalving(gameBoard, boxIndex): newHalvingOptions.append(boxIndex)
            if doesUnexpectedClusterForm(gameBoard, boxIndex): unexpectedClusterOptions.append(boxIndex)
        graphicalDisplay.PaintBoxesWhichCauseNewHalvings(newHalvingOptions)
        graphicalDisplay.PaintBoxesWhichCauseUnexpectedClusters(unexpectedClusterOptions)

        graphicalDisplay.Update(gameBoard)
        
        userinput=input("Press any key to continue")
        if nextMove not in moveOptions:
            print("------ IMPOSSIBLE MOVE REQUESTED -----")
            break

        if gameBoard.weights[nextMove] != max(gameBoard.weights):
            print("~~~Made move not recommended by algorithm.~~~")
            indices = [i for i, x in enumerate(gameBoard.weights) if x == max(gameBoard.weights)]
            print("Box(es) recommended:")
            print(indices)
            print("Weight of box(es) recommended:")
            print(max(gameBoard.weights))
            print("Weight of box chosen:")
            print(gameBoard.weights[nextMove])
            # print(gameBoard.weights)

        if userinput == "w":
            findWeights(gameBoard,weightverbose=1)
            userinput=input("Press any key to continue")

        core.makeMove(gameBoard,nextMove)       

##########################################
if __name__ == '__main__':
##########################################
    try:
        sequenceFile=sys.argv[1]
    except:
        print("Didn't get the parameters I expected.\n\nExpected usage is replay.py <sequence filename>\n")
        sys.exit(1)

    print("\n--------Replay SPL-T--------\n")

    try:
        f = open(sequenceFile, "r")
    except:
        print("Couldn't open file",sequenceFile,", does it exist?")
        sys.exit(1)

    line=f.readline()
    f.close()
    if line[0] == "[": line = line[1:]
    if line[-1] == "]": line = line[:-1]
    sequence=(line.rstrip('\n').split(', '))
    sequence=[int(ii) for ii in sequence]

    print("This sequence has a length of",len(sequence))
    

    app = QApplication(sys.argv)

    gameBoard=core.Board(8,16)    

    graphicalDisplay = gameBoardDisplay(gameBoard)

    score,path=replaySequence(graphicalDisplay,sequence)

    print("\tScore: ",score,"\tLength: ",len(path))

    sys.exit(app.exec_())