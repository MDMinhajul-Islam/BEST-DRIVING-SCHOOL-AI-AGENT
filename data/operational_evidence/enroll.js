/*
 | Course page enrolment form (resources/views/redesign/pages/course.blade.php).
 | Vanilla JS; replaces the jQuery / SmartWizard / bootstrap-datepicker scripts
 | the six purchased-theme views carried. site.js handles the hero price
 | picker outputs; this file keeps the form in step with it.
 |
 | Hooks:
 |   [data-enroll]                     page wrapper (also [data-pk] for site.js)
 |   [data-enroll-form]                the <form>: data-enroll-api (slot endpoint),
 |                                     data-enroll-date-gap (days between rows),
 |                                     data-student-id-initial (student_id prefix)
 |   input[name=product_id]            the option radios — the source of truth
 |   [data-enroll-chip="<product id>"] hero mirror chips (also [data-pk-chip])
 |   [data-pk-select]                  hero <select> shown under 560px
 |   [data-appointment-block="<i>"]    adult rows; shown/enabled up to the checked
 |                                     radio's data-blocks, hidden AND disabled beyond
 |   [data-enroll-row]                 a date + time pair: [data-enroll-date] fills
 |                                     [data-enroll-time] from the API on change
 |   [data-enroll-pairs] [data-enroll-pair] [data-enroll-pair-fields]
 |   [data-enroll-new] [data-enroll-new-rows]   teen pairing
 |   [data-review="<field>"]           the confirmation summary
 |
 | If this never runs the page still posts: the radios, the hidden inputs and
 | native `required` validation are all server-rendered. What is lost is the
 | composed student_name / dob / address / student_id, which the form request
 | then rejects rather than accepting half-filled.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-enroll]');
  if (!root) return;
  var form = root.querySelector('[data-enroll-form]');
  if (!form) return;

  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || root).querySelectorAll(sel)); };
  var byId = function (id) { return form.querySelector('#' + id); };
  var val = function (id) { var el = byId(id); return el ? el.value : ''; };

  /* ---------- option radios <-> hero chips ---------- */
  var radios = $$('input[name="product_id"][type="radio"]', form);
  var chips = $$('[data-enroll-chip]');
  var select = root.querySelector('[data-pk-select]');
  var blocks = $$('[data-appointment-block]', form);

  var chipFor = function (id) {
    return chips.filter(function (c) { return c.getAttribute('data-enroll-chip') === String(id); })[0] || null;
  };
  var radioFor = function (id) {
    return radios.filter(function (r) { return r.value === String(id); })[0] || null;
  };

  // Hidden rows are disabled as well: a disabled field is not submitted and its
  // `required` does not block submission, so the posted appointment_date[]
  // always has exactly as many entries as the option being bought.
  var showRows = function (count) {
    blocks.forEach(function (block) {
      var visible = parseInt(block.getAttribute('data-appointment-block'), 10) < count;
      block.hidden = !visible;
      $$('input, select', block).forEach(function (field) { field.disabled = !visible; });
    });
  };

  var syncChip = function (id) {
    var chip = chipFor(id);
    if (!chip) return;
    if (chip.getAttribute('aria-checked') !== 'true') chip.click();   // site.js applies price/label/panels
    chips.forEach(function (c) { c.setAttribute('aria-checked', c === chip ? 'true' : 'false'); });
  };
  var syncRadio = function (id) {
    var radio = radioFor(id);
    if (!radio || radio.checked) return;
    radio.checked = true;
    radio.dispatchEvent(new Event('change', { bubbles: true }));
  };

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () { syncRadio(chip.getAttribute('data-enroll-chip')); });
  });
  if (select) {
    select.addEventListener('change', function () {
      var chip = chips.filter(function (c) { return c.dataset.value === select.value; })[0];
      if (chip) syncRadio(chip.getAttribute('data-enroll-chip'));
    });
  }
  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      if (!radio.checked) return;
      syncChip(radio.value);
      if (blocks.length) showRows(parseInt(radio.getAttribute('data-blocks'), 10) || 0);
    });
  });
  var checked = radios.filter(function (r) { return r.checked; })[0];
  if (checked) {
    syncChip(checked.value);
    if (blocks.length) showRows(parseInt(checked.getAttribute('data-blocks'), 10) || 0);
  }

  /* ---------- appointment dates -> time slots ---------- */
  var api = form.getAttribute('data-enroll-api') || '';
  var gap = parseInt(form.getAttribute('data-enroll-date-gap'), 10) || 1;
  var dates = $$('[data-enroll-date]', form);

  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var isoLocal = function (d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
  var addDays = function (iso, n) {
    var p = iso.split('-');
    return isoLocal(new Date(+p[0], +p[1] - 1, +p[2] + n));
  };
  var tomorrow = addDays(isoLocal(new Date()), 1);

  var timeFor = function (date) {
    var row = date.closest('[data-enroll-row]');
    return row ? row.querySelector('[data-enroll-time]') : null;
  };
  var setOptions = function (sel, list, emptyText) {
    if (!sel) return;
    sel.innerHTML = '';
    if (!list || !list.length) {
      var o = document.createElement('option');
      o.value = '';
      o.textContent = emptyText;
      sel.appendChild(o);
      return;
    }
    list.forEach(function (t) {
      var o = document.createElement('option');
      o.value = t;
      o.textContent = t;
      sel.appendChild(o);
    });
  };
  var loadTimes = function (date, sel) {
    if (!api || !sel) return;
    setOptions(sel, null, 'Loading…');
    fetch(api + '?date=' + encodeURIComponent(date), { headers: { Accept: 'application/json' }, cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (list) {
        // The DPS endpoint can answer with an object (array_diff keeps keys).
        if (!Array.isArray(list)) list = Object.keys(list || {}).map(function (k) { return list[k]; });
        setOptions(sel, list, 'All slots booked');
      })
      .catch(function () { setOptions(sel, null, 'Error loading slots'); });
  };

  dates.forEach(function (date, i) {
    if (!date.min) date.min = tomorrow;
    date.addEventListener('change', function () {
      var sel = timeFor(date);
      if (!date.value) { setOptions(sel, null, 'Choose a date first'); return; }
      loadTimes(date.value, sel);
      // Later rows start after this one and are cleared, as the old datepicker chain did.
      for (var j = i + 1; j < dates.length; j++) {
        dates[j].value = '';
        setOptions(timeFor(dates[j]), null, 'Choose a date first');
      }
      if (dates[i + 1]) dates[i + 1].min = addDays(date.value, gap);
    });
  });

  /* ---------- teen pairing ---------- */
  var pairInput = form.querySelector('input[name="pair_id"]');
  var pairsBox = form.querySelector('[data-enroll-pairs]');
  var pairFields = form.querySelector('[data-enroll-pair-fields]');
  var newRows = form.querySelector('[data-enroll-new-rows]');
  var pairButtons = $$('[data-enroll-pair]', form);

  var hidden = function (name, value) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    return input;
  };
  var setNewRows = function (on) {
    if (!newRows) return;
    newRows.hidden = !on;
    $$('input, select', newRows).forEach(function (f) { f.disabled = !on; });
  };

  pairButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      pairButtons.forEach(function (o) { o.classList.remove('is-paired'); o.textContent = 'Pair up'; });
      btn.classList.add('is-paired');
      btn.textContent = 'Paired up ✓';
      if (pairInput) pairInput.value = btn.getAttribute('data-enroll-pair') || '';
      if (pairFields) {
        pairFields.innerHTML = '';
        var list = [];
        try { list = JSON.parse(btn.getAttribute('data-appointments') || '[]'); } catch (e) { list = []; }
        for (var k = 0; k < 7; k++) {
          var a = list[k];
          if (!a || !a.appointment_date) continue;
          var dp = String(a.appointment_date).split('-');
          var date = dp.length === 3 ? dp[1] + '/' + dp[2] + '/' + dp[0] : a.appointment_date;
          var hhmm = function (t) { return String(t || '').split(':').slice(0, 2).join(':'); };
          pairFields.appendChild(hidden('appointment_dates[]', date));
          pairFields.appendChild(hidden('appointment_times[]', hhmm(a.appointment_time_start) + ' - ' + hhmm(a.appointment_time_end)));
        }
      }
      setNewRows(false);
    });
  });
  var newBtn = form.querySelector('[data-enroll-new]');
  if (newBtn) {
    newBtn.addEventListener('click', function () {
      if (pairsBox) pairsBox.hidden = true;
      setNewRows(true);
      if (pairInput) pairInput.value = '';
      if (pairFields) pairFields.innerHTML = '';
      pairButtons.forEach(function (o) { o.classList.remove('is-paired'); o.textContent = 'Pair up'; });
    });
  }

  /* ---------- the confirmation summary ---------- */
  var reviews = $$('[data-review]', form);
  var composed = function () {
    var gender = form.querySelector('input[name="gender"]:checked');
    var mm = val('dob_mm'), dd = val('dob_dd'), yy = val('dob_yy');
    return {
      student_name: (val('students_name_first_name') + ' ' + val('students_name_last_name')).trim(),
      student_email: val('student_email'),
      gender: gender ? gender.value : '',
      dob: mm || dd || yy ? mm + '-' + dd + '-' + yy : '',
      student_cell: val('student_cell'),
      home_phone: val('home_phone'),
      address: [val('street_address'), val('city'), val('state'), val('zip_code')].filter(Boolean).join(', '),
      parent_name: val('parent_name'),
      parent_email: val('parent_email'),
      parent_cell: val('parent_cell')
    };
  };
  var updateReview = function () {
    var v = composed();
    reviews.forEach(function (node) {
      var value = v[node.getAttribute('data-review')];
      node.textContent = value ? value : '—';
    });
  };
  if (reviews.length) {
    form.addEventListener('input', updateReview);
    form.addEventListener('change', updateReview);
    updateReview();
  }

  /* ---------- hidden fields, composed exactly as the old templates did ---------- */
  var compose = function () {
    var dd = val('dob_dd'), mm = val('dob_mm'), yy = val('dob_yy');
    var first = val('students_name_first_name'), last = val('students_name_last_name');
    var set = function (id, value) { var el = byId(id); if (el) el.value = value; };
    set('dob', dd + '-' + mm + '-' + yy);
    set('address', val('street_address') + ',' + val('city') + ',' + val('state') + ',' + val('zip_code'));
    set('student_name', first + ' ' + last);
    set('student_id', (form.getAttribute('data-student-id-initial') || '') + '-' + first + '-' + dd + mm + yy);
  };
  /* Native constraint validation runs before compose so an empty date of birth can never post as "--".
     The first invalid field is scrolled to the middle of a phone screen and focused. */
  var guard = function (e) {
    if (form.checkValidity()) { compose(); return; }
    e.preventDefault();
    var first = form.querySelector(':invalid');
    if (first) { first.scrollIntoView({ block: 'center' }); first.focus(); }
    form.reportValidity();
  };
  form.addEventListener('submit', guard);

  /* Server-side rejection: land on the error list instead of the top of the page. */
  var serverErrors = form.querySelector('[data-form-errors]');
  if (serverErrors) { serverErrors.scrollIntoView({ block: 'center' }); serverErrors.focus({ preventScroll: true }); }
})();
