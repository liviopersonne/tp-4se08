"""
bpm_from_file.py
────────────────
Calcule le BPM à partir d'un fichier cardiac.txt contenant
des valeurs flottantes normalisées (une par ligne), telles que
produites par Waveforms / Digilent dans le TP Télécom Paris.

Format attendu :
  -0.2329317549979141
   0.04029444571683128
   0.7796124005920246
   ...

Usage :
  python bpm_from_file.py cardiac.txt
  python bpm_from_file.py cardiac.txt --fs 90 --plot
  python bpm_from_file.py cardiac.txt --fs 90 --pers-ratio 0.4 --verbose
"""

import argparse
import sys
import os

# ── Paramètres par défaut ────────────────────────────────────────────────────
FS_DEFAULT  = 90      # Hz (valeur du TP)
PERS_RATIO  = 0.35    # seuil persistance (fraction du max observé)
RR_MIN_S    = 0.30    # intervalle RR min → 200 BPM
RR_MAX_S    = 2.00    # intervalle RR max → 30 BPM
RR_WINDOW   = 8       # fenêtre médiane glissante
BUF_SIZE    = 180     # 2 s à 90 Hz

# ── Chargement ───────────────────────────────────────────────────────────────

def load_signal(filepath):
    """
    Charge un fichier texte avec une valeur float par ligne.
    Ignore les lignes vides et les commentaires (#).
    """
    samples = []
    with open(filepath, 'r') as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            try:
                samples.append(float(line))
            except ValueError:
                print(f"  [warn] ligne {lineno} ignorée : {line!r}")
    return samples

# ── Pré-traitement ───────────────────────────────────────────────────────────

def normalize(signal):
    """
    Ramène le signal dans [0, 1].
    Nécessaire pour que les seuils de persistance soient
    indépendants de l'amplitude brute du fichier.
    """
    lo, hi = min(signal), max(signal)
    span = hi - lo
    if span == 0:
        return [0.0] * len(signal)
    return [(v - lo) / span for v in signal]

def moving_average(signal, window):
    """Filtre passe-bas léger par moyenne glissante (anti-bruit HF)."""
    out = []
    half = window // 2
    n = len(signal)
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        out.append(sum(signal[lo:hi]) / (hi - lo))
    return out

# ── Algorithme de persistance topologique ───────────────────────────────────

def find_local_maxima(buf):
    return [i for i in range(1, len(buf) - 1)
            if buf[i] > buf[i-1] and buf[i] > buf[i+1]]

def find_local_minima(buf):
    return [i for i in range(1, len(buf) - 1)
            if buf[i] < buf[i-1] and buf[i] < buf[i+1]]

def compute_persistence(buf):
    """
    persistance(p) = buf[p] - max(vallée_gauche, vallée_droite)
    Retourne liste de dict {idx, val, pers}.
    """
    peaks   = find_local_maxima(buf)
    valleys = find_local_minima(buf)
    n       = len(buf)
    result  = []
    for p in peaks:
        lv        = [v for v in valleys if v < p]
        rv        = [v for v in valleys if v > p]
        left_val  = buf[lv[-1]] if lv else buf[0]
        right_val = buf[rv[0]]  if rv else buf[n-1]
        saddle    = max(left_val, right_val)
        pers      = buf[p] - saddle
        if pers > 0:
            result.append({'idx': p, 'val': buf[p], 'pers': pers})
    return result

def refine_peak(buf, p):
    """Interpolation parabolique → position sub-sample."""
    n = len(buf)
    if p == 0 or p == n - 1:
        return float(p)
    y0, y1, y2 = buf[p-1], buf[p], buf[p+1]
    denom = y0 - 2*y1 + y2
    if denom == 0:
        return float(p)
    return p + 0.5 * (y0 - y2) / denom

def median(lst):
    if not lst:
        return None
    s = sorted(lst)
    m = len(s) // 2
    return s[m] if len(s) % 2 == 1 else (s[m-1] + s[m]) / 2.0

