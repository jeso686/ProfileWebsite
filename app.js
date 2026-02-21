const requiredCoverageKeys = [
  ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''), ...'0123456789'.split(''),
  'SPACE','ENTER','TAB','BACKSPACE','ESC','SHIFT','CTRL','ALT',
  'MINUS','EQUAL','LBRACKET','RBRACKET','BACKSLASH','SEMICOLON','APOSTROPHE','COMMA','DOT','SLASH','GRAVE',
  ...Array.from({length:12}, (_,i)=>`F${i+1}`), 'UP','DOWN','LEFT','RIGHT'
];

const mappingTemplate = {
  ...Object.fromEntries(Array.from({length:26},(_,i)=>[String.fromCharCode(65+i), 4+i])),
  '1':30,'2':31,'3':32,'4':33,'5':34,'6':35,'7':36,'8':37,'9':38,'0':39,
  ENTER:40,ESC:41,BACKSPACE:42,TAB:43,SPACE:44,MINUS:45,EQUAL:46,LBRACKET:47,RBRACKET:48,BACKSLASH:49,
  SEMICOLON:51,APOSTROPHE:52,GRAVE:53,COMMA:54,DOT:55,SLASH:56,
  F1:58,F2:59,F3:60,F4:61,F5:62,F6:63,F7:64,F8:65,F9:66,F10:67,F11:68,F12:69,
  RIGHT:79,LEFT:80,DOWN:81,UP:82,SHIFT:225,CTRL:224,ALT:226
};

const state = {
  sample:null, mapping:null, generated:null, messages:[], symbolUsage:new Set(), stickyMods:new Set(),
  delayRule:'event_self'
};

const $ = id => document.getElementById(id);
const ui = {
  sampleFile: $('sampleFile'), mappingFile: $('mappingFile'), coverage:$('coverage'), messages:$('messages'), script:$('script'),
  macroName:$('macroName'), interDelay:$('interDelay'), pressDelay:$('pressDelay'), humanize:$('humanize'), jitter:$('jitter'), jitterOnlyText:$('jitterOnlyText'), endDelay:$('endDelay'), pretty:$('pretty'),
  generateBtn:$('generateBtn'), downloadBtn:$('downloadBtn'), copyBtn:$('copyBtn'), clearBtn:$('clearBtn'), jsonPreview:$('jsonPreview'), eventPreview:$('eventPreview'), typed:$('typed'), summary:$('summary'),
  symbolMap:$('symbolMap'), presets:$('presets'), snippetName:$('snippetName'), saveSnippetBtn:$('saveSnippetBtn'), snippetList:$('snippetList'),
  downloadTemplateBtn:$('downloadTemplateBtn'), coverageBtn:$('coverageBtn')
};

function showMessages(items){
  ui.messages.innerHTML = items.length ? items.map(m=>`<div class="${m.level}">${m.text}</div>`).join('') : '<span class="ok">Ready.</span>';
}

function parseJSONFile(file){ return file.text().then(JSON.parse); }
function saveText(filename, text){ const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type:'application/json'})); a.download=filename; a.click(); URL.revokeObjectURL(a.href);} 

ui.sampleFile.onchange = async e => {
  try { state.sample = await parseJSONFile(e.target.files[0]); inferSampleRule(); showMessages([{level:'ok', text:'sample.mac loaded'}]); regenerate(); }
  catch { showMessages([{level:'err', text:'Invalid sample.mac JSON'}]); }
};
ui.mappingFile.onchange = async e => {
  try { state.mapping = await parseJSONFile(e.target.files[0]); refreshCoverage(); regenerate(); }
  catch { showMessages([{level:'err', text:'Invalid mapping.json'}]); }
};
ui.downloadTemplateBtn.onclick = ()=>saveText('mapping.template.json', JSON.stringify(mappingTemplate, null, 2));
ui.coverageBtn.onclick = ()=>saveText('mapping-coverage.txt', coverageReportText());
ui.generateBtn.onclick = regenerate;
ui.copyBtn.onclick = async ()=> { if(!state.generated) return; await navigator.clipboard.writeText(JSON.stringify(state.generated, null, ui.pretty.checked?2:0)); showMessages([{level:'ok',text:'JSON copied'}]); };
ui.downloadBtn.onclick = ()=>{ if(!state.generated) return; saveText(`${(ui.macroName.value||'Macro').trim()}.mac`, JSON.stringify(state.generated, null, ui.pretty.checked?2:0)); };
ui.clearBtn.onclick = ()=>{ ui.script.value=''; regenerate(); };

