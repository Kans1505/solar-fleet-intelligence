/* ============ CONFIG ============ */
const API_BASE = 'https://solar-fleet-intelligence-1.onrender.com';
const API_KEY  = 'demo-key-tata-2026';

/* ============ NAVIGATION ============ */
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const section = item.dataset.section;

    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    item.classList.add('active');

    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(section).classList.add('active');

    const titles = {
      overview: 'Fleet Overview',
      predict:  'Efficiency Prediction',
      fleet:    'Fleet Health',
      cost:     'Cost Impact'
    };
    document.getElementById('page-title').textContent = titles[section];

    if (section === 'fleet') loadFleet();
    if (section === 'cost')  loadCost();
  });
});

/* ============ ANIMATED COUNTERS ============ */
function animateCounters() {
  document.querySelectorAll('.kpi-value [data-target], .kpi-value[data-target]').forEach(el => {
    const target   = parseFloat(el.dataset.target);
    const decimals = parseInt(el.dataset.decimals || '2');
    const duration = 1000;
    const start    = performance.now();

    function tick(now) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}

/* ============ SLIDERS ============ */
function bindSlider(id, formatter) {
  const input = document.getElementById(id);
  const out   = document.getElementById(id + '-val');
  const update = () => { out.textContent = formatter(input.value); };
  input.addEventListener('input', update);
  update();
}

bindSlider('hour',        v => `${String(v).padStart(2,'0')}:00`);
bindSlider('temperature', v => parseFloat(v).toFixed(1));
bindSlider('irradiance',  v => v);
bindSlider('dc_power',    v => v);
bindSlider('load_ratio',  v => parseFloat(v).toFixed(2));
bindSlider('eff_lag1',    v => parseFloat(v).toFixed(2));

/* ============ PREDICT ============ */
document.getElementById('predict-btn').addEventListener('click', async () => {
  const btn = document.getElementById('predict-btn');
  btn.textContent = 'Running…';
  btn.disabled = true;

  const payload = {
    hour:             parseInt(document.getElementById('hour').value),
    month:            6,
    is_monsoon:       0,
    temperature:      parseFloat(document.getElementById('temperature').value),
    temp_roll3:       parseFloat(document.getElementById('temperature').value),
    irradiance:       parseFloat(document.getElementById('irradiance').value),
    irr_roll3:        parseFloat(document.getElementById('irradiance').value),
    dc_power:         parseFloat(document.getElementById('dc_power').value),
    load_ratio:       parseFloat(document.getElementById('load_ratio').value),
    days_since_start: 180,
    eff_lag1:         parseFloat(document.getElementById('eff_lag1').value)
  };

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    document.getElementById('result-box').style.display = 'block';
    document.getElementById('result-value').textContent = `${data.predicted_efficiency_pct}%`;
    document.getElementById('result-status').textContent = data.status.toUpperCase();
  } catch (err) {
    document.getElementById('result-box').style.display = 'block';
    document.getElementById('result-value').textContent = '—';
    document.getElementById('result-status').textContent = `Error: ${err.message}`;
  } finally {
    btn.textContent = 'Run Prediction';
    btn.disabled = false;
  }
});

/* ============ FLEET HEALTH ============ */
async function loadFleet() {
  const wrap = document.getElementById('fleet-table');
  wrap.innerHTML = '<div class="empty">Loading fleet data…</div>';

  try {
    const res = await fetch(`${API_BASE}/fleet-health`, {
      headers: { 'X-API-Key': API_KEY }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const rows = json.data;

    let html = `<table><thead><tr>
      <th>Inverter</th><th>Anomalies</th><th>Total</th>
      <th>Avg Efficiency</th><th>Anomaly Rate</th>
    </tr></thead><tbody>`;

    rows.forEach(r => {
      const rate = r['anomaly_rate_%'];
      const sev  = rate > 2.5 ? 'sev-high' : rate > 2 ? 'sev-med' : 'sev-low';
      html += `<tr>
        <td>${r.inverter_id}</td>
        <td>${r.anomaly_count}</td>
        <td>${r.total}</td>
        <td>${r.avg_efficiency.toFixed(4)}</td>
        <td><span class="badge-sev ${sev}">${rate.toFixed(2)}%</span></td>
      </tr>`;
    });

    html += '</tbody></table>';
    wrap.innerHTML = html;
    document.getElementById('fleet-count').textContent = `${rows.length} inverters`;
  } catch (err) {
    wrap.innerHTML = `<div class="empty">Failed to load: ${err.message}</div>`;
  }
}

/* ============ COST IMPACT ============ */
async function loadCost() {
  const wrap = document.getElementById('cost-table');
  wrap.innerHTML = '<div class="empty">Loading cost data…</div>';

  try {
    const res = await fetch(`${API_BASE}/cost-impact`, {
      headers: { 'X-API-Key': API_KEY }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const rows = json.data.sort((a,b) => b.annual_loss_inr - a.annual_loss_inr);

    let html = `<table><thead><tr>
      <th>Inverter</th><th>Avg Efficiency</th><th>Energy Loss (kWh)</th>
      <th>Annual Loss (₹)</th>
    </tr></thead><tbody>`;

    let total = 0;
    rows.forEach(r => {
      total += r.annual_loss_inr;
      html += `<tr>
        <td>${r.inverter_id}</td>
        <td>${r.avg_efficiency.toFixed(4)}</td>
        <td>${Math.round(r.energy_loss_kwh).toLocaleString('en-IN')}</td>
        <td>₹${Math.round(r.annual_loss_inr).toLocaleString('en-IN')}</td>
      </tr>`;
    });

    html += `<tr style="background:#f1f5f9;">
      <td><strong>TOTAL</strong></td><td>—</td><td>—</td>
      <td><strong>₹${Math.round(total).toLocaleString('en-IN')}</strong></td>
    </tr></tbody></table>`;
    wrap.innerHTML = html;
  } catch (err) {
    wrap.innerHTML = `<div class="empty">Failed to load: ${err.message}</div>`;
  }
}

/* ============ CHARTS ============ */
let healthChart, costChart;

async function initCharts() {
  try {
    const [hRes, cRes] = await Promise.all([
      fetch(`${API_BASE}/fleet-health`, { headers: { 'X-API-Key': API_KEY } }),
      fetch(`${API_BASE}/cost-impact`,  { headers: { 'X-API-Key': API_KEY } })
    ]);
    const health = (await hRes.json()).data;
    const cost   = (await cRes.json()).data.sort((a,b) => b.annual_loss_inr - a.annual_loss_inr);

    const chartDefaults = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#ffffff',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          titleColor: '#0f172a',
          bodyColor: '#475569',
          padding: 10,
          titleFont: { family: 'Inter', size: 12, weight: '600' },
          bodyFont:  { family: 'IBM Plex Mono', size: 11 }
        }
      },
      scales: {
        x: {
          grid: { color: '#f1f5f9', drawBorder: false },
          ticks: { color: '#94a3b8', font: { family: 'IBM Plex Mono', size: 10 } }
        },
        y: {
          grid: { color: '#f1f5f9', drawBorder: false },
          ticks: { color: '#94a3b8', font: { family: 'IBM Plex Mono', size: 10 } }
        }
      }
    };

    healthChart = new Chart(document.getElementById('healthChart'), {
      type: 'bar',
      data: {
        labels: health.map(h => h.inverter_id.replace('INV-','')),
        datasets: [{
          data: health.map(h => h['anomaly_rate_%']),
          backgroundColor: health.map(h =>
            h['anomaly_rate_%'] > 2.5 ? 'rgba(239,68,68,0.85)' :
            h['anomaly_rate_%'] > 2.0 ? 'rgba(245,158,11,0.85)' :
                                        'rgba(37,99,235,0.75)'
          ),
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: { ...chartDefaults, plugins: { ...chartDefaults.plugins,
        tooltip: { ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => `${ctx.parsed.y.toFixed(2)}% anomaly rate` } } } }
    });

    costChart = new Chart(document.getElementById('costChart'), {
      type: 'bar',
      data: {
        labels: cost.map(c => c.inverter_id.replace('INV-','')),
        datasets: [{
          data: cost.map(c => Math.round(c.annual_loss_inr)),
          backgroundColor: cost.map((_, i) =>
            i < 3 ? 'rgba(239,68,68,0.85)' : 'rgba(37,99,235,0.65)'
          ),
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: { ...chartDefaults, plugins: { ...chartDefaults.plugins,
        tooltip: { ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => `₹${ctx.parsed.y.toLocaleString('en-IN')}` } } } }
    });
  } catch (err) {
    console.error('Chart init failed:', err);
  }
}

/* ============ REFRESH BUTTON ============ */
document.getElementById('refresh-btn').addEventListener('click', () => {
  const active = document.querySelector('.section.active').id;
  if (active === 'fleet') loadFleet();
  if (active === 'cost')  loadCost();
  if (active === 'overview') {
    healthChart?.destroy();
    costChart?.destroy();
    initCharts();
  }
});

/* ============ INIT ============ */
window.addEventListener('DOMContentLoaded', () => {
  animateCounters();
  initCharts();

  fetch(`${API_BASE}/`, { headers: { 'X-API-Key': API_KEY } })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(() => document.getElementById('api-status-text').textContent = 'API Online')
    .catch(() => {
      document.getElementById('api-status-text').textContent = 'API Offline';
      document.querySelector('.status-row .dot').style.background = 'var(--danger)';
    });
});