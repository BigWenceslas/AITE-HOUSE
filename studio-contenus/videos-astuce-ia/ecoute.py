import json, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8')
plan = json.load(open('plan.json'))
for nom, v in plan.items():
    print('==', nom)
    for s in v['scenes']:
        segs, _ = m.transcribe(np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',s['audio'],'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout,np.float32), language='fr', beam_size=1)
        print(' ATTENDU :', s['sous']); print(' ENTENDU :', ' '.join(x.text.strip() for x in segs))
