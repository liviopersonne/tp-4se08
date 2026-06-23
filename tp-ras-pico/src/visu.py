import matplotlib.pyplot as plt
import os
import random

folder = os.path.join(os.getcwd(), "data")
filename = "cardiac.txt"
file = open(os.path.join(folder, filename), 'r')
Y = list(map(lambda x: float(x.strip()), file.readlines()))
data = enumerate(Y)
n = len(Y)
X = range(0, n)

def add_noise(intensity=0.1):
    for i in range(n):
        Y[i] += random.normalvariate(0, intensity)


def naive1():
    window_size = 300
    max_relative = 0.5 # Max accepted relative difference between peak intensities
    local_maxes = []
    for i in range(1, n-1):
        if (Y[i] >= Y[i-1] and Y[i] >= Y[i+1]):
            local_maxes.append((i, Y[i]))


if __name__ == '__main__':
    # add_noise(0.3)
    plt.plot(X, Y)
    plt.grid()
    plt.show()
    file.close()