/* Drives the sorting desk: a recorded ticket slides in, its confidence bars fill, and it drops into a tray.

   All numbers come from data/demo.js, which triage/site.py writes from the result files. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var EASE = 'cubic-bezier(.23, 1, .32, 1)';

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  var pct = function (x) { return (100 * x).toFixed(1); };
  var money = function (x) { return '$' + x.toFixed(4); };

  // Count from the value on screen, not from zero, so a quick second click never jumps backwards.
  function tween(el, to, fmt, ms) {
    var from = typeof el._v === 'number' ? el._v : 0;
    el._v = to;
    if (el._raf) { cancelAnimationFrame(el._raf); }
    if (reduce.matches || from === to) { el.textContent = fmt(to); return; }
    var t0 = performance.now();
    (function step(now) {
      var k = Math.min(1, (now - t0) / (ms || 520));
      var eased = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(from + (to - from) * eased);
      if (k < 1) { el._raf = requestAnimationFrame(step); }
    })(t0);
  }

  function animate(el, frames, opts) {
    if (!el.animate) { return null; }
    if (reduce.matches) {
      // Keep the fade so the change is still visible, drop the movement.
      frames = frames.map(function (f) { return { opacity: f.opacity == null ? 1 : f.opacity }; });
    }
    return el.animate(frames, Object.assign({ easing: EASE, fill: 'backwards' }, opts));
  }

  function splitEmail(text) {
    var m = /^Subject:\s*(.*)\n+(?:Email:\s*)?([\s\S]*)$/.exec(text);
    return m ? { subject: m[1], body: m[2] } : { subject: '', body: text };
  }

  function themeToggle() {
    var root = document.documentElement;
    var order = ['auto', 'light', 'dark'];
    var cur = root.getAttribute('data-theme') || 'auto';
    var label = $('theme-label');
    label.textContent = cur[0].toUpperCase() + cur.slice(1);
    $('theme').addEventListener('click', function () {
      cur = order[(order.indexOf(cur) + 1) % order.length];
      if (cur === 'auto') { root.removeAttribute('data-theme'); } else { root.setAttribute('data-theme', cur); }
      label.textContent = cur[0].toUpperCase() + cur.slice(1);
      try { if (cur === 'auto') { localStorage.removeItem('triage-theme'); } else { localStorage.setItem('triage-theme', cur); } } catch (e) {}
    });
  }

  function start() {
    themeToggle();
    var d = window.DEMO_DATA && window.DEMO_DATA.triage;
    if (!d) {
      $('desk').innerHTML = '<p class="fail">The recorded data did not load. Reload the page, or open data/demo.json to read it directly.</p>';
      return;
    }

    var all = {};
    Object.keys(d.featured).forEach(function (k) { all[d.featured[k].id] = d.featured[k]; });
    d.tickets.forEach(function (t) { all[t.id] = t; });

    var picker = $('picker');
    d.tickets.forEach(function (t) {
      var o = document.createElement('option');
      o.value = t.id;
      o.textContent = t.email.split('\n')[0].replace('Subject: ', '').slice(0, 70);
      picker.appendChild(o);
    });

    $('thr').textContent = d.threshold.toFixed(3);

    // Three fixed bar rows. Updating them in place lets the CSS transition retarget mid-fill.
    var fields = [
      { key: 'category', label: 'category' },
      { key: 'priority', label: 'priority' },
      { key: 'account_id', label: 'account number', note: 'not rescaled' }
    ];
    var markLeft = (100 * d.threshold).toFixed(1) + '%';
    $('bars').innerHTML = fields.map(function (f, i) {
      return '<div class="bar" id="bar-' + i + '"><div class="bar__top"><span><span class="bar__field">' + f.label +
        (f.note ? ' <span class="bar__note">(' + f.note + ')</span>' : '') + '</span><br><span class="bar__value"></span></span>' +
        '<span class="num bar__num">0.00</span></div><div class="bar__track"><div class="bar__fill"></div>' +
        '<div class="bar__mark" style="left:' + markLeft + '"></div></div></div>';
    }).join('');
    var barEls = fields.map(function (f, i) { return $('bar-' + i); });

    var max = d.cost_per_1000.teacher;
    var rows = [['Small model only', d.cost_per_1000.small, false], ['Cascade', d.cost_per_1000.cascade, true], ['Teacher only', d.cost_per_1000.teacher, false]];
    $('meter').innerHTML = rows.map(function (r) {
      return '<div class="meter"' + (r[2] ? ' data-now="true"' : '') + '><span>' + r[0] + '</span><div class="meter__track"><div class="meter__fill" data-to="' +
        (r[1] / max).toFixed(4) + '"></div></div><span class="num">' + money(r[1]) + '</span></div>';
    }).join('');

    var seen = {};
    var tally = { open: 0, up: 0 };
    var timers = [];
    var MAX_STUBS = 6;

    function later(fn, ms) { timers.push(setTimeout(fn, reduce.matches ? 0 : ms)); }

    function fillBars(e) {
      var values = [
        [e.pred.category || 'none', e.confidence.category.chosen],
        [e.pred.priority || 'none', e.confidence.priority.chosen],
        [e.pred.account_id || 'none', e.account_confidence]
      ];
      barEls.forEach(function (el, i) {
        var v = values[i][1];
        el.setAttribute('data-low', String(v < d.threshold));
        el.querySelector('.bar__value').textContent = values[i][0];
        var fill = el.querySelector('.bar__fill');
        fill.style.transition = reduce.matches ? 'none' : 'transform 560ms ' + EASE + ' ' + (140 + i * 70) + 'ms';
        fill.style.transform = 'scaleX(' + v.toFixed(4) + ')';
        tween(el.querySelector('.bar__num'), v, function (x) { return x.toFixed(2); }, 700);
      });
    }

    function fillMeter() {
      document.querySelectorAll('.meter__fill').forEach(function (f, i) {
        f.style.transition = reduce.matches ? 'none' : 'transform 900ms ' + EASE + ' ' + (i * 90) + 'ms';
        f.style.transform = 'scaleX(' + Math.max(0.004, +f.getAttribute('data-to')) + ')';
      });
    }

    // FLIP: remember where the old stubs were, insert the new one, then slide the old ones into place.
    function drop(e) {
      var list = $(e.escalate ? 'up' : 'kept');
      var before = Array.prototype.map.call(list.children, function (li) { return [li, li.getBoundingClientRect().top]; });
      var s = splitEmail(e.email);
      var li = document.createElement('li');
      li.className = 'stub';
      li.setAttribute('data-id', e.id);
      li.innerHTML = '<span class="stub__subject">' + esc(s.subject || s.body) + '</span><span class="stub__meta"><span>' + esc(e.id) +
        (e.kind === 'off-task' ? ' <span class="odd">not a ticket</span>' : '') + '</span><span class="num">' + e.ticket_confidence.toFixed(2) + '</span></span>';
      list.insertBefore(li, list.firstChild);
      while (list.children.length > MAX_STUBS) { list.removeChild(list.lastChild); }
      $(e.escalate ? 'up-empty' : 'kept-empty').hidden = true;
      // Read every new position first, then start the animations, so layout is measured once.
      var moves = before.filter(function (p) { return p[0].parentNode; }).map(function (p) { return [p[0], p[1] - p[0].getBoundingClientRect().top]; });
      moves.forEach(function (m) {
        if (m[1]) { animate(m[0], [{ transform: 'translateY(' + m[1] + 'px)' }, { transform: 'none' }], { duration: 320 }); }
      });
      // Escalated tickets peel off at an angle, kept ones slide straight in.
      var from = e.escalate ? 'translate(-48px, -14px) rotate(7deg)' : 'translate(-36px, 0)';
      animate(li, [{ transform: from, opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 420 });
      markCurrent(e.id);
    }

    function markCurrent(id) {
      document.querySelectorAll('.stub').forEach(function (s) { var on = s.getAttribute('data-id') === id; s.setAttribute('data-current', String(on)); if (on) { s.setAttribute('aria-current', 'true'); } else { s.removeAttribute('aria-current'); } });
    }

    function show(e, button) {
      // Keep the open ticket in the address bar so a link lands on the same email.
      try { history.replaceState(null, '', '#' + e.id); } catch (err) {}
      timers.forEach(clearTimeout);
      timers = [];
      document.querySelectorAll('[data-pick]').forEach(function (b) { b.setAttribute('aria-pressed', String(b === button)); });

      var s = splitEmail(e.email);
      var slip = $('slip');
      slip.setAttribute('data-kind', e.kind);
      $('slip-id').textContent = e.id;
      $('slip-subject').textContent = s.subject || 'No subject line';
      $('email').textContent = s.body;
      $('slip-flag').textContent = 'Not a support email.';
      $('email').scrollTop = 0;
      if (slip.getAnimations) { slip.getAnimations().forEach(function (a) { a.cancel(); }); }
      animate(slip, [{ transform: 'translateX(-28px) rotate(-2deg)', opacity: 0 }, { transform: window.matchMedia('(min-width: 60em)').matches && !reduce.matches ? 'rotate(-0.6deg)' : 'none', opacity: 1 }], { duration: 360 });

      fillBars(e);
      $('json').textContent = JSON.stringify(e.pred, null, 1);

      var v = $('verdict');
      v.setAttribute('data-up', String(e.escalate));
      var line = e.escalate
        ? '<strong>Sent to the teacher</strong>Confidence ' + e.ticket_confidence.toFixed(2) + ' is below the threshold of ' + d.threshold.toFixed(3) + '.'
        : '<strong>Kept by the small model</strong>Confidence ' + e.ticket_confidence.toFixed(2) + ' clears the threshold of ' + d.threshold.toFixed(3) + '.';
      if (e.escalate && e.teacher) { line += '<span class="teacher">Teacher answer: ' + esc(JSON.stringify(e.teacher)) + '</span>'; }
      v.innerHTML = line;
      animate(v, [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { duration: 260, delay: reduce.matches ? 0 : 560 });

      var key = $('key');
      if (e.gold) {
        var same = e.pred.category === e.gold.category && e.pred.priority === e.gold.priority;
        key.textContent = 'Answer key: ' + e.gold.category + ', ' + e.gold.priority + '. The small model ' + (same ? 'matches it.' : 'does not match it.');
      } else {
        key.textContent = e.note || '';
      }

      $('meter-note').textContent = 'This email costs ' + (e.escalate ? money(d.teacher.cost_per_ticket) + ' because it goes to the teacher.' : '$0 because the small model keeps it.') +
        ' The cascade sends ' + pct(d.escalated_share) + ' percent of tickets up. Prices are the teacher API list price, peak rate.';

      if (seen[e.id]) { markCurrent(e.id); return; }
      seen[e.id] = true;
      later(function () {
        drop(e);
        tally.open += 1;
        if (e.escalate) { tally.up += 1; }
        tween($('kept-n'), tally.open - tally.up, function (x) { return Math.round(x); }, 300);
        tween($('up-n'), tally.up, function (x) { return Math.round(x); }, 300);
        tween($('s-open'), tally.open, function (x) { return Math.round(x); }, 300);
        tween($('s-up'), tally.up, function (x) { return Math.round(x); }, 300);
        tween($('s-cost'), tally.up * d.teacher.cost_per_ticket, function (x) { return '$' + x.toFixed(6); }, 700);
      }, 720);
    }

    document.querySelectorAll('[data-pick]').forEach(function (b) {
      b.addEventListener('click', function () { show(d.featured[b.getAttribute('data-pick')], b); });
    });
    picker.addEventListener('change', function () { if (picker.value) { show(all[picker.value], null); } });

    $('paste-go').addEventListener('click', function () {
      var btn = this;
      var msg = $('paste-msg');
      var text = $('paste').value.trim().replace(/\s+/g, ' ');
      if (!text) { msg.setAttribute('data-state', 'miss'); msg.textContent = 'Paste the subject and body of an email first.'; return; }
      btn.setAttribute('aria-busy', 'true');
      btn.disabled = true;
      requestAnimationFrame(function () {
        var hit = Object.keys(all).map(function (k) { return all[k]; }).filter(function (e) { return e.email.trim().replace(/\s+/g, ' ') === text; })[0];
        btn.removeAttribute('aria-busy');
        btn.disabled = false;
        if (hit) { msg.setAttribute('data-state', 'hit'); msg.textContent = 'Found in the recorded runs.'; show(hit, null); }
        else { msg.setAttribute('data-state', 'miss'); msg.textContent = 'That email is not in the recorded runs. This page cannot run the model. Clone the repository and run make serve to try your own.'; }
      });
    });

    var h = d.headline;
    var claims = [
      ['Urgency right before training', h.base_priority, 'percent', 'Always guessing high scores ' + h.trivial_priority.toFixed(1)],
      ['Urgency right after training', h.tuned_priority, 'percent', '95 percent interval ' + h.tuned_priority_ci[0].toFixed(1) + ' to ' + h.tuned_priority_ci[1].toFixed(1)],
      ['Sent to the teacher', 100 * d.escalated_share, 'percent', money(d.cost_per_1000.cascade) + ' per 1,000 tickets']
    ];
    $('claims').innerHTML = claims.map(function (c, i) {
      return '<div class="claim"><span class="claim__label">' + c[0] + '</span><span class="claim__value" id="claim-' + i + '">' + c[1].toFixed(1) +
        '</span> <span class="claim__unit">' + c[2] + '</span><span class="claim__source">' + c[3] + '</span></div>';
    }).join('');

    var c = d.cascade;
    $('cascade-table').innerHTML = '<caption class="sr">Cascade routes compared</caption>' +
      '<thead><tr><th scope="col">Route</th><th scope="col" class="num">Sent up</th><th scope="col" class="num">Both fields right</th><th scope="col" class="num">Per 1,000</th></tr></thead><tbody>' +
      [['Small model only', 0, c.student.acc, 0, false], ['Cascade', c.chosen.escalated, c.chosen.acc, c.chosen.cost_per_1000, true], ['Teacher only', 1, c.teacher.acc, c.teacher.cost_per_1000, false]]
        .map(function (r) { return '<tr' + (r[4] ? ' data-now="true"' : '') + '><td>' + r[0] + '</td><td class="num">' + pct(r[1]) + '%</td><td class="num">' + pct(r[2]) + '%</td><td class="num">' + money(r[3]) + '</td></tr>'; }).join('') + '</tbody>';

    // The headline figures and the cost bars count up once, when they first scroll into view.
    if ('IntersectionObserver' in window && !reduce.matches) {
      claims.forEach(function (cl, i) { var el = $('claim-' + i); el._v = 0; el.textContent = '0.0'; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) { return; }
          io.unobserve(en.target);
          if (en.target.id === 'claims') {
            claims.forEach(function (cl, i) { tween($('claim-' + i), cl[1], function (x) { return x.toFixed(1); }, 900); });
          } else { fillMeter(); }
        });
      }, { threshold: 0.3 });
      io.observe($('claims'));
      io.observe($('meter'));
    } else { fillMeter(); }

    var fromHash = all[decodeURIComponent(location.hash.slice(1))];
    var first = fromHash || d.featured.easy;
    var firstKey = Object.keys(d.featured).filter(function (k) { return d.featured[k].id === first.id; })[0];
    show(first, firstKey ? document.querySelector('[data-pick="' + firstKey + '"]') : null);
    if (!firstKey) { picker.value = first.id; }
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', start); } else { start(); }
})();
