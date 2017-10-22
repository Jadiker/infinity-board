from tkinter import *
import time
from FinalNeuralNet import makeNet, normalizeDataIntoNd


class Game():
    def __init__(self):
        self.runGame = False
        self.loopNumber = 0
        #in the form [(n1, m1), (n2, m2), ...]
        self.networkInfos = []
        self.gameHasStarted = False

    def loop(self):
        if self.loopNumber == 0:
            dg.getData()
        # print("Done and value: {} {}".format(dg.done, dg.returnValue))
        # print("before check", self.runGame)
        if dg.done and self.runGame == False:
            # print(self.runGame)
            print("training...")
            print(dg.returnValue)
            n1, m1 = makeNet(dg.returnValue)
            print("Training complete!")
            print("Data points 1 and 3:")
            print(n1(normalizeDataIntoNd([dg.returnValue[0][0]], m1)))
            print(n1(normalizeDataIntoNd([dg.returnValue[0][2]], m1)))
            self.networkInfos.append((n1, m1))
            self.runGame = True
        if self.runGame and not self.gameHasStarted: #training is done
            root.after(0, dg.listen)
            self.gameHasStarted = True
        # print("runGame afterwards!!!! {}".format(self.runGame))
            
        self.loopNumber+=1
        root.after(3000, self.loop)

def keyup(e):
    #print ('up', e.char)
    global key
    if key == e.char:
        key = None

def keydown(e):
    global key
    key = e.char
    #print("Keydown: {}".format(e.char))
    
def getBigLastUserInput():
    global key
    global dg
    global userArray
    userArray.append(dg.charToNum(key))			 
    userArray.pop(0)
    return userArray

# TODO delete if not used
def resetBigLastUserInput():
    global userArray
    # print("trying to reset")
    userArray = [0] * 500

def lastKey():
    global key
    #print("Returning last key: {}".format(key))
    return key

class DataGetter:
    def __init__(self, root):
        self.goodAmt = 3
        self.badAmt = 3
        self.samples = 500 #if edited during runtime, need to run updateFrequency
        self.runTime = 5 #if edited during runtime, need to run updateFrequency
        self.frequency = None
        self.updateFrequency()
        self.examples = []
        # during training, this is the example put in by user
        # during gameply, this is the user input
        self.curExample = []
        # during training, these are the training labels (0 or 1) (e.g. [1, 1, 0])
        # during gameplay, this is the controls (e.g. ["right", "left"])
        self.targets = []
        self.state = 0
        self.samplesLeft = 0
        self.root = root
        self.done = True
        # (self.examples, self.targets)
        self.returnValue = None

    def updateFrequency(self):
        self.frequency = round((self.samples * 1.0) / self.runTime)

    def getData(self):
        if self.state < self.goodAmt:
            if self.state == 0:
                self.done = False
            else:
                self.examples.append(self.curExample)
            self.samplesLeft = self.samples
            print("give a good example")
            self.root.after(0, self.getExample)
            return
        elif self.state < self.goodAmt + self.badAmt:
            self.examples.append(self.curExample)
            self.samplesLeft = self.samples
            print("give a bad example")
            self.root.after(0, self.getExample)
            return
        else:
            self.examples.append(self.curExample)
            self.state = 0
            self.targets = []
            for i in range(self.goodAmt):
                self.targets.append(10)
            for i in range(self.badAmt):
                self.targets.append(-10)
            # print("Targets: {}".format(self.targets))
            self.returnValue = (self.examples, self.targets)
            self.done = True
            return
    
    def listen(self):
        # print("I am alive!")
        # print("state: {}".format(self.state))
        # time.sleep(5)
        if self.state == 0:
            self.samplesLeft = self.samples
            self.state = -1
            # print("About to call self.getExample:")
            # time.sleep(5)
            self.root.after(0, self.getExample)
            return
        else: #got something back
            self.state = 0
            self.root.after(0, self.inputToControl)
            return
        
    def inputToControl(self):
        # print("just got inside inputToControl")
        # time.sleep(5)
        threshold = 0
        # print("ui:\n{}".format(ui))
        self.targets = []
        # if our "right" network fires
        netValue = runNet(game.networkInfos[0], self.curExample)
        print("Net value: {}".format(netValue))
        if netValue > threshold:
            # print("Should move!")
            self.targets.append("right")
        #print("about to call the ball move")
        # time.sleep(5)
        self.root.after(0, ball1.move_ball)
        
            
    def getExample(self):
        if self.samplesLeft > 0:
            if self.samplesLeft == self.samples:
                self.curExample = []
                if lastKey() == None:
                    root.after(5, self.getExample)
                    return
            #print("curExample: {}".format(self.curExample))
            self.curExample.append(self.charToNum(lastKey()))
            self.samplesLeft -= 1
            # timeConstant = 10 #must be an integer
            # root.after(self.frequency*timeConstant, self.getExample)
            root.after(5, self.getExample)
            return
        else: #all done
            if self.state >= 0: #if I was called by self.getData
                # print("increasing state by 1")
                self.state += 1
                root.after(0, self.getData)
                return
            else: #I was called by self.listen
                root.after(0, self.listen)
                return
        
    
    def charToNum(self, c):
        if c==None:
            return 0
        else:
            return ord(c)

