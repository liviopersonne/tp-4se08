import random

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
        noise = random.normalvariate(0, abs(value) / snr)
        yield value + noise