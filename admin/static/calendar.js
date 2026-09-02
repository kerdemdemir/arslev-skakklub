/* Kalender-editoren: tilføj og fjern datoer og sæsoner.
 *
 * Feltnavnene bærer sæsonens nummer ("s0_date", "s1_date" osv.), fordi
 * serveren læser hver sæson for sig med form.getlist(). Nye sæsoner får
 * derfor et nummer, der ikke er brugt før - også hvis en sæson er fjernet.
 */
(function () {
  'use strict';

  const seasons = document.getElementById('seasons');
  const rowTpl = document.getElementById('rowTpl');
  const seasonTpl = document.getElementById('seasonTpl');

  // Næste ledige sæsonnummer: ét over det højeste, der findes i forvejen.
  let nextIndex = 0;
  seasons.querySelectorAll('.season').forEach(f => {
    nextIndex = Math.max(nextIndex, +f.dataset.index + 1);
  });

  function fill(fragment, index) {
    fragment.querySelectorAll('[name]').forEach(el => {
      el.name = el.name.replace('__S__', 's' + index);
    });
    return fragment;
  }

  function isoWeek(value) {
    // ISO 8601: ugen hører til det år, hvor dens torsdag ligger.
    const d = new Date(value + 'T00:00:00');
    if (isNaN(d)) return '–';
    const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
    const start = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
    return Math.ceil(((t - start) / 86400000 + 1) / 7);
  }

  function addRow(fieldset) {
    const index = fieldset.dataset.index;
    const frag = fill(rowTpl.content.cloneNode(true), index);
    fieldset.querySelector('tbody').appendChild(frag);
  }

  // Én lytter på hele formularen frem for én pr. knap, så nye rækker og
  // sæsoner virker uden at skulle bindes op bagefter.
  document.getElementById('calForm').addEventListener('click', e => {
    const add = e.target.closest('.addrow');
    if (add) { addRow(add.closest('.season')); return; }

    const rm = e.target.closest('.rm');
    // Hele rækken fjernes, så dato, aktivitet og type forsvinder sammen.
    // Det er det, der holder serverens tre getlist-lister på linje.
    if (rm) rm.closest('tr').remove();
  });

  // Vis ugenummeret, så snart en dato skrives.
  document.getElementById('calForm').addEventListener('change', e => {
    if (e.target.type !== 'date') return;
    const wk = e.target.closest('tr').querySelector('.wk');
    if (wk) wk.textContent = e.target.value ? isoWeek(e.target.value) : '–';
  });

  document.getElementById('addSeason').addEventListener('click', () => {
    const index = nextIndex++;
    const frag = fill(seasonTpl.content.cloneNode(true), index);
    const fieldset = frag.querySelector('.season');
    fieldset.dataset.index = index;
    seasons.appendChild(frag);
    addRow(fieldset);
    fieldset.querySelector('input[name$="_kicker"]').focus();
  });
})();
