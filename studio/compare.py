# Objective QA metrics for one or more renders.
#   python compare.py out/final.mp4                      -> metrics for one film
#   python compare.py A=old/final.mp4 B=out/final.mp4    -> side-by-side table
#   python compare.py --sync out/music.wav index.html    -> audio onset vs timeline events (needs <script id="tl"> JSON)
import json, re, subprocess, sys, os
import numpy as np

def probe(p):
    o = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,width,height,r_frame_rate',
                                   '-of', 'json', p], capture_output=True, text=True).stdout)
    v = next(s for s in o['streams'] if s['codec_type'] == 'video'); n, d = map(int, v['r_frame_rate'].split('/'))
    return {'w': v['width'], 'h': v['height'], 'fps': n / d, 'dur': float(o['format']['duration']), 'mb': int(o['format']['size']) / 1e6}

def loudness(p):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', e); tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)
    return (float(i[-1]) if i else float('nan')), (float(tp[-1]) if tp else float('nan'))

def motion(p, fps, thr=0.6):
    # thr 0.6 sits above the film-grain floor (grain-only steps measured up to ~0.59 at 108x192 area-downscale)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vf', 'scale=108:192:flags=area,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(np.float32)
    d = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2)); st = d < thr
    run = best = 0
    for s in st: run = run + 1 if s else 0; best = max(best, run)
    f = int(round(fps)); dead = sum(1 for i in range(len(d) // f) if d[i * f:(i + 1) * f].max() < thr)
    seam = float(np.abs(F[-1] - F[0]).mean())
    return {'moving_pct': float(100 * (1 - st.mean())), 'longest_still_s': best / fps, 'dead_seconds': dead,
            'seam_ratio': seam / max(float(np.median(d)), 1e-6) if seam > 0.05 else 0.0}

def sync(wav, html):
    import librosa
    TL = json.loads(re.search(r'<script id="tl" type="application/json">(.*?)</script>', open(html, encoding='utf8').read(), re.S).group(1))
    ev = []
    for k, v in TL.items():
        if isinstance(v, list): ev += [x[0] if isinstance(x, list) else x for x in v if isinstance(x if not isinstance(x, list) else x[0], (int, float))]
        elif isinstance(v, (int, float)) and k not in ('bpm', 'dur'): ev.append(v)
    ev = sorted(set(t for t in ev if t > 0.05))          # an onset exactly at t=0 cannot be detected
    y, sr = librosa.load(wav, sr=None, mono=True); on = librosa.onset.onset_detect(y=y, sr=sr, units='time', hop_length=128)
    err = [(t, 1000 * (on[np.argmin(np.abs(on - t))] - t)) for t in ev]
    for t, e in err: print(f'  {t:6.2f}s  {e:+7.1f} ms')
    a = np.abs([e for _, e in err]); print(f'events {len(err)}  mean |err| {a.mean():.1f} ms  within 25 ms: {(a <= 25).sum()}/{len(a)}')

if __name__ == '__main__':
    if sys.argv[1] == '--sync': sync(sys.argv[2], sys.argv[3]); sys.exit()
    vids = dict((a.split('=', 1) if '=' in a else (os.path.basename(os.path.dirname(os.path.abspath(a))), a)) for a in sys.argv[1:])
    res = {}
    for n, p in vids.items():
        info = probe(p); lufs, tp = loudness(p)
        res[n] = {**info, 'lufs': lufs, 'true_peak': tp, **motion(p, info['fps'])}
    rows = [('dur', 'duration s', '{:.2f}'), ('fps', 'fps', '{:.0f}'), ('mb', 'file MB', '{:.1f}'), ('lufs', 'loudness LUFS (want -14)', '{:.1f}'),
            ('true_peak', 'true peak dB (want <= -1)', '{:.1f}'), ('moving_pct', '% frames moving', '{:.0f}'),
            ('longest_still_s', 'longest still s (want < 1)', '{:.2f}'), ('dead_seconds', 'dead whole seconds (want 0)', '{:d}'),
            ('seam_ratio', 'loop seam x median step (<1 ok)', '{:.1f}')]
    print(f"{'metric':34s}" + ''.join(f'{n[:14]:>16s}' for n in res))
    for k, label, f in rows: print(f'{label:34s}' + ''.join(f'{f.format(res[n][k]):>16s}' for n in res))