# value is in the form [1, 2, 3,4 , 5, 2, 3,4 ,4, ...]
# netInfo is in the form (n1, m1)
def runNet(netInfo, value):
    # print("net info", netInfo)
    return ((netInfo[0](normalizeDataIntoNd([value], netInfo[1])))[0][0]).asscalar()

# TODO
# get the user input, convert it into a list of commands using the neural networks
def getUserControl():
    threshold = .5
    ui = getBigLastUserInput()
    # print("ui:\n{}".format(ui))
    controls = []
    # if our "right" network fires
    netValue = runNet(game.networkInfos[0], ui)
    print("Net value: {}".format(netValue))
    if netValue > threshold:
        # print("Should move!")
        controls.append("right")
        #resetBigLastUserInput()
        # print("Reset:\n{}".format(getBigLastUserInput()))
    return controls

class Ball:
    def __init__(self, canvas, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.canvas = canvas
        self.ball = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill="red")

    def move_ball(self):
        returnTime = 5 # milliseconds
        ballSpeed = 50
        if game.runGame:
            # print("hi\n")
            # x = input("give me a key: ")
            x = dg.targets
            if "left" in x:
                self.canvas.move(self.ball, -ballSpeed, 0)
            elif "right" in x:
                print("I LIKE TO MOVE IT MOVE IT!!!!")
                self.canvas.move(self.ball, ballSpeed, 0)
            # print("If I die here, you know who's to blame.")
            # time.sleep(5)
            # print("setting the state to 0")
            dg.state = 0
            root.after(0, dg.listen)
        # self.canvas.after(returnTime, self.move_ball)
        '''
        elif x == "s":
            self.canvas.move(self.ball, 0, 10)
            self.canvas.after(50, self.move_ball)
        elif x == "w":
            self.canvas.move(self.ball, 0, -10)
            self.canvas.after(50, self.move_ball)
        '''

if __name__ == "__main__":
    # initialize root Window and canvas
    root = Tk()
    root.title("Balls")
    root.resizable(False,False)
    game = Game()
    canvas = Canvas(root, width = 700, height = 300)
    # create two ball objects and animate them
    ball1 = Ball(canvas, 10, 10, 30, 30)
    # ball1.move_ball()
    dg = DataGetter(root)
    key = None
    loopNumber = 0
    userArray = [0] * 500
    runGame = False
    print("first test")
    print(lastKey())
    canvas.bind("<KeyPress>", keydown)
    canvas.bind("<KeyRelease>", keyup)
    canvas.pack()
    canvas.focus_set()
    root.after(2300, game.loop)
    root.mainloop()
