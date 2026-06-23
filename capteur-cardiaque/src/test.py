import matplotlib.pyplot as plt
import numpy as np
from itertools import islice
from sample import sample_file_stream, add_noise

sample = r"data/cardiac.txt"


def show_stream(stream, period: int, n_samples: int):
    X = np.linspace(0, stop=period, num=n_samples, dtype=float)
    Y = list(islice(stream, n_samples)) # n first elements of stream
    plt.plot(X, Y)
    plt.grid()
    plt.show()

if __name__ == '__main__':
    # visualise noisy sample
    show_stream(add_noise(sample_file_stream(sample), snr=10), period=5, n_samples=100)