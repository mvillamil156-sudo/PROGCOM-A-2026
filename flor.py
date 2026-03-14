import turtle
import math

#pantalla
pantalla = turtle.Screen()
pantalla.bgcolor("black")

flor = turtle.Turtle()
flor.speed(0)
flor.width(2)

#colores de pétalos
colores = ["#ff4d6d", "#ff758f", "#ff8fa3", "#ffb3c1"]

#función para dibujar un pétalo
def petalo(radio, angulo):
    for i in range(2):
        flor.circle(radio, angulo)
        flor.left(180 - angulo)

#dibujar la dalia
for i in range(60):
    flor.color(colores[i % len(colores)])
    petalo(100, 60)
    flor.left(6)

#centro de la flor
flor.penup()
flor.goto(0, -20)
flor.pendown()
flor.color("gold")
flor.begin_fill()
flor.circle(20)
flor.end_fill()
flor.hideturtle()
turtle.done()