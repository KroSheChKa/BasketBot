# BasketBot
## A simple bot that throws the ball into a basketball hoop.

**The bot works in general using computer vision (OpenCV + mss libraries), and mouse movement emulation.**

>I decided not to use the pyautogui library, as it is quite slow. It was replaced by win32(api/con) which are much faster and smoother than pyautogui. Also mss library much faster in making screenshots than method with pyautogui.

----
**_Overall, the idea isn't really complicated. These 3 steps are implemented in the main program:_**

`1. We get the screen coordinates of the ring and the ball with OpenCV.`

`2. Calculate at what angle you need to throw the ball so it goes into the basketball hoop without hitting the ring.`

>At the 2d stage, I had some difficulties with the derivation of the formula, because it must include the physical properties of the inner world of the game. Not surprisingly that I didn't have such data. So I had to calculate the parameters of the world on my own, such as initial velocity(v0), gravitational acceleration(g). (Thanks to school physics, I did it.)

I did some calculations on the wall in my room:

![IMG_0098](https://user-images.githubusercontent.com/104899233/232847993-deb48127-827f-455e-9220-8bce9557e147.jpg)
> In the upper right corner you can see the calculation of the **gravitational acceleration (g)** and the **initial velocity (v₀)** with the only inputs that I was able to measure: **time (t)**, **height (h)** (in pixels). In the remaining part of the wall, the derivation of the full physical formula from the system of equations

**Main output:**

$$
formula = tan(a) * x - \frac{g * x^2}{2 * v₀^2 * cos(a)^2} - y
$$
> To find the right angle, the formula must be close to zero*

Implemented formula in python:
```python
formula = (tan(radians(a))*x) - (g*(pow(x, 2))) / (2*(pow(v0, 2)) * pow((cos(radians(a)), 2))) - y
```

`3. Execute the throw by moving the cursor with the pressed button.`

### The advanced version of the bot provides:

- *Automatically collect the score and add it to a small database.*
- *Automatic restart of the game*

----

## How to use?

**I didn't really plan for anyone to use this bot, so you're unlikely to be able to run it, but...**

>The whole program is designed to have the game window open in a specific area on the screen. In addition there is the problem that the OpenCV function doesn't like it when the size of the original pictures and the model on the screen are different.
>- For example, the original picture of a ball is 100x100 pixels, and you have exactly the same ball on your screen, but with dimensions 50x50. The confidence of machine vision will be quite low, consequently it will not be possible to determine the exact coordinates of the object.

#### But if you have a 3440x1440 monitor, you have a good chance of breaking my record. Here is a little instruction:

1. It is necessary to have an account in a popular CIS social network [VK.com](https://vk.com)
2. Then go into the [Game](https://vk.com/app6657931)
3. All you need is to set the scale of the page 150% and place the browser window (I used Chrome) exactly halfway across the screen on the left half.
4. Run the code using Python IDLE
5. Make sure the game window is on the top. You will have a second to remove the IDLE Shell from game area


**If you are such a crazy person and want to run this code whatever the cost, then you will have to:**
- Change many values related to the screen resolution
- Re-screenshot the original images.

>I hope my detailed comments in the code will help you
----
## The only issue
The only reason why the bot loses is the rare in-game cases where the ball is in the lower left/right corner and the ring is high in the opposite corner. Developers have not provided such an outcome and the ball just gets stuck on the basketball hoop and doesn't score :\

---

    I would love to optimize the bot to any scale, but I'm afraid that's probably impracticable with these technologies. 

I created it for me and for my own pleasure, to learn new and interesting solutions and features, as well as to break the records of other players XD (It really makes me feel more confident and fulfilled).

**If you find some bugs or shortcomings, please leave a comment about it.**

*a new bot is coming soon...*