# ── Pipeline principal ───────────────────────────────────────────────────────

def compute_bpm(signal, fs, pers_ratio, buf_size, rr_window, verbose=False):
    """
    Traite le signal par fenêtres glissantes (stride = 1 s).
    Retourne (bpm_final, bpm_series, peak_times).
    """
    n         = len(signal)
    rr_buf    = []
    last_peak = -1.0
    peak_times  = []
    bpm_series  = []
    total_peaks = 0

    for start in range(0, n - buf_size, fs):
        buf = signal[start : start + buf_size]

        pers_data = compute_persistence(buf)
        if not pers_data:
            continue

        max_pers  = max(p['pers'] for p in pers_data)
        threshold = pers_ratio * max_pers
        valid     = [p for p in pers_data if p['pers'] >= threshold]

        for p in valid:
            refined  = refine_peak(buf, p['idx'])
            abs_samp = start + refined

            if last_peak < 0:
                last_peak = abs_samp
                continue

            interval_s = (abs_samp - last_peak) / fs
            if RR_MIN_S <= interval_s <= RR_MAX_S:
                rr_buf.append(interval_s)
                if len(rr_buf) > rr_window:
                    rr_buf.pop(0)
                last_peak = abs_samp
                peak_times.append(abs_samp / fs)
                total_peaks += 1

        med_rr = median(rr_buf)
        if med_rr:
            bpm_now  = 60.0 / med_rr
            t_center = (start + buf_size / 2) / fs
            bpm_series.append((round(t_center, 2), round(bpm_now, 1)))
            if verbose:
                print(f"  t={t_center:6.1f}s  →  {bpm_now:5.1f} BPM  "
                      f"(RR médian={med_rr*1000:.0f} ms, {len(rr_buf)} intervalles)")

    all_bpms  = [b for _, b in bpm_series]
    bpm_final = round(median(all_bpms), 1) if all_bpms else None
    return bpm_final, bpm_series, peak_times

# ── Affichage terminal ───────────────────────────────────────────────────────

def print_summary(signal, fs, bpm_final, bpm_series, peak_times):
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

    if bpm_series:
        print()
        print("  Évolution temporelle :")
        for t, b in bpm_series:
            bar = "█" * int(b / 5)
            print(f"  {t:6.1f}s  {b:5.1f} BPM  {bar}")

# ── Graphiques ───────────────────────────────────────────────────────────────

