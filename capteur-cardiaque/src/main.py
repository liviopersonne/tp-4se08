from machine import Pin, ADC, Timer
import utime
import os


# Hardware components
led = Pin(25, Pin.OUT)
adc = ADC(Pin(26, mode=Pin.IN))
timer = Timer()


# Functions
def blink(timer):
    led.toggle()

def show_adc(period: int):
    while True:
        start = utime.ticks_us()
        print(adc.read_u16())
        stop = utime.ticks_us()
        elapsed = utime.ticks_diff(stop, start)
        utime.sleep_us(max(0, period - elapsed))

def sample_file_read(filepath: str):
    with open(filepath, 'r') as f:
        for i, raw in enumerate(f):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            try:
                yield float(line)
            except ValueError:
                print(f"  [warn] ligne {i} ignorée : {line!r}")


# Main
if __name__ == '__main__':
    # blink
    # timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)
    
    # read and print adc
    # show_adc(1000)

    # read and show sample file
    for l in sample_file_read(r"cardiac.txt"):
        print(l)