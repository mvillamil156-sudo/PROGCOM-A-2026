import turtle
import math

#pantalla
screen = turtle.Screen()
screen.bgcolor("black")

t = turtle.Turtle()
t.speed(0)
t.width(2)
t.hideturtle()

#angulo
angulo = 137.5

for i in range(300):
    
    #r
    r = 0.5 * i
    
    #rad
    theta = math.radians(i * angulo)
    
    #pol-car
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    
    t.penup()
    t.goto(x, y)
    t.pendown()
    
    #petalo
    size = i / 20 + 2
    
    #colores
    t.pencolor(1, 0.5 * math.sin(i*0.1) + 0.5, 0.8)
    
    t.circle(size)

turtle.done()