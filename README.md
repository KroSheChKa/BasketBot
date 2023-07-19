# BasketBot
## A simple bot that throws the ball into a basketball hoop.

**The bot works in general using computer vision `(OpenCV + mss libraries)`, and mouse movement emulation.**

>I decided not to use the pyautogui library, as it is quite slow. It was replaced by `win32(api/con)` which are much faster and smoother than pyautogui. Also `mss library` much faster in making screenshots than method with pyautogui.

![basketbot_gif](https://github.com/KroSheChKa/BasketBot/assets/104899233/dc98a915-1dc4-47bd-a097-cf7647bf0d83)

> **[Video](https://youtu.be/pxDiq9SRecY) in YouTube how BasketBot works!**

- Use the `BasketBot` for single runs and manual checks!
- Use the `BasketBot_v2` for idle runs and collecting data!

----
**_Overall, the idea isn't really complicated. These 3 steps are implemented in the main program:_**

### 1. We get the screen coordinates of the ring and the ball with OpenCV.

### 2. Calculate at what angle you need to throw the ball so it goes into the basketball hoop without hitting the ring.

At the 2d stage, I had some difficulties with the derivation of the formula, because it must include the `physical properties of the inner world of the game`. Not surprisingly that I didn't have such data. So I had to calculate the parameters of the world on my own. (Thanks to school physics, I did it.)

I did some calculations on the wall in my room:

![IMG_0098](https://user-images.githubusercontent.com/104899233/232847993-deb48127-827f-455e-9220-8bce9557e147.jpg)
> In the upper right corner you can see the calculation of the `gravitational acceleration (g)` and the `initial velocity (v₀)` with the only inputs that I was able to measure: `time (t)`, `height (h)` (in pixels). In the remaining part of the wall, the derivation of the full physical formula from the system of equations

> > P.S. Actually I recalculated them on a bigger screen resolution to get more accurate data.

**Main output:**

$$
formula = tan(a) * x - \frac{g * x^2}{2 * v₀^2 * cos(a)^2} - y
$$
> To find the right angle, the formula value must be `close to zero`

Implemented formula in python:
```python
formula = (tan(radians(a))*x) - (g*(pow(x, 2))) / (2*(pow(v0, 2)) * pow((cos(radians(a)), 2))) - y
```

### 3. Throw the ball with the left button pressed at a modified coefficient angle.

So why do we need to enter some other coefficient when we can substitute values into the formula, find the angle, and throw?

**In this game, the angle of flight of the ball is different from the input angle**

- So I had to come up with a solution. First, I introduced a constant, a coefficient. This solved the problem for the most part, but there were still a lot of flaws. After observation, I noticed that the `coefficient is dynamic` and you need to increase it as the distance between the ball and the ring increases.

```python
coefficient = 2.167
if x + y >= 955: #As long as the distance doesn't reach 955 px, coef. is static
    coefficient = coefficient + (math.sqrt(x + y - 955) / 53) # Compensate angle
```

**Formula calculation with a material point, not with an object**

- As we know, in physics we usually take objects to be material points that have `no distance` at all. In my case, however, we are throwing a ball, which has a `decent size`! This creates a big problem, because where a material point will fly, the ball won't fly.

  > This is often the reason for losing. The ball hits the ring and flies away

![basketbot_angle](https://github.com/KroSheChKa/BasketBot/assets/104899233/2a348895-365f-4c45-a1f2-afdad140cdae)

> As you can see in the gif above you can see the influence of the coefficient on the ball's trajectory. The black line is the **`desired`** angle of flight of the ball, which the formula calculates. The white line is the changed cursor trajectory by coefficient, so that the ball flew with the angle of the black line.

----

## How to use?

#### Installation steps:

- Install [python](https://www.python.org/downloads/) together with `IDLE` on your computer **(you should run the code via IDLE!)**
- Clone this project by this command somewhere on your computer:
> **Make sure you have downloaded [git](https://git-scm.com/downloads)!**
```
git clone https://github.com/KroSheChKa/BasketBot.git
```
- Open cmd in the created folder or press RButton in the folder and click "`Git Bash Here`" and paste that:
```
pip install -r requirements.txt
```
**Particular case:** *If you have a monitor 3440x1440, then simply place the window with the game exactly half the screen on the left, set the **window scale 150%** and run it via `Python IDLE`.*

In other cases to run this code on your computer you will have to `change values` depending on the resolution of your monitor, such as:

```python 
# This area of the game depends on your monitor resolution
play_zone = {'left': 662,'top': 285,'width': 617,'height': 1093}
```
> Try to make it right on the borders of the game

In `BasketBot_v2` change theese values to a place where you see the result:
```python 
# A small area to determine the end of the game
score_zone = {'left': 776,'top': 295,'width': 200,'height': 50}
``` 
```python 
# Change the second static value to where the center of the ball is relative to the y coordinate
center_b = (max_loc_b[0] + basket_w // 2, 973)
```
*Also you may play with threshold coefficients if something goes wrong.*

- It is **necessary** to have an account in a popular CIS social network [VK.com](https://vk.com)
  
- Then go into the [Game](https://vk.com/app6657931)

- Launch the bot **via `Python IDLE`**. Move the windows that pop out away from the window with the game.

### Press Q to start. Press Q to stop the bot.
> You can change the key to another using [that table](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes)

And that's it.
>I hope my detailed comments in the code will help you

----

## The only issue
The only reason why the bot loses is the rare `in-game cases` where the ball is in the lower left/right corner and the ring is high in the opposite corner. Developers have not provided such an outcome and the ball just gets stuck on the basketball hoop or it just doesn't fly to it and doesn't score :\

---

#### I created it for my own pleasure, to learn new and interesting solutions and features, as well as to break the records of other players XD (It really makes me feel more confident and fulfilled).


*Any suggestions? You found a bug?*

-> Leave a comment in [Discussions](https://github.com/KroSheChKa/BasketBot/discussions)
