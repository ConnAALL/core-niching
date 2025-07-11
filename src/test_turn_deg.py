# Test how many deg we turn per turn quant

from Engine import libpyAI as ai
import time
import sys

global counter
global curr
global prev
global timer
global turn_quantity
counter = 0
curr = 90
prev = 90
timer = False
turn_quantity = int(sys.argv[1]) # Turn quant in sys args

def loop():
    global counter
    global curr
    global prev
    global timer
    global turn_quantity

    print(f"init heading {ai.selfHeadingDeg()}")
    time.sleep(0)
    for i in range(2):
        ai.turn(10 * turn_quantity)  # Turn clockwise
    counter = counter + 1
    print(f"after turn heading {ai.selfHeadingDeg()}, turned {counter} times")
    curr = ai.selfHeadingDeg()
    if curr < prev:
        timer = True
    
    if timer and curr >= 90:
        turn_amount = 270 + ai.selfHeadingDeg()
        overcorrection = abs(360 - turn_amount)
        turn_deg_per_turn = turn_amount/counter
        print(f"took {counter} turns, we turned {overcorrection} more degrees than we should have")
        print(f"we turned {turn_deg_per_turn} deg each time we turned, turn_quantity = {turn_quantity}")
        time.sleep(5)
    prev = ai.selfHeadingDeg()

# turn quant turn deg, numbers taken when ship has visually completed a full circle
# 0 = 0.0 (does not turn)
# 1 = 2.9268
# 2 = 2.9268
# 3 = 4.000
# 4 = 5.5384
# 5 = 6.667
# 6 = 8.1818
# 7 = 8.7723


def main():
    ai.start(loop, ["-name", "test", "-join", "localhost"])



if __name__ == "__main__":
    main()