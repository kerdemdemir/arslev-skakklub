/* Partiviser til Årslev Skakklubs admin-side.
 *
 * Brættet og Stockfish-motoren følger samme mønster som VisionChessVAR:
 * en tabel med brikbilleder, og motoren som en Web Worker, der tales UCI med.
 * Forskellen er, at brættet her tegnes ud fra en FEN. Serveren har allerede
 * læst PGN'en med python-chess, så der er ingen skakregler i browseren.
 */
(function () {
  'use strict';

  const G = window.GAME;                       // {start_fen, moves:[...]}
  if (!G) return;

  // ---------------------------------------------------------------- brættet
  const PIECES = '/admin/static/pieces/';
  const FILES = 'abcdefgh';

  function fenToBoard(fen) {
    const rows = fen.split(' ')[0].split('/');
    const out = {};
    rows.forEach((row, i) => {
      const rank = 8 - i;
      let file = 0;
      for (const ch of row) {
        if (/\d/.test(ch)) { file += +ch; continue; }
        const code = (ch === ch.toUpperCase() ? 'w' : 'b') + ch.toUpperCase();
        out[FILES[file] + rank] = code;
        file++;
      }
    });
    return out;
  }

  // Brættet er et CSS-grid og ikke en tabel: tomme rækker i en tabel klapper
  // sammen, så de midterste linjer forsvandt, når der ikke stod brikker på dem.
  function drawBoard(el, fen, highlight, flipped) {
    const board = fenToBoard(fen);
    const hi = new Set(highlight || []);
    const ranks = flipped ? [1, 2, 3, 4, 5, 6, 7, 8] : [8, 7, 6, 5, 4, 3, 2, 1];
    const files = flipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
    let h = '';
    for (const r of ranks) {
      for (const f of files) {
        const sq = FILES[f] + r;
        const dark = (f + r) % 2 === 1;      // a1 (f=0, r=1) er et mørkt felt
        const p = board[sq];
        const cls = 'sq ' + (dark ? 'd' : 'l') + (hi.has(sq) ? ' hi' : '');
        let coord = '';
        if (f === files[0]) coord += `<span class="rk">${r}</span>`;
        if (r === ranks[ranks.length - 1]) coord += `<span class="fl">${FILES[f]}</span>`;
        const img = p ? `<img src="${PIECES}${p}.png" alt="">` : '';
        h += `<div class="${cls}">${coord}${img}</div>`;
      }
    }
    el.innerHTML = `<div class="board">${h}</div>`;
  }

  // ------------------------------------------------------------- Stockfish
  // Den enkelttrådede lite-udgave kræver ingen SharedArrayBuffer og dermed
  // ingen særlige cross-origin-headere. Selve wasm-filen (7 MB) hentes fra
  // jsDelivr; serveren udleverer kun de 21 KB worker-kode. Siden er bag
  // login, så ingen almindelig besøgende henter noget fra et CDN.
  const WASM = 'https://cdn.jsdelivr.net/gh/kerdemdemir/visionchess-engine-nets'
             + '@sf-18.0.8/stockfish-18-lite-single.wasm';

  let sf = null, sfReady = false, sfJob = null;
  const sfQueue = [];
  const evalCache = {};                        // fen -> centipawns set fra hvid

  function sfInit() {
    if (sf) return;
    sf = new Worker('/admin/static/sf/stockfish-18-lite-single.js#' + encodeURIComponent(WASM));
    sf.onmessage = e => onSf(typeof e.data === 'string' ? e.data : (e.data && e.data.data) || '');
    sf.onerror = () => { setStatus('Motoren kunne ikke indlæses.'); sfJob = null; };
    sf.postMessage('uci');
    sf.postMessage('isready');
  }

  function analyse(fen, depth, priority) {
    return new Promise(resolve => {
      const job = { fen, depth: depth || 14, resolve, score: null, best: null };
      if (priority) sfQueue.unshift(job); else sfQueue.push(job);
      pump();
    });
  }

  function pump() {
    sfInit();
    if (sfJob || !sfQueue.length) return;
    if (!sfReady) { setTimeout(pump, 200); return; }
    sfJob = sfQueue.shift();
    sf.postMessage('position fen ' + sfJob.fen);
    sf.postMessage('go depth ' + sfJob.depth);
  }

  function onSf(line) {
    if (line === 'uciok' || line === 'readyok') { sfReady = true; pump(); return; }
    if (!sfJob) return;
    if (line.startsWith('info') && line.includes('score')) {
      const mate = line.match(/score mate (-?\d+)/);
      const cp = line.match(/score cp (-?\d+)/);
      if (mate) sfJob.score = { mate: +mate[1] };
      else if (cp) sfJob.score = { cp: +cp[1] };
    } else if (line.startsWith('bestmove')) {
      sfJob.best = (line.split(' ')[1] || '').trim();
      const j = sfJob; sfJob = null;
      j.resolve({ score: j.score, best: j.best });
      pump();
    }
  }

  // Motoren svarer set fra den, der er i trækket. Vi regner altid i hvids favør.
  function toWhiteCp(score, fen) {
    if (!score) return null;
    const whiteToMove = fen.split(' ')[1] === 'w';
    const v = ('mate' in score)
      ? (score.mate > 0 ? 100000 - score.mate : -100000 - score.mate)
      : score.cp;
    return whiteToMove ? v : -v;
  }

  function cpText(cp) {
    if (cp == null) return '–';
    if (cp >= 99000) return 'mat om ' + (100000 - cp);
    if (cp <= -99000) return 'mat om ' + (100000 + cp);
    const p = cp / 100;
    return (p > 0 ? '+' : '') + p.toFixed(2);
  }

  // ------------------------------------------------------------- tilstand
  const elBoard = document.getElementById('board');
  const elMoves = document.getElementById('movelist');
  const elPly = document.getElementById('plyLabel');
  const elEval = document.getElementById('evalText');
  const elBar = document.getElementById('evalFill');
  const elBest = document.getElementById('bestMove');
  const elStatus = document.getElementById('engineStatus');
  const elComment = document.getElementById('moveComment');

  let ply = 0;                                 // 0 = startstilling
  let flipped = false;
  let autoEval = false;

  function setStatus(t) { if (elStatus) elStatus.textContent = t || ''; }

  function fenAt(p) { return p === 0 ? G.start_fen : G.moves[p - 1].fen; }
  function hiAt(p) { return p === 0 ? [] : [G.moves[p - 1].from, G.moves[p - 1].to]; }

  function renderMoveList() {
    let h = '';
    for (let i = 0; i < G.moves.length; i += 2) {
      const no = i / 2 + 1;
      const w = G.moves[i], b = G.moves[i + 1];
      h += `<div class="mrow"><span class="no">${no}.</span>`;
      h += `<button class="mv" data-ply="${w.ply}">${w.san}</button>`;
      h += b ? `<button class="mv" data-ply="${b.ply}">${b.san}</button>` : '<span class="mv"></span>';
      h += '</div>';
    }
    elMoves.innerHTML = h;
    elMoves.querySelectorAll('.mv[data-ply]').forEach(btn => {
      btn.addEventListener('click', () => goto(+btn.dataset.ply));
    });
  }

  function paintEval(cp) {
    if (elEval) elEval.textContent = cpText(cp);
    if (elBar) {
      // ±600 centipawns fylder hele bjælken
      const clamped = Math.max(-600, Math.min(600, cp == null ? 0 : cp));
      elBar.style.height = (50 + clamped / 12) + '%';
    }
  }

  function goto(p) {
    ply = Math.max(0, Math.min(G.moves.length, p));
    drawBoard(elBoard, fenAt(ply), hiAt(ply), flipped);

    elPly.textContent = ply === 0
      ? 'Startstilling'
      : `${Math.ceil(ply / 2)}${ply % 2 ? '.' : '…'} ${G.moves[ply - 1].san}`
        + `  (halvtræk ${ply} af ${G.moves.length})`;

    const c = ply > 0 ? (G.moves[ply - 1].comment || '') : '';
    if (elComment) { elComment.textContent = c; elComment.hidden = !c; }

    elMoves.querySelectorAll('.mv[data-ply]').forEach(b => {
      b.classList.toggle('on', +b.dataset.ply === ply);
    });
    const on = elMoves.querySelector('.mv.on');
    if (on) on.scrollIntoView({ block: 'nearest' });

    const fen = fenAt(ply);
    if (evalCache[fen] !== undefined) {
      paintEval(evalCache[fen]);
      if (elBest) elBest.textContent = '';
    } else {
      paintEval(null);
      if (elBest) elBest.textContent = '';
    }
    if (autoEval) evaluateCurrent();
  }

  function evaluateCurrent() {
    const fen = fenAt(ply);
    setStatus('Analyserer …');
    analyse(fen, 15, true).then(r => {
      const cp = toWhiteCp(r.score, fen);
      evalCache[fen] = cp;
      if (fenAt(ply) === fen) {                // brugeren kan have bladret videre
        paintEval(cp);
        if (elBest && r.best && r.best !== '(none)') {
          elBest.textContent = 'Motorens forslag: ' + r.best;
        }
      }
      setStatus('');
    });
  }

  // --------------------------------------------------------------- knapper
  document.getElementById('first').onclick = () => goto(0);
  document.getElementById('prev').onclick = () => goto(ply - 1);
  document.getElementById('next').onclick = () => goto(ply + 1);
  document.getElementById('last').onclick = () => goto(G.moves.length);
  document.getElementById('flip').onclick = () => {
    flipped = !flipped;
    drawBoard(elBoard, fenAt(ply), hiAt(ply), flipped);
  };

  const btnEval = document.getElementById('evalBtn');
  btnEval.onclick = () => {
    autoEval = !autoEval;
    btnEval.classList.toggle('on', autoEval);
    btnEval.textContent = autoEval ? 'Motor: til' : 'Motor: fra';
    if (autoEval) evaluateCurrent(); else setStatus('');
  };

  const btnScan = document.getElementById('scanBtn');
  btnScan.onclick = async () => {
    btnScan.disabled = true;
    const total = G.moves.length;
    for (let p = 0; p <= total; p++) {
      const fen = fenAt(p);
      if (evalCache[fen] === undefined) {
        setStatus(`Gennemgår partiet … ${p} af ${total}`);
        const r = await analyse(fen, 12, false);
        evalCache[fen] = toWhiteCp(r.score, fen);
      }
      if (p === ply) paintEval(evalCache[fen]);
    }
    markMistakes();
    setStatus('Gennemgang færdig.');
    btnScan.disabled = false;
  };

  // Et stort fald i vurderingen for den, der lige trak, markeres.
  function markMistakes() {
    for (let p = 1; p <= G.moves.length; p++) {
      const before = evalCache[fenAt(p - 1)];
      const after = evalCache[fenAt(p)];
      if (before == null || after == null) continue;
      const whiteMoved = p % 2 === 1;
      const loss = whiteMoved ? before - after : after - before;
      const btn = elMoves.querySelector(`.mv[data-ply="${p}"]`);
      if (!btn) continue;
      btn.classList.remove('blunder', 'mistake', 'inaccuracy');
      if (loss >= 300) btn.classList.add('blunder');
      else if (loss >= 150) btn.classList.add('mistake');
      else if (loss >= 70) btn.classList.add('inaccuracy');
    }
  }

  document.addEventListener('keydown', e => {
    if (/^(INPUT|TEXTAREA)$/.test(e.target.tagName)) return;
    const k = { ArrowLeft: ply - 1, ArrowRight: ply + 1, Home: 0, End: G.moves.length };
    if (k[e.key] !== undefined) { e.preventDefault(); goto(k[e.key]); }
  });

  renderMoveList();
  goto(0);
})();
