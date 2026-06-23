from machine import Pin, ADC, Timer
import utime


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


# Main
if __name__ == '__main__':
    # blink
    timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)
    
    # read and print adc
    show_adc(1000)