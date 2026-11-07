const input = document.querySelector('#search');
const filters = [...document.querySelectorAll('[data-filter]')];
const cards = [...document.querySelectorAll('[data-card]')];
const grid = document.querySelector('.grid');
const btnCard = document.querySelector('#btn-view-card');
const btnList = document.querySelector('#btn-view-list');
let category = '全部';

function setView(mode) {
  if (!grid || !btnCard || !btnList) return;
  if (mode === 'list') {
    grid.classList.add('view-list');
    btnList.classList.add('active');
    btnList.setAttribute('aria-pressed', 'true');
    btnCard.classList.remove('active');
    btnCard.setAttribute('aria-pressed', 'false');
    try { localStorage.setItem('channel_view_mode', 'list'); } catch (e) {}
  } else {
    grid.classList.remove('view-list');
    btnCard.classList.add('active');
    btnCard.setAttribute('aria-pressed', 'true');
    btnList.classList.remove('active');
    btnList.setAttribute('aria-pressed', 'false');
    try { localStorage.setItem('channel_view_mode', 'card'); } catch (e) {}
  }
}

btnCard?.addEventListener('click', () => setView('card'));
btnList?.addEventListener('click', () => setView('list'));

try {
  const saved = localStorage.getItem('channel_view_mode');
  if (saved === 'list') setView('list');
} catch (e) {}

function update() {
  const q = input ? input.value.trim().toLocaleLowerCase() : '';
  let count = 0;
  for (const card of cards) {
    const match = (category === '全部' || card.dataset.category === category) && card.dataset.search.includes(q);
    card.hidden = !match;
    if (match) count++;
  }
  const countEl = document.querySelector('#count');
  if (countEl) countEl.textContent = `${count} 篇笔记`;
  const emptyEl = document.querySelector('#empty');
  if (emptyEl) emptyEl.hidden = count > 0;
}

input?.addEventListener('input', update);
filters.forEach(button => button.addEventListener('click', () => {
  category = button.dataset.filter;
  filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  update();
}));
