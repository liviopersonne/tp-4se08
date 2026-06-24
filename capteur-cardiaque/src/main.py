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

## ── Main ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # read and print adc
    # show_adc(1000)

    # read and show sample file
    # for val in sample_simulation(sample, int(1e5)):
    #     print(val)

    # compute bpm from dummy stream
    # dummy_stream = sample_simulation(sample, int(1e4))
    # noisy_stream = add_noise(dummy_stream, snr=3)
    # signal_args = analysis.SignalArgs(
    #     freq = 90,
    #     pers_ratio = 0.35,
    #     buf_size = 180,             # 2s at 90 Hz
    #     rr_window = 8,
    #     rr_min_size = 0.30,         # 200 BPM
    #     rr_max_size = 2.00,         # 30 BPM
    #     verbose = False
    # )
    # bpm_stream = analysis.compute_bpm_stream(noisy_stream, signal_args)
    # for bpm in bpm_stream:
    #     print(bpm)

    # show text
    show_text()
