#!/usr/bin/env python3
"""splice.py <out.mp4> <out.frames.tsv> <ref.frames.tsv> <take_dir>...: one gate-clean video of a movie from several
tasty takes of the same core. For every movie frame, the first take (in argument order) whose row is clean (dup_reason
none, an AVI frame, full 512x224 size) supplies it. Each chosen row's hash must equal the reference log's hash for that movie frame; the script
stops on any mismatch or gap. The output TSV lists, per movie frame, the hash and which take supplied it."""
import glob, os, subprocess, sys
out, otsv, ref = sys.argv[1:4]; TAKES = sys.argv[4:]
W, H = 512, 224

def rows(d):
    tsv = glob.glob(os.path.join(d, '*.frames.tsv'))[0]
    stem = os.path.basename(tsv)[:-len('.frames.tsv')]
    r = {}; full = {}  # segment -> its AVI is 512x224 (tasty drops a stalled segment to half size; the TSV still says 512x224)
    for avi in glob.glob(os.path.join(d, stem + '_*.avi')):
        wh = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                             '-of', 'csv=p=0', avi], capture_output=True, text=True).stdout.strip()
        full[int(avi[-7:-4])] = wh == f'{W},{H}'
    for l in open(tsv).read().splitlines()[1:]:
        c = l.split('\t')
        mf = int(c[4])
        if mf < 0 or c[3] != 'none' or c[8] == '-1' or not full.get(int(c[8])):
            continue
        r.setdefault(mf, (c[5], int(c[8]), int(c[9])))
    return stem, r

refh = {}
for l in open(ref).read().splitlines()[1:]:
    c = l.split('\t')
    if int(c[4]) >= 0: refh.setdefault(int(c[4]), c[5])
T = [rows(d) for d in TAKES]
plan = []; missing = []
for mf in range(max(refh) + 1):
    k = next((i for i, (_, r) in enumerate(T) if mf in r), None)
    if k is None: missing.append(mf); continue
    src = (k, T[k][1][mf])
    if src[1][0] != refh[mf]: sys.exit(f'movie frame {mf}: hash {src[1][0]} != reference {refh[mf]}')
    plan.append((mf, src[0], src[1]))
print('frames', len(plan), {os.path.basename(TAKES[i]): sum(p[1] == i for p in plan) for i in range(len(TAKES))})
if missing: sys.exit(f'no clean frame in any take for movie frames {missing}')
if os.environ.get('DRY'): sys.exit(0)

class Seg:  # sequential raw decoder of one AVI segment, with forward seeking by frame index
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE); self.n = -1; self.buf = None
    def get(self, i):
        while self.n < i:
            self.buf = self.p.stdout.read(W * H * 3); self.n += 1
            if len(self.buf) != W * H * 3: sys.exit(f'short read at {self.n}')
        if self.n != i: sys.exit(f'backward seek {self.n} -> {i}')
        return self.buf

segs = {}
def frame(take, seg, af):
    d, stem = TAKES[take], T[take][0]
    k = (take, seg)
    if k not in segs or segs[k].n > af: segs[k] = Seg(os.path.join(d, f'{stem}_{seg:03d}.avi'))
    return segs[k].get(af)

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', '25000000/415979', '-i', '-', '-vf', 'scale=1024:896:flags=neighbor,format=yuv420p',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', out],
                       stdin=subprocess.PIPE)
with open(otsv, 'w') as t:
    t.write('movie_frame\thash\ttake\n')
    for mf, take, (h, seg, af) in plan:
        enc.stdin.write(frame(take, seg, af)); t.write(f'{mf}\t{h}\t{os.path.basename(TAKES[take])}\n')
enc.stdin.close(); sys.exit(enc.wait())