document.addEventListener('keydown', e=>{
  if(e.ctrlKey && e.key==='Enter'){ e.preventDefault(); regenerate(); }
  if(e.ctrlKey && e.key.toLowerCase()==='s'){ e.preventDefault(); ui.downloadBtn.click(); }
  if(e.ctrlKey && e.key.toLowerCase()==='l'){ e.preventDefault(); ui.clearBtn.click(); }
  if(e.ctrlKey && e.key==='/'){ e.preventDefault(); insertAtCursor(ui.script, '{CHORD:CTRL+V}'); }
});

function insertAtCursor(el, text){ const [s,e]=[el.selectionStart, el.selectionEnd]; el.value = el.value.slice(0,s)+text+el.value.slice(e); el.selectionStart = el.selectionEnd = s+text.length; }

const presets = [
  ['Fast Type', ()=>{ui.interDelay.value=30; ui.pressDelay.value=0;}],
  ['Normal Type', ()=>{ui.interDelay.value=70; ui.pressDelay.value=0;}],
  ['Human Type', ()=>{ui.interDelay.value=70; ui.pressDelay.value=0; ui.humanize.checked=true; ui.jitter.value=10;}],
  ['Paste', ()=>insertAtCursor(ui.script,'{CHORD:CTRL+V}')], ['Copy', ()=>insertAtCursor(ui.script,'{CHORD:CTRL+C}')], ['Cut', ()=>insertAtCursor(ui.script,'{CHORD:CTRL+X}')],
  ['Save', ()=>insertAtCursor(ui.script,'{CHORD:CTRL+S}')], ['Undo', ()=>insertAtCursor(ui.script,'{CHORD:CTRL+Z}')],
  ['Diskpart snippet', ()=>insertAtCursor(ui.script,'{TEXT:"diskpart\\nlist disk\\n"}')]
];
ui.presets.innerHTML = presets.map(([n],i)=>`<button data-i="${i}">${n}</button>`).join('');
ui.presets.onclick = e=>{ const i=e.target.dataset.i; if(i===undefined) return; presets[i][1](); regenerate(); };

function inferSampleRule(){
  const events = state.sample?.Events || [];
  const eventType = events[0]?.Type ?? 10;
  state.eventType = eventType;
  state.delayRule = 'event_self'; // inferred: Delay exists on every event in sample
}

function preprocess(script){
  return script.split('\n').filter(line=>!line.trimStart().startsWith('#')).join('\n');
}

function parseScript(input){
  const s = preprocess(input);
  function readEscapedText(i){
    let out='';
    while(i<s.length){
      if(s[i]==='\\'){
        if(s[i+1]==='{'||s[i+1]==='\\'){ out+=s[i+1]; i+=2; continue; }
      }
      if(s[i]==='{') break;
      out += s[i++];
    }
    return {text:out, i};
  }
  function parseBlock(i, inRepeat=false){
    const tokens=[];
    while(i<s.length){
      const {text, i:ni}=readEscapedText(i); i=ni; if(text) tokens.push({type:'TEXT_RAW', text});
      if(i>=s.length) break;
      const end = s.indexOf('}', i+1); if(end<0) throw new Error('Некорректный формат {…}');
      const cmd = s.slice(i+1,end).trim(); i=end+1;
      if(cmd==='/REPEAT'){
        if(!inRepeat) throw new Error('Лишний {/REPEAT}');
        return {tokens, i, closed:true};
      }
      if(cmd.startsWith('REPEAT:')){
        const n = Number(cmd.split(':')[1]); if(!Number.isInteger(n)||n<1) throw new Error('Некорректный {REPEAT:n}');
        const inner = parseBlock(i, true); if(!inner.closed) throw new Error('Незакрытый {/REPEAT}');
        tokens.push({type:'REPEAT', n, tokens:inner.tokens}); i=inner.i; continue;
      }
      tokens.push(parseCommand(cmd));
    }
    return {tokens, i, closed:!inRepeat};
  }
  return parseBlock(0).tokens;
}

