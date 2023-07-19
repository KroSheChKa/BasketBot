import cv2
import mss
import numpy as np
import time
import win32api, win32con
import sys, ctypes, keyboard
import math
import easyocr
from openpyxl import load_workbook

# Site with the game - https://vk.com/app6657931
# The scale of the window - 150%
# Window resolution 1720x1440

def is_key_pressed(key):
    return ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000 != 0

def sleep_key(sec, key_code = 0x51):
    start_time = time.time()
    
    while True:
        if is_key_pressed(key_code):
            sys.exit()
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if elapsed_time >= sec:
            break

# This function moves the cursor to x,y position
def move(x,y):
    win32api.SetCursorPos((x,y))

# Function to drag from the center of the ball to sm coordinates
#  to throw it with a certain angle to the ground
def dragball(x, y, c_b, left, top):

    # Set cursor position in the center of the ball
    move(c_b[0] + left, c_b[1] + top)

    sleep_key(0.05)

    # Press and hold...
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    sleep_key(0.05)
    move(x + left,y + top)
    sleep_key(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)


# solve_4_angle is a function to find exact angle to throw
def solve_4_angle(x,y, v0 = 2632.1094902, g = 3789.9344711, a = 90):
    # Physical parameters of game world:
        # v0 - initial velocity
        # g - gravitational acceleration
        # a = angle. 90 is default value. angle could't be more than 90 degrees

    # Lower and upper - borders
    lower = 89
    upper = 90

    # A small optimization. We don't have to count an angle that close to 90,
    #  because it will play into the margin of error
    if x <= 8:
        print("Your angle is approx. 90°")
        return a
    
    # Here 'q' button is needed to quit out of loop -> stop bot
    while keyboard.is_pressed('q') == False:

        step = 0.35
        confidence = 0.001
        a = (lower + upper) / 2

        # This is the main QUADRATIC formula, the tarector is a parabola,
        #  consequently we will have TWO angles. But the only one is needed.
        formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
        
        # The second angle could interrupt us. We always need bigger angle.
        #  So the borders are moving slightly till there won't be an angle in it
        if formula < 0:
            upper -= step
            lower -= step
            #print(f"Reduced by {step}")

        # After finding a gap with only 1 angle we can find it
        # Here I decided to use binary search, due it's speed.
        else:
            while abs(formula) >= confidence :
                a = (lower + upper) / 2
                formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
                if formula < -confidence:
                    upper = a
                    #print('Upper', a, formula)
                elif formula >= confidence:
                    lower = a
                    #print('Lower', a, formula)
            else:
                print('Angle:', round(a, 5), 'Radians:', round(a * math.pi / 180, 5))
                return a

# The function that calculates at what coordinates to move the cursor to throw the ball
def angle_to_cord_x(a,y1):
    x = y1*math.tan(math.radians(90-a))
    return x

# It clicks on replay button
def replay():
    move(977, 1267) # Possition of replay button
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    sleep_key(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    sleep_key(0.4)

# Finction just to collect data (scores).
# Results are in "Results.xlsx"
def add_to_excel(score):
    wb = load_workbook("Results.xlsx")
    ws = wb['Data']
    ws.append(['Score:', score])
    wb.save("Results.xlsx")

def main():
    # Reading 3 images + widht, height of a ring and a ball
    score_pink = cv2.imread(r'Images\score_pink.png')
    score = cv2.imread(r'Images\Score.png')

    ring = cv2.imread(r'Images\ring_new.png')
    ring_w = ring.shape[1]
    ring_h = ring.shape[0]

    basket = cv2.imread(r'Images\Basket_cutted.png')
    basket_w = basket.shape[1]
    #basket_h = basket.shape[0] I decided make it static (y cordinate)

    # "Activate" mss
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

        score_pink_ = cv2.matchTemplate(scr_r, score_pink, cv2.TM_CCOEFF_NORMED)
        _, max_val_s_p, _, _ = cv2.minMaxLoc(score_pink_)
        
        bask = cv2.matchTemplate(scr_r, basket, cv2.TM_CCOEFF_NORMED)
        _, max_val_b, _, max_loc_b = cv2.minMaxLoc(bask)

        ringg = cv2.matchTemplate(scr_r, ring, cv2.TM_CCOEFF_NORMED)
        _, max_val_r, _, max_loc_r = cv2.minMaxLoc(ringg)

        # In this step we check if the game is over, saving data, repeat game
        if (max_val_s > 0.9) or (max_val_s_p > 0.9):
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
        if max_val_b > 0.885:
            
            # As in physics, we start from the center of objects
            # The second arg. in center_b I decided to set up manually,
            #  beacause ball is bouncing, but the object itself is fixed
            center_b = (max_loc_b[0] + basket_w //2, 973)
            center_r = (max_loc_r[0] + ring_w//2 - 2, max_loc_r[1] + ring_h // 2) 

            #print(f"Max Val B: {round(max_val_b, 4)} Max Val R: {round(max_val_r, 4)} Ball center: {center_b}, Ring center: {center_r}")

            # The difference between the centers of coordinates of the hoop and the ball
            x = abs(center_b[0] - center_r[0])
            y = abs(center_b[1] - center_r[1])

            # Getting an angle
            angle = solve_4_angle(x,y)
            
            # y_triangle - static value of a bigger cathetus in a right triangle.
            y_triangle = 960

            # Coefficient that aligns the difference between the angle of 
            # the ball and the cursor trajectory
            coefficient = 2.167

            # I found out that angle is quiet big when x and y are big too. So here's "solution":
            if x + y >= 955:
                coefficient = coefficient + (math.sqrt(x + y - 955) / 53)

            # x1 - searchable value of another cathetus
            x_triangle = round(angle_to_cord_x(angle,y_triangle)*coefficient)

            # Determine which way to throw. Right/Left
            if center_r[0] <= center_b[0]:
                x_triangle = -x_triangle
            
            # Dragging cursor
            dragball(round(center_b[0] + x_triangle), (center_b[1] - y_triangle),
                          center_b, play_zone['left'], play_zone['top'])

            # Bot throws and sleeps for some time
            sleep_key(2)


# Entry point
if __name__ == '__main__':

    # Time to prepare
    sleep_key(0.5)

    # Runs a program
    main()
