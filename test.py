import random
secret_number = random.randint(1, 100)
while True:
    guess = int(input('Guess the number between 1 and 100: '))
    if guess == secret_number:
        print('You are correct!')
        break
    elif guess < secret_number:
        print('Too low! Try again.')
    else:
        print('Too high! Try again.')

       
       
import turtle

# Create a turtle object
t = turtle.Turtle()

# Set the turtle's color to purple
t.color("blue")

# Optional: Set the turtle's shape (default is an arrow)
t.shape("turtle")

# Optional: Set the turtle's speed (0 is the fastest)
t.speed(2)

t.forward(100)

# Draw something using the turtle
# For example, let's draw a square
for i in range(4):
    t.forward(100)
    t.right(90)

# Keep the window open until it's closed by the user
turtle.done()