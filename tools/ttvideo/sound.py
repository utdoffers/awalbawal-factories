# -*- coding: utf-8 -*-
"""🔊 ثلاثةُ أصواتٍ للعلامة — مولَّدةٌ بالكامل. لا ملفَّ خارجيًّا ولا ترخيص."""
import wave, math, struct, random, sys
SR = 44100

def mk(n): return [0.0] * n

def kick(b, t0, amp=1.0):
    s = int(t0*SR)
    for i in range(int(0.30*SR)):
        if s+i >= len(b): break
        t = i/SR
        f = 130*math.exp(-26*t) + 46           # هبوطُ نغمةٍ = دقّةُ الطبل
        b[s+i] += amp*math.exp(-9*t)*math.sin(2*math.pi*f*t)

def hat(b, t0, amp=0.20, ln=0.05):
    s = int(t0*SR)
    for i in range(int(ln*SR)):
        if s+i >= len(b): break
        b[s+i] += amp*math.exp(-70*i/SR)*(random.random()*2-1)

def clap(b, t0, amp=0.5):
    s = int(t0*SR)
    for i in range(int(0.20*SR)):
        if s+i >= len(b): break
        t=i/SR
        b[s+i] += amp*math.exp(-22*t)*(random.random()*2-1)*(1+0.6*math.sin(300*t))

def bass(b, t0, f, ln, amp=0.42):
    s = int(t0*SR)
    for i in range(int(ln*SR)):
        if s+i >= len(b): break
        t=i/SR; env = min(1, t*40)*math.exp(-2.4*t)
        b[s+i] += amp*env*(math.sin(2*math.pi*f*t)+0.3*math.sin(4*math.pi*f*t))

def bell(b, t0, f, amp=0.34, dec=3.2):
    s = int(t0*SR)
    for i in range(int(1.6*SR)):
        if s+i >= len(b): break
        t=i/SR; e=math.exp(-dec*t)
        b[s+i] += amp*e*(math.sin(2*math.pi*f*t)+0.5*math.sin(2*math.pi*f*2*t)+0.25*math.sin(2*math.pi*f*3.01*t))

def riser(b, t0, ln, amp=0.34):
    s = int(t0*SR)
    for i in range(int(ln*SR)):
        if s+i >= len(b): break
        p = i/(ln*SR)
        f = 220 + 1500*p*p
        b[s+i] += amp*(0.25+0.75*p)*(0.55*math.sin(2*math.pi*f*i/SR) + 0.45*(random.random()*2-1)*p)

def finish(b, out, tail=0.55):
    n=len(b)
    for i in range(int(tail*SR)):
        j=n-1-i
        if j>=0: b[j] *= i/(tail*SR)
    pk=max(1e-9, max(abs(v) for v in b)); g=0.80/pk
    w=wave.open(out,"w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1,min(1,v*g))*32767)) for v in b)); w.close()

def s1(dur, rev, out):                       # ① هادئ — نبضةٌ وجرس
    b=mk(int(dur*SR)); t=0.0
    while t<dur-0.2: kick(b,t,0.42); t+=0.5
    bell(b,rev,784); bell(b,rev+0.08,1175,0.22)
    bell(b,dur-1.1,523,0.24); finish(b,out)

def s2(dur, rev, out):                       # ② إيقاع — 120 نبضة/دقيقة
    b=mk(int(dur*SR)); beat=0.5; t=0.0; i=0
    notes=[55,55,73.4,65.4]
    while t<dur-0.1:
        kick(b,t,0.95)
        hat(b,t+beat/2,0.16); hat(b,t+beat/4,0.10); hat(b,t+3*beat/4,0.10)
        if i%2==1: clap(b,t,0.44)
        bass(b,t,notes[i%4],beat*0.95)
        t+=beat; i+=1
    bell(b,rev,988,0.30,4.0)
    finish(b,out)

def s3(dur, rev, out):                       # ③ تصعيدٌ ثمّ انفجارٌ عند الكود
    b=mk(int(dur*SR))
    riser(b,0.0,rev)                         # صعودٌ حتى لحظة الكشف
    kick(b,rev,1.0); clap(b,rev,0.6); bass(b,rev,41.2,1.2,0.55)
    bell(b,rev+0.02,1318,0.30,3.0)
    t=rev+0.5; i=0
    while t<dur-0.1:
        kick(b,t,0.80); hat(b,t+0.25,0.16)
        if i%2==1: clap(b,t,0.38)
        bass(b,t,[41.2,49,55,49][i%4],0.48)
        t+=0.5; i+=1
    finish(b,out)

dur, rev = float(sys.argv[1]), float(sys.argv[2])
for name, fn in (("s1",s1),("s2",s2),("s3",s3)):
    random.seed(7); fn(dur, rev, f"/tmp/{name}.wav"); print("✓", name)
