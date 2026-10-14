# EXAMPLE score for a 20 s film (kick/hat/bass bed + clicks, pops, whooshes, thumps). Rewrite it per film:
# read cue times from the timeline JSON in index.html (ERRORS.md E25) instead of the hardcoded lists below.
import os, numpy as np, soundfile as sf, json
os.makedirs('out', exist_ok=True)
sr=44100; D=20; n=sr*D
rng=np.random.default_rng(7)
mus=np.zeros(n); sfx=np.zeros(n)
def add(buf,t,x,g=1.0):
    s=int(t*sr)
    if s>=n: return
    e=min(n,s+len(x)); buf[s:e]+=x[:e-s]*g
def tt(d): return np.arange(int(d*sr))/sr
def kick():
    t=tt(0.3); return np.sin(2*np.pi*np.cumsum(50+110*np.exp(-t*25))/sr)*np.exp(-t*11)
def hat():
    t=tt(0.06); return rng.standard_normal(len(t))*np.exp(-t*70)
def bass(f,d=0.45):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*5)*np.minimum(1,t*200)
def pluck(f):
    t=tt(0.35); return (np.sin(2*np.pi*f*t)+0.4*np.sin(6*np.pi*f*t))*np.exp(-t*9)
def click():
    t=tt(0.05); return (np.sin(2*np.pi*1800*t)*np.exp(-t*90)+rng.standard_normal(len(t))*np.exp(-t*140)*0.4)
def pop():
    t=tt(0.12); return np.sin(2*np.pi*np.cumsum(900-500*t/0.12)/sr)*np.exp(-t*30)
def whoosh(d=0.6):
    t=tt(d); x=rng.standard_normal(len(t)); k=np.convolve(x,np.ones(40)/40,'same')
    env=np.sin(np.pi*np.clip(t/d,0,1))**2; return k*env*1.5
def thump():
    t=tt(0.5); return np.sin(2*np.pi*(40+30*np.exp(-t*8))*t)*np.exp(-t*6)
notes={'A':55.0,'F':43.65,'C':65.41,'G':49.0}
prog=['A','A','F','F','C','C','G','G','A','A']  # one chord per bar (2s)
for b in range(int(D/0.5)):
    t=b*0.5
    add(mus,t,kick(),0.9 if b%4==0 else 0.7)
    add(mus,t+0.25,hat(),0.12)
    if b>=4: add(mus,t+0.25,bass(notes[prog[min(9,int(t/2))]]),0.5)
    if b>=8 and b%2==1: add(mus,t,pluck(notes[prog[min(9,int(t/2))]]*8),0.15)
for t in [6.8,9.0,11.1,13.0]: add(sfx,t,click(),0.7)
add(sfx,13.0,pop(),0.5)
for i in range(1,12): add(sfx,13.0+i/14,pop(),0.25)
for t in [2.0,3.0,3.5,4.0,6.0,8.0,10.0,12.0,14.0,16.0,18.0,19.2]:
    add(sfx,t-0.15,whoosh(),0.25)
add(sfx,2.0,thump(),0.5); add(sfx,14.0,thump(),0.5); add(sfx,16.0,thump(),0.5)
mix=mus*0.8+sfx
mix[int(19.6*sr):]*=np.linspace(1,0,n-int(19.6*sr))
mix=mix/np.abs(mix).max()*0.85
sf.write('out/music.wav',np.stack([mix,mix],1).astype('float32'),sr)
