import gpiod
from time import sleep

chip = gpiod.Chip('gpiochip0')

inPin1 = chip.get_line(21)
inPin2 = chip.get_line(20)
inPin3 = chip.get_line(16)
inPin4 = chip.get_line(12)

inPin1.request(consumer="button1", type=gpiod.LINE_REQ_DIR_IN)
inPin2.request(consumer="button2", type=gpiod.LINE_REQ_DIR_IN)
inPin3.request(consumer="button3", type=gpiod.LINE_REQ_DIR_IN)
inPin4.request(consumer="button4", type=gpiod.LINE_REQ_DIR_IN)

while True:
    readVal1 = inPin1.get_value()
    readVal2 = inPin2.get_value()
    readVal3 = inPin3.get_value()
    readVal4 = inPin4.get_value()
    
    print("button1:", readVal1)
    print("button2:", readVal2)
    print("button3:", readVal3)
    print("button4:", readVal4)
    
    sleep(0.2)