function parseCommand(cmd){
  if(['ENTER','TAB','SPACE','BACKSPACE','ESC'].includes(cmd)) return {type:'KEY', key:cmd};
  if(cmd.startsWith('DELAY:')) return {type:'DELAY', ms:Number(cmd.slice(6))};
  if(cmd.startsWith('RAW:')) return {type:'RAW', key:cmd.slice(4).trim().toUpperCase()};
  if(cmd.startsWith('CHORD:')) return {type:'CHORD', value:cmd.slice(6).trim().toUpperCase()};
  if(cmd.startsWith('DOWN:')) return {type:'DOWN', key:cmd.slice(5).trim().toUpperCase()};
  if(cmd.startsWith('UP:')) return {type:'UP', key:cmd.slice(3).trim().toUpperCase()};
  if(cmd.startsWith('HOLD:')){ const p=cmd.split(':'); return {type:'HOLD', key:(p[1]||'').trim().toUpperCase(), ms:Number(p[2])}; }
  if(cmd.startsWith('TEXT:')){ return {type:'TEXT_RAW', text:parseQuoted(cmd.slice(5).trim())}; }
  throw new Error(`Неизвестная команда {${cmd}}`);
}

function parseQuoted(q){
  if(!q.startsWith('"')||!q.endsWith('"')) throw new Error('TEXT должен быть в кавычках');
  let out='';
  for(let i=1;i<q.length-1;i++){
    if(q[i]==='\\'){ const n=q[++i]; if(n==='n') out+='\n'; else if(n==='"') out+='"'; else if(n==='\\') out+='\\'; else throw new Error('Неверный escape в TEXT'); }
    else out+=q[i];
  }
  return out;
}

function flatten(tokens){ return tokens.flatMap(t=>t.type==='REPEAT' ? Array.from({length:t.n}, ()=>flatten(t.tokens)).flat() : [t]); }

function charToUS(ch){
  const punct = {
    ' ':'SPACE','\n':'ENTER','\t':'TAB',';':'SEMICOLON',':':['SEMICOLON',true],"'":'APOSTROPHE','"':['APOSTROPHE',true],',':'COMMA','<':['COMMA',true],'.':'DOT','>':['DOT',true],'/':'SLASH','?':['SLASH',true],
    '-':'MINUS','_':['MINUS',true],'=':'EQUAL','+':['EQUAL',true],'[':'LBRACKET','{':['LBRACKET',true],']':'RBRACKET','}':['RBRACKET',true],'\\':'BACKSLASH','|':['BACKSLASH',true],'`':'GRAVE','~':['GRAVE',true],
    '!':['1',true],'@':['2',true],'#':['3',true],'$':['4',true],'%':['5',true],'^':['6',true],'&':['7',true],'*':['8',true],'(':['9',true],')':['0',true]
  };
  if(/[a-z]/.test(ch)) return {key:ch.toUpperCase(), shift:false, out:ch};
  if(/[A-Z]/.test(ch)) return {key:ch, shift:true, out:ch};
  if(/[0-9]/.test(ch)) return {key:ch, shift:false, out:ch};
  if(punct[ch]){ const v=punct[ch]; return Array.isArray(v)?{key:v[0], shift:v[1], out:ch}:{key:v, shift:false, out:ch}; }
  return null;
}

function applyDelay(events, idx, ms){
  if(idx<0 || idx>=events.length) return;
  events[idx].Delay = String(Math.max(0, Math.round(Number(events[idx].Delay||0)+ms)));
}

