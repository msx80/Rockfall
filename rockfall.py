import mindstorms
import utime
import hub
import random

# Rockfall by MSX80 - (C) 2021

# tune is a list of tuple (note, duration)
def playTune(tune):
    for notes in tune:
        hub.sound.beep(freq=notes[0], time=notes[1], waveform=3)
        utime.sleep_ms(notes[1])

class Rock:
    def __init__(self, c, r):
        self.col = c
        self.row = r

class GameState:

    def __init__(self):
        self.tickDuration = 500 # tick duration, basically how fast the rocks falls
        self.level = 1          # current level
        self.PlayerCol = 2      # player position (column), 2 is middle
        self.rocks = []         # list of all rocks currently in game
        self.score = 0          # current score
        self.wasLeft = False    # control if the left key was released
        self.wasRight = False   # same for right

        # start with six rocks, place them around randomly.
        # Rocks with a negative row index are up on the top outside the screen,
        # they still fall and will appear as soon as they enter the screen.
        for i in range(6):
            r = Rock(random.randint(0,4), 0 - random.randint(3, 13))
            self.rocks.append(r)
        # initialize led to level
        hub.led(self.level)

    def updatePlayer(self):
        # handle left and right buttons.
        # remember if they were pressed the previous loop
        # so it doesn't move every cycle but only on keypress
        if hub.button.left.is_pressed():
            if not self.wasLeft:
                self.wasLeft = True
                if self.PlayerCol>0:
                    self.PlayerCol-=1;
        else:
            self.wasLeft = False
        if hub.button.right.is_pressed():
            if not self.wasRight:
                self.wasRight = True
                if self.PlayerCol<4:
                    self.PlayerCol+=1;
        else:
            self.wasRight = False

    def render(self):
        # render the game state on an Image that can be printed on the screen
        canvas = hub.Image(5,5)
        canvas.set_pixel(self.PlayerCol, 4, 9)
        for rock in self.rocks:
            if rock.row>=0:
                canvas.set_pixel(rock.col, rock.row, 8)
        return canvas

    def resetRock(self, rock):
        # move the rock back up outside the screen on the top
        rock.row = -random.randint(2,4)
        rock.col = random.randint(0,4)
        
    def ensurePassage(self):
        # check there's at least a vertical passage and the row is not completely blocked
        # still allow for dead ends etc., but should mitigate the problem of having a whole row blocked
        
        # these are the columns that contains a vertical passage of two, on rows -1 and -2, initialize with all
        valid = [0,1,2,3,4]
        for rock in self.rocks:
            # consider rows -1 and -2
            if rock.row == -2 or rock.row == -1:
                # mark column as not valid by removing from valid
                if rock.col in valid:
                    valid.remove(rock.col)
        # valid now contains columns that don't have rock in -1 or -2 (that is, columns with a passage)
        if len(valid) == 0:
            # no passages! Pick a random column
            col = random.randint(0,4)
            # move rocks on that column on row -1 and -2 up away
            for rock in self.rocks:
                if rock.col == col and ( rock.row == -2 or rock.row == -1 ):
                    rock.row -= 6

        


    def tick(self):
        # update the rocks
        for rock in self.rocks:
            if rock.row == 4:
                # if the rocks are at the bottom, reset it
                self.resetRock(rock)
                # we made a point!
                self.score += 1
                # every x points increase level!
                if self.score % 50 == 0:
                    playTune([ (400, 20),(500, 50) ])
                    # increase level and set led accordingly
                    self.level += 1
                    hub.led(self.level)
                    # add a rock
                    r = Rock(random.randint(0,4), -1)
                    self.rocks.append(r)
                    # make things faster
                    self.tickDuration -= 50
            else:
                rock.row+=1
        self.ensurePassage()

    def checkFinish(self):
        # check if the player is over a rock
        for rock in self.rocks:
            if rock.row == 4 and rock.col == self.PlayerCol:
                return True
        return False

    def run(self):
        while True:
            # store when the tick will end
            tickEnd = utime.ticks_ms()+self.tickDuration
            # update the game
            self.tick()
            while tickEnd>utime.ticks_ms():
                # while waiting for the next tick, move the player and update the display
                self.updatePlayer()
                hub.display.show(self.render())
                # check if the player hit a rock
                if self.checkFinish():
                    return True 


### Start of program ###

# setup volume and display
hub.sound.volume(3)
write = mindstorms.MSHub().light_matrix.write # needed to write strings on the screen
hub.display.align(hub.FRONT)

while True:
    # this loop is run every match
    playTune([(600, 100),(700, 200)])
    write("READY")
    # create a new game state
    game = GameState()
    # run the game
    game.run()
    # dead! turn led red
    hub.led(9)
    # final tune
    playTune([(500, 100),(400, 100),(300, 300)])

    utime.sleep_ms(2000)
    write("YOU DIED")
    utime.sleep_ms(1000)
    write("SCORE:"+str(game.score))
    hub.led(0)
    utime.sleep_ms(2000)