def plot_results(signal_raw, signal_proc, fs, peak_times, bpm_series):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        import numpy as np
    except ImportError:
        print("\n[info] matplotlib non installé — pip install matplotlib")
        return

    t_sig = np.arange(len(signal_raw)) / fs

    fig = plt.figure(figsize=(13, 8))
    gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.5, wspace=0.35)

    # ── Signal brut ──
    ax0 = fig.add_subplot(gs[0, :])
    ax0.plot(t_sig, signal_raw, color='#888', linewidth=0.6, label='Brut')
    ax0.plot(t_sig, signal_proc, color='#1d9e75', linewidth=0.9, label='Normalisé + lissé')
    ax0.set_title('Signal cardiaque')
    ax0.set_xlabel('Temps (s)')
    ax0.legend(fontsize=9)
    ax0.grid(alpha=0.2)

    # ── Signal lissé + pics ──
    ax1 = fig.add_subplot(gs[1, :])
    ax1.plot(t_sig, signal_proc, color='#1d9e75', linewidth=0.9)
    if peak_times:
        peak_vals = [signal_proc[min(int(pt * fs), len(signal_proc)-1)]
                     for pt in peak_times]
        ax1.scatter(peak_times, peak_vals, color='#e24b4a', zorder=5,
                    s=60, label=f'Pics ({len(peak_times)})', marker='^')
    ax1.set_title('Pics détectés (persistance topologique)')
    ax1.set_xlabel('Temps (s)')
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.2)

    # ── BPM dans le temps ──
    ax2 = fig.add_subplot(gs[2, 0])
    if bpm_series:
        ts, bs = zip(*bpm_series)
        ax2.plot(ts, bs, color='#185fa5', linewidth=1.5, marker='o', markersize=4)
        ax2.axhline(60,  color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        ax2.axhline(100, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        ax2.fill_between(ts, 60, 100, alpha=0.08, color='green', label='Zone normale')
        ax2.legend(fontsize=9)
    ax2.set_title('Évolution du BPM')
    ax2.set_xlabel('Temps (s)')
    ax2.set_ylabel('BPM')
    ax2.grid(alpha=0.2)

    # ── Histogramme RR ──
    ax3 = fig.add_subplot(gs[2, 1])
    if len(peak_times) >= 2:
        rr_ms = [round((peak_times[i+1] - peak_times[i]) * 1000)
                 for i in range(len(peak_times)-1)
                 if RR_MIN_S <= peak_times[i+1]-peak_times[i] <= RR_MAX_S]
        if rr_ms:
            ax3.hist(rr_ms, bins=20, color='#534AB7', edgecolor='white', linewidth=0.5)
            mean_rr = sum(rr_ms) / len(rr_ms)
            ax3.axvline(mean_rr, color='#e24b4a', linestyle='--',
                        label=f'Moy. {mean_rr:.0f} ms')
            ax3.legend(fontsize=9)
    ax3.set_title('Distribution intervalles RR')
    ax3.set_xlabel('RR (ms)')
    ax3.set_ylabel('Fréquence')
    ax3.grid(alpha=0.2)

    plt.suptitle('Analyse BPM — persistance topologique', fontsize=11)
    plt.tight_layout()
    plt.show()

# ── Point d'entrée ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='BPM depuis cardiac.txt (valeurs flottantes normalisées).')
    parser.add_argument('filepath')
    parser.add_argument('--fs',         type=int,   default=FS_DEFAULT,
                        help=f'Fréquence d\'échantillonnage Hz (défaut: {FS_DEFAULT})')
    parser.add_argument('--pers-ratio', type=float, default=PERS_RATIO,
                        help=f'Seuil persistance 0–1 (défaut: {PERS_RATIO})')
    parser.add_argument('--smooth',     type=int,   default=3,
                        help='Fenêtre du lissage passe-bas en samples (défaut: 3)')
    parser.add_argument('--plot',       action='store_true')
    parser.add_argument('--verbose',    action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"Erreur : fichier introuvable → {args.filepath}")
        sys.exit(1)

    print(f"Chargement de {args.filepath} ...")
    signal_raw = load_signal(args.filepath)

    if len(signal_raw) < BUF_SIZE:
        print(f"Erreur : signal trop court ({len(signal_raw)} samples, "
              f"minimum {BUF_SIZE} requis à {args.fs} Hz)")
        sys.exit(1)

    print(f"  {len(signal_raw)} échantillons  |  "
          f"{len(signal_raw)/args.fs:.1f} s à {args.fs} Hz")
    print(f"  Amplitude brute : [{min(signal_raw):.3f}, {max(signal_raw):.3f}]")

    # Pré-traitement : normalisation + lissage léger
    signal_proc = normalize(signal_raw)
    if args.smooth > 1:
        signal_proc = moving_average(signal_proc, args.smooth)

    print(f"  Seuil persistance : {args.pers_ratio}  |  lissage : {args.smooth} samples")
    print()
    print("Analyse en cours...")

    bpm_final, bpm_series, peak_times = compute_bpm(
        signal     = signal_proc,
        fs         = args.fs,
        pers_ratio = args.pers_ratio,
        buf_size   = BUF_SIZE,
        rr_window  = RR_WINDOW,
        verbose    = args.verbose,
    )

    print_summary(signal_raw, args.fs, bpm_final, bpm_series, peak_times)

    if args.plot:
        plot_results(signal_raw, signal_proc, args.fs, peak_times, bpm_series)

    return bpm_final

if __name__ == '__main__':
    main()
