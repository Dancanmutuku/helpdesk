// IT HelpDesk — Main JS

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar mobile toggle ──────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay && overlay.classList.toggle('active');
    });
    overlay && overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }

  // ── Auto-dismiss alerts ────────────────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ── Tab system ─────────────────────────────────────────────
  document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', () => {
      const target = link.dataset.tab;
      const parent = link.closest('.tab-section');
      if (!parent) return;
      parent.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
      parent.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      link.classList.add('active');
      const content = parent.querySelector(`#tab-${target}`);
      if (content) content.classList.add('active');
    });
  });

  // ── Canned responses ──────────────────────────────────────
  const cannedBtn = document.getElementById('canned-btn');
  if (cannedBtn) {
    cannedBtn.addEventListener('click', async () => {
      const resp = await fetch('/tickets/api/canned-responses/');
      const data = await resp.json();
      const dropdown = document.getElementById('canned-dropdown');
      if (!dropdown) return;
      dropdown.innerHTML = '';
      data.responses.forEach(r => {
        const item = document.createElement('div');
        item.className = 'canned-item';
        item.textContent = r.title;
        item.style.cssText = 'padding:8px 14px;cursor:pointer;font-size:13px;border-bottom:1px solid var(--border);';
        item.addEventListener('click', () => {
          const body = document.getElementById('id_body') || document.querySelector('textarea[name=body]');
          if (body) body.value = r.body;
          dropdown.style.display = 'none';
        });
        item.addEventListener('mouseenter', () => item.style.background = 'var(--bg)');
        item.addEventListener('mouseleave', () => item.style.background = '');
        dropdown.appendChild(item);
      });
      dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    });
  }

  // ── SLA countdown timers ──────────────────────────────────
  document.querySelectorAll('[data-sla-due]').forEach(el => {
    const due = new Date(el.dataset.slaDue);
    const update = () => {
      const diff = due - new Date();
      if (diff <= 0) {
        el.textContent = 'OVERDUE';
        el.className = 'sla-overdue';
        return;
      }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      el.textContent = `${h}h ${m}m remaining`;
      el.className = diff < 3600000 * 2 ? 'sla-warning' : 'sla-ok';
    };
    update();
    setInterval(update, 60000);
  });

  // ── CSAT stars ───────────────────────────────────────────
  const csatStars = document.querySelectorAll('.csat-star');
  csatStars.forEach((star, idx) => {
    star.addEventListener('mouseenter', () => {
      csatStars.forEach((s, i) => s.classList.toggle('hovered', i <= idx));
    });
    star.addEventListener('mouseleave', () => {
      csatStars.forEach(s => s.classList.remove('hovered'));
    });
    star.addEventListener('click', () => {
      const val = star.dataset.val;
      const input = document.querySelector('input[name=csat_score]');
      if (input) input.value = val;
      csatStars.forEach((s, i) => s.classList.toggle('selected', i < val));
    });
  });

  // ── File input display ───────────────────────────────────
  document.querySelectorAll('input[type=file]').forEach(input => {
    input.addEventListener('change', () => {
      const label = input.nextElementSibling;
      if (label && label.classList.contains('file-label')) {
        label.textContent = Array.from(input.files).map(f => f.name).join(', ') || 'No file chosen';
      }
    });
  });

  // ── Confirm dialogs ───────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

});
