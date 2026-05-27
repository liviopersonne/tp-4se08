import matplotlib.pyplot as plt
import os

folder = os.path.join(os.getcwd(), "data")
filename = "cardiac.txt"
file = open(os.path.join(folder, filename), 'r')

def show_beat():
    Y = list(map(lambda x: float(x.strip()), file.readlines()))
    X = range(0, len(Y))

    print(X[:5], Y[:5])

    plt.plot(X, Y)
    plt.grid()
    plt.show()


if __name__ == '__main__':
    show_beat()
    file.close()