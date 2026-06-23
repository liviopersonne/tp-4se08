from machine import Pin, ADC, Timer
import utime
from sample import sample_file_stream, add_noise

sample = r"cardiac.txt"


## ── Hardware components ────────────────────────────────────────────────────

led = Pin(25, Pin.OUT)
adc = ADC(Pin(26, mode=Pin.IN))
timer = Timer()


## ── Functions ──────────────────────────────────────────────────────────────

# Blink the screen periodically
def blink(timer):
    led.toggle()

# Print adc read values at a specific period
def show_adc(period: int):
    while True:
        start = utime.ticks_us()
        print(adc.read_u16())
        stop = utime.ticks_us()
        elapsed = utime.ticks_diff(stop, start)
        utime.sleep_us(max(0, period - elapsed))

# Simulate a signal using the sample
def sample_simulation(filepath: str, period: int):
        stream = sample_file_stream(filepath)
        for val in stream:
            start = utime.ticks_us()
            yield val
            stop = utime.ticks_us()
            elapsed = utime.ticks_diff(stop, start)
            utime.sleep_us(max(0, period - elapsed))


## ── Main ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ...
    # blink
    # timer.init(freq=10, mode=Timer.PERIODIC, callback=blink)
    
    # read and print adc
    # show_adc(1000)

    # read and show sample file
    for val in sample_simulation(sample, int(1e5)):
        print(val)