import random
import math

def gauss(mu=0.0, sigma=1.0):
    u1 = random.random()
    while u1 == 0.0:
        u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mu + z0 * sigma


# Stream the sample file (returns a generator)
def sample_file_stream(filepath: str):
    with open(filepath, 'r') as f:
        for i, raw in enumerate(f):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            try:
                yield float(line)
            except ValueError:
                print(f"  [warn] ligne {i} ignorée : {line!r}")

# Add gaussian noise to a generator
def add_noise(stream, snr=10):
    for value in stream:
        noise = gauss(0, abs(value) / snr)
        yield value + noise