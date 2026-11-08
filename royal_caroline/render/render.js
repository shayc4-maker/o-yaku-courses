const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',args:['--no-sandbox','--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1280,height:720}}); p.on('console',m=>console.log('page:',m.text())); p.on('pageerror',e=>console.log('pageerror',e.message));
  await p.goto('http://localhost:8765/web/index.html'); await p.waitForFunction('window.ready===true',{timeout:120000});
  const N=parseInt(process.argv[2]||'96'); fs.mkdirSync('frames',{recursive:true}); const t0=Date.now();
  for(let i=0;i<N;i++){ await p.evaluate(t=>window.setT(t),i/(N-1)); await p.locator('#c').screenshot({path:`frames/f${String(i).padStart(3,'0')}.png`}); if(i%12==0)console.log('frame',i,((Date.now()-t0)/1000).toFixed(0)+'s'); }
  await b.close();
})();
