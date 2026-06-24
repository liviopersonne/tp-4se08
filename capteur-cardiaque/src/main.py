from machine import Pin, SPI, PWM, Pin, ADC
import utime
from sample import sample_file_stream, add_noise
import analysis
from ST7735 import LCD_0inch96
import framebuf
import time

sample = r"cardiac.txt"


## ── Hardware components ────────────────────────────────────────────────────

adc = ADC(Pin(26, mode=Pin.IN))

# init screen
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000
lcd = LCD_0inch96()
lcd.fill(BLACK)


## ── Functions ──────────────────────────────────────────────────────────────

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

def show_text():
    lcd.text("TELECOM-PARIS!",35,15,GREEN)
    lcd.text("This is:",50,35,RED)    
    lcd.text("Pico-LCD-0.96",30,55,BLUE)
    lcd.display() #this command launches the display

def plot_graph(data, color=GREEN):
    if not data:
        lcd.display()
        return

    width = 160
    height = 80

    lo, hi = min(data), max(data)
    span = hi - lo if hi != lo else 1

    n = len(data)
    # map each data point to an x pixel, spread evenly across the screen width
    points = []
    for i, val in enumerate(data):
        x = int(i / (n - 1) * (width - 1)) if n > 1 else 0
        y = height - 1 - int((val - lo) / span * (height - 1))  # flip y: 0 is top
        points.append((x, y))

    # draw connecting lines between consecutive points
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        lcd.line(x0, y0, x1, y1, color)

## ── Main ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # read and print adc
    # show_adc(1000)

    # read and show sample file
    # for val in sample_simulation(sample, int(1e5)):
    #     print(val)

    # compute bpm from dummy stream
    dummy_stream = sample_simulation(sample, int(100))
    noisy_stream = add_noise(dummy_stream, snr=3)
    signal_args = analysis.SignalArgs(
        freq = 90,
        pers_ratio = 0.35,
        buf_size = 180,             # 2s at 90 Hz
        display_size = 100,
        rr_window = 8,
        rr_min_size = 0.30,         # 200 BPM
        rr_max_size = 2.00,         # 30 BPM
        verbose = False
    )

    # print("ok")

    display_window = []
    bpm_stream = analysis.compute_bpm_stream(dummy_stream, signal_args, display_window)
    for t, bpm in bpm_stream:
        lcd.fill(BLACK)
        plot_graph(display_window)
        lcd.text(str(round(bpm,1)),10,15,RED)
        lcd.display()

    # show text
    # show_text()

    # graph
    stream = sample_simulation(sample, int(1))
    data = []
    for i in range(100):
        data.append(next(stream))
        lcd.fill(BLACK)
        plot_graph(data)
        lcd.text(str(i),10,15,RED)
        lcd.display()