function compile(tokens){
  const messages=[]; const events=[]; let typed=''; state.symbolUsage=new Set(); state.stickyMods=new Set();
  const rev = reverseMap();
  const settings = {
    inter: Math.max(0, Number(ui.interDelay.value)||0),
    press: Math.max(0, Number(ui.pressDelay.value)||0),
    human: ui.humanize.checked,
    jitter: Math.max(0, Number(ui.jitter.value)||0),
    jitterOnlyText: ui.jitterOnlyText.checked
  };
  const jitter = (ms, text)=> !settings.human || (settings.jitterOnlyText && !text) ? ms : Math.max(0, ms + Math.floor((Math.random()*2-1)*settings.jitter));
  const btn = k => state.mapping?.[k];
  const push = (action,key,delay)=>{
    const b=btn(key); if(b===undefined){ messages.push({level:'err', text:`Отсутствует KEY_NAME в mapping: ${key}`}); return; }
    events.push({Action:action, Button:Number(b), Delay:String(Math.max(0,Math.round(delay))), Type:state.eventType??10});
  };
  const tap = (key,text=false)=>{ push('down',key,settings.press); push('up',key,jitter(settings.inter,text)); };

  for(const t of tokens){
    if(t.type==='TEXT_RAW'){
      for(const ch of t.text){
        const p = charToUS(ch);
        if(!p){ messages.push({level:'err', text:`Неизвестный символ: ${JSON.stringify(ch)}`}); typed += '[?]'; continue; }
        state.symbolUsage.add(`${ch} -> ${p.shift?'SHIFT+':''}${p.key}`);
        if(ch===':') state.symbolUsage.add(': -> SHIFT+SEMICOLON');
        if(ch===';') state.symbolUsage.add('; -> SEMICOLON');
        if(p.shift){
          push('down','SHIFT',0);
          push('down',p.key,settings.press);
          push('up',p.key,jitter(settings.inter,true));
          push('up','SHIFT',0);
        } else tap(p.key,true);
        typed += p.out;
      }
    } else if(t.type==='KEY'){ tap(t.key,false); typed += t.key==='ENTER'?'\n':(t.key==='TAB'?'\t':(t.key==='SPACE'?' ':'['+t.key+']')); }
    else if(t.type==='RAW'){ tap(t.key,false); typed += `[${t.key}]`; }
    else if(t.type==='CHORD'){
      const parts=t.value.split('+').map(x=>x.trim()).filter(Boolean); if(parts.length<2){ messages.push({level:'err', text:`Некорректный CHORD: ${t.value}`}); continue; }
      const mods=parts.slice(0,-1); const main=parts.at(-1);
      mods.forEach(m=>push('down',m,0)); push('down',main,settings.press); push('up',main,jitter(settings.inter,false)); [...mods].reverse().forEach(m=>push('up',m,0));
      typed += `[${t.value}]`;
    } else if(t.type==='DOWN'){ push('down',t.key,settings.inter); if(['SHIFT','CTRL','ALT'].includes(t.key)) state.stickyMods.add(t.key); typed += `[DOWN:${t.key}]`; }
    else if(t.type==='UP'){ push('up',t.key,settings.inter); state.stickyMods.delete(t.key); typed += `[UP:${t.key}]`; }
    else if(t.type==='HOLD'){ if(t.ms<0||!Number.isFinite(t.ms)){ messages.push({level:'err', text:`Некорректный HOLD ms: ${t.ms}`}); continue; } push('down',t.key,t.ms); push('up',t.key,settings.inter); typed += `[HOLD:${t.key}:${t.ms}]`; }
    else if(t.type==='DELAY'){
      if(!Number.isFinite(t.ms)||t.ms<0||t.ms>3600000){ messages.push({level:'err', text:`Некорректная задержка: ${t.ms}`}); continue; }
      if(events.length===0) messages.push({level:'warn', text:'{DELAY} в начале пропущен (нет предыдущего события)'});
      else applyDelay(events, events.length-1, t.ms);
      typed += `[DELAY:${t.ms}]`;
    }
  }
  const endDelay = Math.max(0, Number(ui.endDelay.value)||0);
  if(endDelay && events.length) applyDelay(events, events.length-1, endDelay);
  if(state.stickyMods.size) messages.push({level:'warn', text:`Залипшие модификаторы: ${[...state.stickyMods].join(', ')}`});
  return {events, messages, typed, rev};
}

