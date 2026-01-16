from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
from machine import Pin, Timer, PWM
import random
from time import sleep
import time
import _thread

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
W, H = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED   = display.create_pen(255, 0, 0)
PINK = display.create_pen(229,135,213)
PURPLE = display.create_pen(72,1,102)

buzzer = PWM(Pin(0))
SCORE_BUZZ = 100
FAIL_BUZZ = 100

buzz_timer=Timer()

def stopBuzz(timer):
    buzzer.duty_u16(0)

def buzz(duration = 0.3, freq = 200, duty = 40000):
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    buzz_timer.init(freq=3,mode=Timer.ONE_SHOT,callback=stopBuzz)

display.set_pen(BLACK)
display.clear()

default_rect_y = int (H * 2/3) + 15
rect_y = default_rect_y
default_rect_H = 15
rect_H = default_rect_H

score = 0
default_speed = 0.1
speed = default_speed
radius = 15
offset = 20
y = radius + offset
x = random.randint(radius,W-radius)

delta_factor = 0.00003

reversed = False

def drawBackgroundColor(color):
    display.set_pen(color)
    display.clear()

def drawRectangleColor(color):
    global rect_y, rect_H, reversed
    display.set_pen(color)
    display.rectangle(0,rect_y,W,rect_H)

def drawBallColor(color):
    global radius, x,y, reversed
    display.set_pen(color)
    display.circle(x,int(y),radius)

def drawScoreColor(color):
    global score,W
    display.set_pen(color)
    if not reversed:
        display.text("Score: "+str(score),0,0,W,3) 
    else:
        display.text("Score: "+str(score),0,H-20,W,3)

previous = time.ticks_us()
def drawBall():

    global x,y,default_speed, speed, radius, offset, score, default_rect_H, rect_y, rect_H, reversed, previous, delta_factor

    current = time.ticks_us()
    delta = (current - previous) * delta_factor
    previous = current

    if not reversed:
        if y - radius >= H :
            speed = default_speed
            y = radius + offset
            x = random.randint(radius,W-radius)
            score = 0
            rect_H = default_rect_H
            rect_y = default_rect_y
        else: 
            y = y + speed * delta
            speed = speed + random.random()
    else:
        if y + radius <= 0:
            reversed = False
            speed = default_speed
            y = radius + offset
            x = random.randint(radius,W-radius)
            score = 0
            rect_H = default_rect_H
            rect_y = default_rect_y
        else:
            y = y + speed * delta
            speed = speed - random.random()

    if score < 15:
        drawBackgroundColor(BLACK)
        drawRectangleColor(RED)
        drawScoreColor(WHITE)
        if score <10:
            drawBallColor(WHITE)
        else:
            drawBallColor(PINK)
    else:
        drawBackgroundColor(WHITE)
        drawScoreColor(BLACK)
        drawRectangleColor(BLACK)
        drawBallColor(PURPLE)
    display.update()

pressed_score_button = False
score_button = Pin(14,Pin.IN,Pin.PULL_UP)

def on_press():
    global x, y, radius, rect_y, rect_H, score, default_speed, speed, default_rect_H, H, offset, reversed, pressed_score_button, released_button
    val = not score_button.value()
    if val and not pressed_score_button:
        if score >= 20:
            reversed = random.choice([0,1])
        if not reversed:
            if (y + radius >= rect_y) and (y - radius <= rect_y + rect_H):
                buzz(freq=SCORE_BUZZ)
                score = score + 1
                speed = default_speed
                y = radius + offset
                x = random.randint(2*radius,W-2*radius)
                if score >= 3:
                    rect_y = random.randint(2*radius+offset,H-radius)
            else:
                buzz(freq=FAIL_BUZZ)
                score = 0
                speed = default_speed
                y = radius + offset
                x = random.randint(2*radius, W-2*radius)
                rect_y = default_rect_y
                rect_H = default_rect_H
        else: 
            if (y - radius <= rect_y + rect_H) and (y + radius >= rect_y):
                buzz(freq=SCORE_BUZZ)
                score = score + 1
                speed = -default_speed
                y = H - radius - offset
                x = random.randint(2*radius,W-2*radius)
                if score >= 3:
                    rect_y = random.randint(0 + radius, H - 2 * radius - offset)
            else:
                buzz(freq=FAIL_BUZZ)
                reversed = False
                score = 0
                speed = -default_speed
                y = radius + offset
                x = random.randint(2*radius, W-2*radius)
                rect_y = default_rect_y
                rect_H = default_rect_H

        if score == 5:
            print(default_rect_H - 50/100 * default_rect_H )
            rect_H = int(default_rect_H - 50/100 * default_rect_H)
        if score == 10:
            print(default_rect_H - 90/100 * default_rect_H)
            rect_H = int(default_rect_H - 90/100 * default_rect_H)

        if score == 10:
            speed = 5

        if score == 15:
            speed = 3
    pressed_score_button = val

running = 1

def stop(_):
    global running
    running = 0

off_button = Pin(3,Pin.IN,Pin.PULL_DOWN)
off_button.irq(trigger=Pin.IRQ_FALLING, handler=stop)

# keep the game going
while running:
    on_press()
    drawBall()