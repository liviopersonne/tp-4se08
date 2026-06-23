from collections import namedtuple

SignalArgs = namedtuple('SignalArgs', [
    'freq',         # sampling frequency (in Hz)
    'pers_ratio',   # persistence threshold (0-1 ratio)
    'buf_size',     # size of the buffer window
    'rr_window',    # size of the r-r window (between 2 peaks)
    'rr_min_size',  # minimal r-r size
    'rr_max_size',  # maximal r-r size
    'verbose',      # print debug messages
])

# ── Pre-treatement ──────────────────────────────────────────────────────────

# Bring the signal to [0, 1]
def normalize(signal):
    lo, hi = min(signal), max(signal)
    span = hi - lo
    if span == 0:
        return [0.0] * len(signal)
    return [(v - lo) / span for v in signal]

# Filter out noise with a low-pass filter
def moving_average(signal, window):
    out = []
    half = window // 2
    n = len(signal)
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        out.append(sum(signal[lo:hi]) / (hi - lo))
    return out


# ── Topological persistence computation ─────────────────────────────────────

# Return the median of a list
def median(lst):
    if not lst:
        return None
    s = sorted(lst)
    m = len(s) // 2
    return s[m] if len(s) % 2 == 1 else (s[m-1] + s[m]) / 2.0

# Return sorted indices of local maxima and minima
def find_local_extrema(sig):
    maxima, minima = [], []
    for i in range(1, len(sig) - 1):
            if sig[i] > sig[i-1] and sig[i] > sig[i+1]:
                maxima.append(i)
            elif sig[i] < sig[i-1] and sig[i] < sig[i+1]:
                minima.append(i)
    return maxima, minima

# Parabolic interpolation -> sub-sample peak position
def refine_peak(sig, p):
    n = len(sig)
    if p == 0 or p == n - 1:
        return float(p)
    y0, y1, y2 = sig[p-1], sig[p], sig[p+1]
    denom = y0 - 2*y1 + y2
    if denom == 0:
        return float(p)
    return p + 0.5 * (y0 - y2) / denom

# Returns a list of persistences: {idx, val, pers}
# For each peak p: pers(p) = sig[p] - max(left_valley, right_valley)
def compute_persistence(sig):
    peaks, valleys = find_local_extrema(sig)
    result = []
    for p in peaks:
        lv        = [v for v in valleys if v < p]
        rv        = [v for v in valleys if v > p]
        left_val  = sig[lv[-1]] if lv else sig[0]
        right_val = sig[rv[0]]  if rv else sig[-1]
        saddle    = max(left_val, right_val)
        pers      = sig[p] - saddle
        if pers > 0:
            result.append({'idx': p, 'val': sig[p], 'pers': pers})
    return result


# ── Heartbeat computation ───────────────────────────────────────────────────

# Computes the bpm of the signal using a sliding window
def compute_bpm_stream(stream, signal_args: SignalArgs):
    rr_buf    = []
    last_peak = -1.0
    start = 0
    buf = []

    for _ in range(signal_args.buf_size):
        buf.append(next(stream))

    while True:
        val = next(stream)
        buf.pop(0)
        buf.append(val)
        start += 1

        pers_data = compute_persistence(buf)
        if not pers_data:
            continue

        max_pers  = max(p['pers'] for p in pers_data)
        threshold = signal_args.pers_ratio * max_pers
        valid     = [p for p in pers_data if p['pers'] >= threshold]

        for p in valid:
            refined  = refine_peak(buf, p['idx'])
            abs_samp = start + refined

            if last_peak < 0:
                last_peak = abs_samp
                continue

            interval_s = (abs_samp - last_peak) / signal_args.freq
            if signal_args.rr_min_size <= interval_s <= signal_args.rr_max_size:
                rr_buf.append(interval_s)
                if len(rr_buf) > signal_args.rr_window:
                    rr_buf.pop(0)
                last_peak = abs_samp

        med_rr = median(rr_buf)
        if med_rr:
            bpm_now  = 60.0 / med_rr
            t_center = (start + signal_args.buf_size / 2) / signal_args.freq
            if signal_args.verbose:
                print(f"  t={t_center:6.1f}s  ->  {bpm_now:5.1f} BPM")
            yield (t_center, bpm_now)

# Computes the bpm of the signal using a sliding window
def compute_bpm(signal, signal_args: SignalArgs):
    n         = len(signal)
    rr_buf    = []
    last_peak = -1.0
    peak_times  = []
    bpm_series  = []
    total_peaks = 0

    for start in range(0, n - signal_args.buf_size, signal_args.freq):
        buf = signal[start : start + signal_args.buf_size]

        pers_data = compute_persistence(buf)
        if not pers_data:
            continue

        max_pers  = max(p['pers'] for p in pers_data)
        threshold = signal_args.pers_ratio * max_pers
        valid     = [p for p in pers_data if p['pers'] >= threshold]

        for p in valid:
            refined  = refine_peak(buf, p['idx'])
            abs_samp = start + refined

            if last_peak < 0:
                last_peak = abs_samp
                continue

            interval_s = (abs_samp - last_peak) / signal_args.freq
            if signal_args.rr_min_size <= interval_s <= signal_args.rr_max_size:
                rr_buf.append(interval_s)
                if len(rr_buf) > signal_args.rr_window:
                    rr_buf.pop(0)
                last_peak = abs_samp
                peak_times.append(abs_samp / signal_args.freq)
                total_peaks += 1

        med_rr = median(rr_buf)
        if med_rr:
            bpm_now  = 60.0 / med_rr
            t_center = (start + signal_args.buf_size / 2) / signal_args.freq
            bpm_series.append((round(t_center, 2), round(bpm_now, 1)))
            if signal_args.verbose:
                print(f"  t={t_center:6.1f}s  →  {bpm_now:5.1f} BPM  "
                      f"(RR médian={med_rr*1000:.0f} ms, {len(rr_buf)} intervalles)")

    all_bpms  = [b for _, b in bpm_series]
    bpm_final = round(median(all_bpms), 1) if all_bpms else None
    return bpm_final, bpm_series, peak_times

