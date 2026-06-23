import matplotlib.pyplot as plt
import numpy as np
from itertools import islice
from sample import sample_file_stream, add_noise
import analysis

sample = r"data/cardiac.txt"

# Show the first n samples of a stream sampled at a specific period
def show_stream(stream, period: int, n_samples: int):
    X = np.linspace(0, stop=period, num=n_samples, dtype=float)
    Y = list(islice(stream, n_samples)) # n first elements of stream
    plt.plot(X, Y)
    plt.grid()
    plt.show()

# Print a summary of the analysis
def print_summary(signal, fs, bpm_final, peak_times):
    duration = len(signal) / fs
    print()
    print("╔══════════════════════════════════════════╗")
    print("║           RÉSULTATS BPM                  ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Durée signal        : {duration:6.1f} s           ║")
    print(f"║  Échantillons        : {len(signal):6d}            ║")
    print(f"║  Fréq. éch. (Fs)     :   {fs:4d} Hz           ║")
    print(f"║  Pics détectés       : {len(peak_times):6d}            ║")
    if bpm_final:
        zone = ("🟢 Normal"       if 60 <= bpm_final <= 100
                else "🔵 Bradycardie" if bpm_final < 60
                else "🟡 Tachycardie")
        print(f"║                                          ║")
        print(f"║  BPM FINAL (médiane) :  {bpm_final:5.1f} BPM        ║")
        print(f"║  Zone physiologique  :  {zone:<17s} ║")
    else:
        print("║  BPM FINAL : non calculé (signal court?) ║")
    print("╚══════════════════════════════════════════╝")

# Show the evolution of the BPM
def show_series(bpm_series):
    plt.step(*zip(*bpm_series), where='mid')
    plt.grid()
    plt.show()

if __name__ == '__main__':
    clear_stream = sample_file_stream(sample)
    noisy_stream = add_noise(sample_file_stream(sample), snr=3)

    # visualise noisy sample
    # show_stream(noisy_stream, period=5, n_samples=100)

    # compute bpm
    signal_args = analysis.SignalArgs(
        freq = 90,
        pers_ratio = 0.35,
        buf_size = 180,             # 2s at 90 Hz
        rr_window = 8,
        rr_min_size = 0.30,         # 200 BPM
        rr_max_size = 2.00,         # 30 BPM
        verbose = False
    )
    
    signal = list(noisy_stream)
    bpm_final, bpm_series, peak_times = analysis.compute_bpm(signal, signal_args)
    # print_summary(signal, 90, bpm_final, peak_times)
    show_series(bpm_series)