function reverseMap(){ const rev={}; Object.entries(state.mapping||{}).forEach(([k,v])=>rev[Number(v)]=k); return rev; }

function refreshCoverage(){
  const has = requiredCoverageKeys.filter(k=>state.mapping?.[k]!==undefined);
  const miss = requiredCoverageKeys.filter(k=>state.mapping?.[k]===undefined);
  ui.coverage.innerHTML = `Coverage: ${has.length}/${requiredCoverageKeys.length}\n<span class="${miss.length?'warn':'ok'}">Missing: ${miss.length?miss.join(', '):'none'}</span>`;
}
function coverageReportText(){
  const miss = requiredCoverageKeys.filter(k=>state.mapping?.[k]===undefined);
  return `Coverage ${requiredCoverageKeys.length-miss.length}/${requiredCoverageKeys.length}\nMissing:\n${miss.join('\n')||'none'}`;
}

function generateGuid(){ const d=new Date(); return `${d.getFullYear()}_${String(d.getMonth()+1).padStart(2,'0')}_${String(d.getDate()).padStart(2,'0')}_${String(d.getHours()).padStart(2,'0')}_${String(d.getMinutes()).padStart(2,'0')}_${String(d.getSeconds()).padStart(2,'0')}_${String(d.getMilliseconds()).padStart(3,'0')}`; }

function regenerate(){
  const msgs=[];
  if(!state.sample){ showMessages([{level:'err', text:'нужен sample.mac'}]); return; }
  if(!state.mapping){ msgs.push({level:'warn', text:'mapping.json не загружен; можно скачать template'}); }
  try {
    const tokens = flatten(parseScript(ui.script.value||''));
    const {events, messages, typed, rev} = compile(tokens);
    const mac = structuredClone(state.sample);
    mac.MacroName = (ui.macroName.value || 'Macro').trim();
    mac.Guid = generateGuid();
    mac.Events = events;
    state.generated = mac;

    const total = events.reduce((a,e)=>a+Number(e.Delay||0),0);
    ui.summary.textContent = `Events: ${events.length}\nTotal delay: ${total} ms\nDelay rule: per-event (from sample)`;
    ui.typed.textContent = typed;
    ui.symbolMap.textContent = [...state.symbolUsage].sort().join('\n') || '(none)';
    ui.eventPreview.textContent = events.slice(0,60).map((e,i)=>`${i+1}. ${e.Action} ${rev[e.Button]||'?'} (${e.Button}) Delay=${e.Delay}`).join('\n');
    ui.jsonPreview.textContent = JSON.stringify(mac, null, ui.pretty.checked?2:0);
    showMessages([...msgs, ...messages]);
    refreshCoverage();
  } catch(err){ showMessages([{level:'err', text:String(err.message||err)}]); }
}

function getSnippets(){ try { return JSON.parse(localStorage.getItem('rd_snippets')||'[]'); } catch { return []; } }
function setSnippets(v){ localStorage.setItem('rd_snippets', JSON.stringify(v)); }
function renderSnippets(){
  const list = getSnippets();
  ui.snippetList.innerHTML = list.length ? list.map((s,i)=>`<div class="row"><b>${s.name}</b><button data-i="${i}" data-a="insert">Insert</button><button data-i="${i}" data-a="delete">Delete</button></div>`).join('') : 'No snippets';
}
ui.saveSnippetBtn.onclick = ()=>{ const name=ui.snippetName.value.trim(); if(!name) return; const list=getSnippets(); list.push({name, script:ui.script.value}); setSnippets(list); renderSnippets(); };
ui.snippetList.onclick = e=>{ const i=Number(e.target.dataset.i); const a=e.target.dataset.a; if(Number.isNaN(i)) return; const list=getSnippets(); if(a==='insert') insertAtCursor(ui.script, list[i].script); if(a==='delete'){ list.splice(i,1); setSnippets(list); renderSnippets(); } };

renderSnippets();
refreshCoverage();
showMessages([{level:'warn', text:'Load sample.mac to start'}]);
