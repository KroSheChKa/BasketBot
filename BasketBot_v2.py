import cv2
import mss
import keyboard
import numpy as np
from time import sleep
import win32api, win32con
import math
import easyocr
from openpyxl import load_workbook
from pathlib import Path

#X:  662 Y:  285 RGB: ( 34,  34,  34)
#X: 1279 Y: 1380 RGB: (166, 166, 166)
#150%

def move(x,y):
    win32api.SetCursorPos((x,y))

def dragball(x,y):
    move(center_b[0] + 662, center_b[1] + 285)
    sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    sleep(0.05)
    move(x,y)
    sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def f_test(x,y):
    v0, g, a = 2670, 3990, 90
    lower = 89
    upper = 90
    
    if x <= 8:
        print('Вот твой угол(околонулевой):',a)
        return a
    
    while keyboard.is_pressed('q') == False:
        
        a = (lower + upper) / 2  
        formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
        if formula < 0:
            upper -= 0.35
            lower -= 0.35
            print("Понизил на 0.35")
        else:
            while abs(formula) > 0.1 :
                a = (lower + upper) / 2
                formula = (math.tan(math.radians(a)) * x) - (g*(x**2))/(2*(v0**2)*(math.cos(math.radians(a))**2))-y
                if formula < -0.1:
                    upper = a
                    print('upper', a, formula)
                elif formula > 0.1:
                    lower = a
                    print('lower', a, formula)
            else:
                print('Angle:', a, formula)
                return a

def angle_to_cord_x(a,y1):
    x = y1*math.tan(math.radians(90-a))
    return x

def add_to_excel(score):
    path = Path('E:\Школа\Школа\информатика\Python\Basketball\Results.xlsx')
    #name = "Results.xlsx"
    wb = load_workbook(path)
    ws = wb['Data']
    ws.append(['Score:', score])
    wb.save(path)

sleep(1)

score = cv2.imread('Score.png')

ring = cv2.imread('ring.png')
ring_w = ring.shape[1]
ring_h = ring.shape[0]

basket = cv2.imread('Basket_cutted.png')
basket_w = basket.shape[1]
basket_h = basket.shape[0]

sct = mss.mss()

non = {'left': 662,'top': 285,'width': 617,'height': 1093}
non_score = {'left': 776,'top': 295,'width': 200,'height': 50}

while keyboard.is_pressed('q') == False:
    
    scr = np.array(sct.grab(non))
    scr_r = scr[:,:,:3]
    
    score_ = cv2.matchTemplate(scr_r, score, cv2.TM_CCOEFF_NORMED)
    _, max_val_s, _, _ = cv2.minMaxLoc(score_)

    bask = cv2.matchTemplate(scr_r, basket, cv2.TM_CCOEFF_NORMED)
    _, max_val_b, _, max_loc_b = cv2.minMaxLoc(bask)

    ringg = cv2.matchTemplate(scr_r, ring, cv2.TM_CCOEFF_NORMED)
    _, max_val_r, _, max_loc_r = cv2.minMaxLoc(ringg)

    if max_val_s > 0.95:
        scr_score = np.array(sct.grab(non_score))
        reader = easyocr.Reader(['ru'], gpu = False)
        result = reader.readtext(scr_score, paragraph = True, detail=False)
        print(result)

        score_list = result[0].split(':')
        score_now = int(score_list[-1].strip())
        add_to_excel(score_now)
        print(score_now)

        move(977, 1267)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
        sleep(1)

    if (max_val_b > 0.88) and (max_val_r > 0.88):
        center_b = (max_loc_b[0] + (basket_w //2), 973)
        center_r = (max_loc_r[0] + (ring_w//2), max_loc_r[1] + (ring_h//2) - 10) 
        
        #cv2.circle(scr, center_b, (basket_h//2), (255, 255, 255), 4)
        #cv2.rectangle(scr, (max_loc_r[0], max_loc_r[1]), ((max_loc_r[0] + ring_w), (max_loc_r[1] + ring_h)), (255, 0, 0), 4)
        print(f"Max Val B: {max_val_b} Max Val R: {max_val_r} Ball center: {center_b}, Ring center: {center_r}")

        #cv2.line(scr, (max_loc_r[0] + (ring_w//2), 0), (max_loc_r[0] + (ring_w//2), 1440), (0,255,0), 2)
        #cv2.line(scr, (0, max_loc_b[1]+ basket_h // 2), (617, max_loc_b[1]+ basket_h//2), (0,255,0), 2)
        
        x = abs(center_b[0] - center_r[0])
        y = abs(center_b[1] - center_r[1])

        angle = f_test(x,y)
        
        y1 = 960
        x1 = round(angle_to_cord_x(angle,y1)*2.122)
        
        if center_r[0] >= center_b[0]:
            dragball(round(662 + center_b[0] + x1), (285 + center_b[1] - y1))
            print(662 + center_b[0] + x1, (285 + center_b[1] - y1))
        else:
            dragball(round(662 + center_b[0] - x1), (285 + center_b[1] - y1))
            print(662 + center_b[0] - x1, (285 + center_b[1] - y1))
        sleep(1.78)
        
        #cv2.imshow('test', scr)
        #cv2.waitKey(1)