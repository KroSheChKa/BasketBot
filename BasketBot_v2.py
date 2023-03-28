import cv2
import mss
import keyboard
import numpy as np
from time import sleep
import win32api, win32con
import math
import easyocr
from openpyxl import load_workbook

# The scale of the window - 150%
# Window resolution 1720x1440

# This function moves the cursor to x,y position
def move(x,y):
    win32api.SetCursorPos((x,y))

# Function to drag from the center of the ball to sm coordinates
#  to throw it with a certain angle to the ground

def dragball(x,y):

    # Set cursor position in the center of the ball
    move(center_b[0] + 662, center_b[1] + 285)

    sleep(0.05)

    # Press and hold...
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    sleep(0.05)
    move(x,y)
    sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

# solve_4_angle is a function to find exact angle to throw
def solve_4_angle(x,y):

    # Physical parameters of game world:
        # v0 - starting speed
        # g - gravitational acceleration
        # a = angle. 90 is default value. angle could't be more than 90 degrees
    v0, g, a = 2670, 3990, 90

    # Lower and upper - borders
    lower = 89
    upper = 90

    # A small optimization. We don't have to count an angle that close to 90,
    #  because it will play into the margin of error
    if x <= 8:
        print("Here's your angle (close to 90):",a)
        return a
    
    # Here 'q' button is needed to quit out of loop -> stop bot
    while keyboard.is_pressed('q') == False:

        step = 0.35
        confidence = 0.1

        a = (lower + upper) / 2

        # This is the main QUADRATIC formula, the tarector is a parabola,
        #  consequently we will have TWO angles. But the only one is needed.
        formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
        
        # The second angle could interrupt us. We always need bigger angle.
        #  So the borders are moving slightly till there won't be an angle in it
        if formula < 0:
            upper -= step
            lower -= step
            print(f"Reduced by {step}")

        # After finding a gap with only 1 angle we can find it
        # Here I decided to use binary search, due it's speed.
        else:
            while abs(formula) > confidence :
                a = (lower + upper) / 2
                formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
                if formula < -confidence:
                    upper = a
                    #print('Upper', a, formula)
                elif formula > confidence:
                    lower = a
                    #print('Lower', a, formula)
            else:
                print('Angle:', a, formula)
                return a

# The function that calculates at what coordinates to move the cursor to throw the ball
def angle_to_cord_x(a,y1):
    x = y1*math.tan(math.radians(90-a))
    return x

# It clicks on replay button
def replay():
    move(977, 1267)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    sleep(0.4)

# Not really needed function. Just to collect data (score).
# Results are in "Results.xlsx"
def add_to_excel(score):
    wb = load_workbook("Results.xlsx")
    ws = wb['Data']
    ws.append(['Score:', score])
    wb.save("Results.xlsx")

sleep(1)

# Reading 3 images
score = cv2.imread('Score.png')

ring = cv2.imread('ring.png')
ring_w = ring.shape[1]
ring_h = ring.shape[0]

basket = cv2.imread('Basket_cutted.png')
basket_w = basket.shape[1]
basket_h = basket.shape[0]

sct = mss.mss()

# This area of the game depends on your monitor resolution
play_zone = {'left': 662,'top': 285,'width': 617,'height': 1093}

# A small area to determine the end of the game
score_zone = {'left': 776,'top': 295,'width': 200,'height': 50}

# Actually the main(). Press Q to break
while keyboard.is_pressed('q') == False:
    
    # Grabbing screenshot
    scr = np.array(sct.grab(play_zone))

    # Delete the unnecessary alpha channel
    scr_r = scr[:,:,:3]
    
    # Getting confidence and location of 3 objects
    score_ = cv2.matchTemplate(scr_r, score, cv2.TM_CCOEFF_NORMED)
    _, max_val_s, _, _ = cv2.minMaxLoc(score_)

    bask = cv2.matchTemplate(scr_r, basket, cv2.TM_CCOEFF_NORMED)
    _, max_val_b, _, max_loc_b = cv2.minMaxLoc(bask)

    ringg = cv2.matchTemplate(scr_r, ring, cv2.TM_CCOEFF_NORMED)
    _, max_val_r, _, max_loc_r = cv2.minMaxLoc(ringg)

    # In this step we check if the game is over, saving data, repeat game
    if max_val_s > 0.95:
        scr_score = np.array(sct.grab(score_zone))

        # Because the game is in Russian, it will be read with 'ru' parameter,
        #  however it doesn't really important. We only need a value (score)
        reader = easyocr.Reader(['ru'], gpu = True)
        result = reader.readtext(scr_score, paragraph = True, detail=False)

        # Getting the score
        score_list = result[0].split(':')
        score_now = int(score_list[-1].strip())

        # Adding to an excel file
        add_to_excel(score_now)

        print('Your score: ', score_now)

        # Pressing the replay button
        replay()

    # Values are optimized to exclude the possibility of incorrect detection
    if (max_val_b > 0.88) and (max_val_r > 0.88):

        # As in physics, we start from the center of objects
        # The second arg. in center_b I decided to set up manually,
        #  beacause ball is bouncing, but the object itself is fixed
        center_b = (max_loc_b[0] + (basket_w //2), 973)
        center_r = (max_loc_r[0] + (ring_w//2), max_loc_r[1] + (ring_h//2) - 10) 

        #print(f"Max Val B: {max_val_b} Max Val R: {max_val_r} Ball center: {center_b}, Ring center: {center_r}")

        # The difference between the centers of coordinates of the hoop and the ball
        x = abs(center_b[0] - center_r[0])
        y = abs(center_b[1] - center_r[1])

        # Getting an angle
        angle = solve_4_angle(x,y)
        
        # y1 - static value of a bigger cathetus in a right triangle.
        y1 = 960

        # x1 - searchable value of another cathetus
        x1 = round(angle_to_cord_x(angle,y1)*2.122)
        # RANDOM coefficient-----------------^^^^^ (need to resolve)

        # Determine which way to throw. Right/Left
        if center_r[0] >= center_b[0]:
            dragball(round(662 + center_b[0] + x1), (285 + center_b[1] - y1))
            print(662 + center_b[0] + x1, (285 + center_b[1] - y1))
        else:
            dragball(round(662 + center_b[0] - x1), (285 + center_b[1] - y1))
            print(662 + center_b[0] - x1, (285 + center_b[1] - y1))

        # Bot throws and sleeps for sm time
        sleep(1.78)