// ===================== Auth Modal (unchanged behavior) =====================
let currentMode = 'login';

function openModal(mode) {
  currentMode = mode;
  const modal = document.getElementById('authModal');
  const title = document.getElementById('modalTitle');
  const submitBtn = document.getElementById('submitAuthBtn');

  title.innerText = mode === 'login' ? 'Log In' : 'Sign Up';
  submitBtn.innerText = mode === 'login' ? 'Log In' : 'Create Account';

  modal.style.display = 'block';
}

function closeModal() {
  document.getElementById('authModal').style.display = 'none';
}

function handleAuth(event) {
  event.preventDefault();
  alert(`${currentMode === 'login' ? 'Logged in' : 'Signed up'} successfully!`);
  closeModal();
}

window.onclick = function (event) {
  const modal = document.getElementById('authModal');
  if (event.target === modal) {
    closeModal();
  }
};

// ===================== State list (shared across views) =====================
const STATES = [
  "Andhra Pradesh", "Uttar Pradesh", "Maharashtra", "Bihar", "Tamil Nadu",
  "Rajasthan", "West Bengal", "Karnataka", "Punjab", "Gujarat",
];

function populateStateSelects() {
  const selects = [document.getElementById('diagnoseState'), document.getElementById('recommendState')];
  selects.forEach(sel => {
    STATES.forEach(state => {
      const opt = document.createElement('option');
      opt.value = state;
      opt.textContent = state;
      sel.appendChild(opt);
    });
  });
}

// ===================== View switching =====================
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');

  document.querySelectorAll('.view-link').forEach(l => l.classList.remove('active'));
  const navMap = { diagnose: 'navDiagnose', recommend: 'navRecommend', dashboard: 'navDashboard' };
  document.getElementById(navMap[name]).classList.add('active');

  if (name === 'dashboard') loadDashboard();
}

// ===================== Backend config =====================
const API_BASE_URL = "http://localhost:5000";

// ===================== Diagnose crop =====================
function previewImage() {
  const input = document.getElementById('imageUpload');
  const preview = document.getElementById('imagePreview');
  if (input.files && input.files[0]) {
    preview.src = URL.createObjectURL(input.files[0]);
    preview.style.display = 'block';
  }
}

async function submitDiagnosis() {
  const fileInput = document.getElementById('imageUpload');
  const state = document.getElementById('diagnoseState').value;
  const resultDiv = document.getElementById('diagnoseResult');
  const btn = document.getElementById('diagnoseBtn');

  if (!fileInput.files || !fileInput.files[0]) {
    resultDiv.innerHTML = `<div class="result-card error">Please upload a crop photo first.</div>`;
    return;
  }

  btn.disabled = true;
  btn.innerText = 'Analyzing with AI...';
  resultDiv.innerHTML = `<div class="result-card loading">Analyzing your crop photo...</div>`;

  const formData = new FormData();
  formData.append('image', fileInput.files[0]);
  formData.append('state', state);

  try {
    const response = await fetch(`${API_BASE_URL}/api/diagnose`, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<div class="result-card error">Error: ${data.error}</div>`;
    } else {
      resultDiv.innerHTML = `
        <div class="result-card success">
          <strong>${data.diagnosis}</strong>
          <span class="tag priority-${data.confidence.toLowerCase() === 'high' ? 'high' : data.confidence.toLowerCase() === 'low' ? 'low' : 'medium'}">${data.confidence} Confidence</span>
          <p>${data.explanation}</p>
          <p><strong>Recommended regenerative actions:</strong> ${data.regenerative_actions}</p>
        </div>
      `;
    }
  } catch (err) {
    resultDiv.innerHTML = `<div class="result-card error">Could not reach the server. Make sure server.py is running.<br><small>${err}</small></div>`;
  }

  btn.disabled = false;
  btn.innerText = 'Diagnose Crop';
}

// ===================== Get recommendation =====================
async function submitRecommendation() {
  const state = document.getElementById('recommendState').value;
  const soilType = document.getElementById('soilType').value;
  const season = document.getElementById('seasonSelect').value;
  const resultDiv = document.getElementById('recommendResult');
  const btn = document.getElementById('recommendBtn');

  btn.disabled = true;
  btn.innerText = 'Generating recommendation...';
  resultDiv.innerHTML = `<div class="result-card loading">Analyzing regional context...</div>`;

  try {
    const response = await fetch(`${API_BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state, soil_type: soilType, season }),
    });
    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<div class="result-card error">Error: ${data.error}</div>`;
    } else {
      resultDiv.innerHTML = `
        <div class="result-card success">
          <strong>Recommended crops:</strong> ${data.recommended_crops}
          <p><strong>Regenerative practices:</strong> ${data.regenerative_practices}</p>
          <p><strong>Climate note:</strong> ${data.climate_note}</p>
        </div>
      `;
    }
  } catch (err) {
    resultDiv.innerHTML = `<div class="result-card error">Could not reach the server. Make sure server.py is running.<br><small>${err}</small></div>`;
  }

  btn.disabled = false;
  btn.innerText = 'Get Recommendation';
}

// ===================== State cooperation dashboard =====================
async function loadDashboard() {
  const metricsDiv = document.getElementById('dashboardMetrics');
  const issuesDiv = document.getElementById('commonIssues');
  const diagStateDiv = document.getElementById('diagnosesByState');
  const recStateDiv = document.getElementById('recsByState');

  metricsDiv.innerHTML = `<div class="metric-card">Loading...</div>`;

  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard`);
    const data = await response.json();

    metricsDiv.innerHTML = `
      <div class="metric-card">
        <span class="metric-label">Total Diagnoses</span>
        <span class="metric-value">${data.total_diagnoses}</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">Total Recommendations</span>
        <span class="metric-value">${data.total_recommendations}</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">States Participating</span>
        <span class="metric-value">${data.states_participating}</span>
      </div>
    `;

    issuesDiv.innerHTML = data.common_issues.length
      ? data.common_issues.map(([issue, count]) => `<div class="breakdown-row"><span>${issue}</span><span>${count}</span></div>`).join('')
      : '<p>No diagnoses submitted yet.</p>';

    diagStateDiv.innerHTML = Object.keys(data.diagnoses_by_state).length
      ? Object.entries(data.diagnoses_by_state).sort((a, b) => b[1] - a[1])
          .map(([state, count]) => `<div class="breakdown-row"><span>${state}</span><span>${count}</span></div>`).join('')
      : '<p>No data yet.</p>';

    recStateDiv.innerHTML = Object.keys(data.recommendations_by_state).length
      ? Object.entries(data.recommendations_by_state).sort((a, b) => b[1] - a[1])
          .map(([state, count]) => `<div class="breakdown-row"><span>${state}</span><span>${count}</span></div>`).join('')
      : '<p>No data yet.</p>';

  } catch (err) {
    metricsDiv.innerHTML = `<div class="metric-card error">Could not reach the server. Make sure server.py is running.</div>`;
  }
}

// ===================== Init =====================
populateStateSelects();
