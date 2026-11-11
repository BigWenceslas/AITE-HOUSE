import json, os, subprocess, hashlib, sys
sys.path.insert(0, os.path.dirname(__file__)); from scenarios import VIDEOS
V = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(V, 'cache'); os.makedirs(C, exist_ok=True)
env = dict(os.environ, HYPERFRAMES_PYTHON=os.path.join(V, '.venv-tts/bin/python'))
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
out = {}
for nom, vid in VIDEOS.items():
    for s in vid['scenes']:
        h = hashlib.sha256(('1.0|'+s['voix']).encode()).hexdigest()[:14]
        brut, norme = f'{C}/{h}.wav', f'{C}/{h}-n.wav'
        if not os.path.exists(norme):
            subprocess.run(['npx','--yes','hyperframes@0.8.139','tts',s['voix'],'-v','ff_siwis','-s','1.0','-o',brut],cwd=V,env=env,capture_output=True)
            # coupe les silences de début et de fin, puis normalise
            subprocess.run(['ffmpeg','-v','error','-y','-i',brut,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=7','-ar','48000','-ac','1',norme],check=True)
        s['audio'] = norme; s['vdur'] = round(dur(norme), 3)
    t = 0.0
    for s in vid['scenes']:
        s['debut'] = round(t, 3)
        s['duree'] = round(max(2.6, s['vdur'] + (0.55 if s['type'] != 'fin' else 2.4) + 0.3), 3)
        t += s['duree']
    vid['total'] = round(t, 3); out[nom] = vid
    print(nom, vid['total'], [s['vdur'] for s in vid['scenes']])
json.dump(out, open(os.path.join(V, 'plan.json'), 'w'), ensure_ascii=False, indent=1)
