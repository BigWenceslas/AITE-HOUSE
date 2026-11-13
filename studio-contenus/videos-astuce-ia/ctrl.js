// images de contrôle à des instants précis : node ctrl.js nom t1 t2 ...
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const [nom,...ts]=process.argv.slice(2); const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'plan.json')))[nom];
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+path.join(__dirname,'page.html'));await p.evaluate(pl=>window.charger(pl),plan);fs.mkdirSync(path.join(__dirname,'ctrl'),{recursive:true});
 for(const t of ts){await p.evaluate(x=>window.seek(x),+t);await p.screenshot({path:path.join(__dirname,'ctrl',`${nom}-${t}.jpg`),type:'jpeg',quality:70})}
 await b.close()})();
