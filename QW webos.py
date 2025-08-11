import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

# -------------------- App Config --------------------
app = Flask(__name__)
APP_NAME = "Patient Records Management"
DATABASE_FILE = "patients.db"

# -------------------- Database Setup --------------------
def init_db():
    """Initialize the SQLite database and create the patients table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            docket_number TEXT,
            modality TEXT,
            procedure TEXT,
            phone_number TEXT,
            dob TEXT,
            coming_from TEXT,
            health_card TEXT,
            next_clinic_appointment TEXT
        )
    ''')
    conn.commit()
    conn.close()

# -------------------- HTML Template --------------------
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{ app_name }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
    --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    --success-gradient: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
    --danger-gradient: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    min-height: 100vh;
  }

  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }

  .glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    animation: slideInUp 0.6s ease-out;
  }

  .form-input-group { 
    position: relative; 
    margin-bottom: 1.5rem;
  }

  .form-input {
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    padding: 1rem 1rem 1rem 3rem;
    width: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    color: #1f2937;
    font-weight: 500;
  }

  .form-input:focus {
    outline: none;
    border-color: rgba(102, 126, 234, 0.6);
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
    transform: translateY(-2px);
  }

  .form-input::placeholder {
    color: rgba(75, 85, 99, 0.7);
  }

  .form-label {
    position: absolute;
    left: 3rem;
    top: 1rem;
    color: #4b5563;
    pointer-events: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(to right, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.8));
    padding: 0 0.5rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.875rem;
  }

  .form-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #667eea;
    font-size: 1.1rem;
    z-index: 10;
  }

  .form-input:focus + .form-icon {
    color: #4f46e5;
    animation: pulse 2s infinite;
  }

  .form-input:focus + .form-icon + .form-label,
  .form-input:not(:placeholder-shown) + .form-icon + .form-label,
  select.form-input:not([value=""]) + .form-icon + .form-label,
  input[type="date"].form-input:not(:placeholder-shown) + .form-icon + .form-label,
  input[type="datetime-local"].form-input:not(:placeholder-shown) + .form-icon + .form-label {
    top: -0.5rem;
    left: 2.5rem;
    font-size: 0.75rem;
    color: #667eea;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
  }

  .gradient-btn {
    background: var(--primary-gradient);
    border: none;
    border-radius: 15px;
    padding: 1rem 2rem;
    color: white;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
  }

  .gradient-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }

  .gradient-btn:active {
    transform: translateY(-1px);
  }

  .gradient-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }

  .gradient-btn:hover::before {
    left: 100%;
  }

  .success-btn {
    background: var(--success-gradient);
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
  }

  .success-btn:hover {
    box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
  }

  .danger-btn {
    background: var(--danger-gradient);
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
  }

  .danger-btn:hover {
    box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
  }

  .stats-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.8s ease-out;
  }

  .stats-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(31, 38, 135, 0.5);
  }

  .stats-number {
    font-size: 2.5rem;
    font-weight: 700;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    display: block;
  }

  .stats-label {
    color: #6b7280;
    font-weight: 500;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .modern-table {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    overflow: hidden;
  }

  .table-header {
    background: rgba(102, 126, 234, 0.1);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  .table-row {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .table-row:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.01);
  }

  .floating-action-btn {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--secondary-gradient);
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 8px 25px rgba(241, 147, 251, 0.4);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
  }

  .floating-action-btn:hover {
    transform: scale(1.1) rotate(180deg);
    box-shadow: 0 12px 35px rgba(241, 147, 251, 0.6);
  }

  .loading-spinner {
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top: 3px solid #667eea;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-right: 0.5rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .status-success {
    background: var(--success-gradient);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 500;
    animation: slideInUp 0.5s ease-out;
  }

  .status-error {
    background: var(--danger-gradient);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 500;
    animation: slideInUp 0.5s ease-out;
  }

  .header-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.5rem;
    animation: fadeIn 1s ease-out;
  }

  .header-subtitle {
    color: rgba(255, 255, 255, 0.9);
    text-align: center;
    font-weight: 400;
    animation: fadeIn 1.2s ease-out;
  }

  .clear-btn {
    background: none;
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: #6b7280;
    padding: 1rem 2rem;
    border-radius: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .clear-btn:hover {
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    .floating-action-btn {
      bottom: 1rem;
      right: 1rem;
      width: 50px;
      height: 50px;
      font-size: 1.2rem;
    }
    
    .glass-card {
      margin: 1rem;
      border-radius: 15px;
    }
    
    .form-input {
      padding: 0.875rem 0.875rem 0.875rem 2.5rem;
    }
    
    .form-label {
      left: 2.5rem;
    }
  }
</style>
</head>
<body onload="initializePage()">
  <div class="container mx-auto p-4 md:p-8 space-y-8 min-h-screen">
    <header class="text-center py-8">
      <h1 class="text-5xl font-bold header-title mb-4">
        <i class="fas fa-heartbeat mr-4"></i>{{ app_name }}
      </h1>
      <p class="header-subtitle text-lg">Modern healthcare management with style and efficiency</p>
    </header>

    <!-- Statistics Dashboard -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="stats-card">
        <i class="fas fa-users text-3xl text-blue-500 mb-3"></i>
        <span class="stats-number" id="totalPatients">0</span>
        <div class="stats-label">Total Patients</div>
      </div>
      <div class="stats-card">
        <i class="fas fa-calendar-plus text-3xl text-green-500 mb-3"></i>
        <span class="stats-number" id="todayAppointments">0</span>
        <div class="stats-label">Today's Appointments</div>
      </div>
      <div class="stats-card">
        <i class="fas fa-clock text-3xl text-yellow-500 mb-3"></i>
        <span class="stats-number" id="upcomingAppointments">0</span>
        <div class="stats-label">Upcoming</div>
      </div>
      <div class="stats-card">
        <i class="fas fa-chart-line text-3xl text-purple-500 mb-3"></i>
        <span class="stats-number" id="monthlyGrowth">+0%</span>
        <div class="stats-label">Monthly Growth</div>
      </div>
    </div>

    <div class="glass-card p-8">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-user-plus mr-3 text-indigo-600"></i>Patient Management
        </h2>
        <button class="gradient-btn" onclick="exportPatientData()">
          <i class="fas fa-download mr-2"></i>Export Data
        </button>
      </div>
      <form id="patientForm" onsubmit="handlePatientSubmit(event)" class="space-y-6">
        <input type="hidden" id="patientId" name="patientId">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="form-input-group">
            <input class="form-input" type="text" id="patient_name" placeholder="Enter patient name" required>
            <i class="form-icon fas fa-user"></i>
            <label class="form-label" for="patient_name">Patient Name</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="docket_number" placeholder="Enter docket number">
            <i class="form-icon fas fa-file-medical"></i>
            <label class="form-label" for="docket_number">Docket Number</label>
          </div>
          <div class="form-input-group">
            <select id="modality" class="form-input" onchange="this.setAttribute('value', this.value)">
              <option value="" selected>Select Modality...</option>
              <option value="US">US</option>
              <option value="CT">CT</option>
              <option value="DX/CR">DX/CR</option>
              <option value="MAMMO">MAMMO</option>
            </select>
            <i class="form-icon fas fa-x-ray"></i>
            <label class="form-label" for="modality">Modality</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="procedure" placeholder="Enter procedure">
            <i class="form-icon fas fa-procedures"></i>
            <label class="form-label" for="procedure">Procedure</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="tel" id="phone_number" placeholder="Enter phone number">
            <i class="form-icon fas fa-phone"></i>
            <label class="form-label" for="phone_number">Phone Number</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="date" id="dob" placeholder=" ">
            <i class="form-icon fas fa-birthday-cake"></i>
            <label class="form-label" for="dob">Date of Birth</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="coming_from" placeholder="Enter source">
            <i class="form-icon fas fa-map-marker-alt"></i>
            <label class="form-label" for="coming_from">Source</label>
          </div>
          <div class="form-input-group">
            <select id="health_card" class="form-input" onchange="this.setAttribute('value', this.value)">
              <option value="">Select Health Card</option>
              <option>Sagicor</option>
              <option>Canopy</option>
              <option>Guardian Life</option>
              <option>Other</option>
            </select>
            <i class="form-icon fas fa-id-card"></i>
             <label class="form-label" for="health_card">Health Card</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="datetime-local" id="next_clinic_appointment" placeholder=" ">
            <i class="form-icon fas fa-calendar-alt"></i>
            <label class="form-label" for="next_clinic_appointment">Next Appointment</label>
          </div>
        </div>
        <div class="flex items-center flex-wrap gap-4 pt-6">
          <button id="patientSubmitBtn" type="submit" class="gradient-btn">
            <i class="fas fa-plus mr-2"></i>Add Patient
          </button>
          <button type="button" class="clear-btn" onclick="resetPatientForm()">
            <i class="fas fa-times mr-2"></i>Clear Form
          </button>
        </div>
      </form>
      <div id="patientStatus" class="text-sm mt-6 font-medium"></div>
      
      <div class="flex items-center justify-between mt-12 mb-6">
        <h3 class="text-2xl font-bold text-gray-800">
          <i class="fas fa-list mr-3 text-indigo-600"></i>Patient Records
        </h3>
        <div class="flex gap-3">
          <button class="gradient-btn" onclick="refreshPatients()">
            <i class="fas fa-sync-alt mr-2"></i>Refresh
          </button>
          <button class="gradient-btn success-btn" onclick="addNewPatient()">
            <i class="fas fa-user-plus mr-2"></i>Quick Add
          </button>
        </div>
      </div>
      <div class="modern-table">
        <table class="min-w-full text-sm">
          <thead class="table-header"><tr id="patient-table-header"></tr></thead>
          <tbody id="patientTbody" class="divide-y">
            <tr><td class="p-6 text-center text-gray-500" colspan="11">
              <div class="loading-spinner"></div>Loading patients...
            </td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Floating Action Button -->
    <button class="floating-action-btn" onclick="scrollToTop()" title="Scroll to top">
      <i class="fas fa-chevron-up"></i>
    </button>
  </div>

<script>
// -------------------- State --------------------
const patientFormFields = ['patient_name', 'docket_number', 'modality', 'procedure', 'phone_number', 'dob', 'coming_from', 'health_card', 'next_clinic_appointment'];

// -------------------- Enhanced Patient Management JS --------------------
async function loadPatients() {
  showLoadingState();
  try {
    const resp = await fetch('/api/patients');
    if (!resp.ok) throw new Error(`Server error: ${resp.statusText}`);
    const patients = await resp.json();
    const tbody = document.getElementById('patientTbody');
    const header = document.getElementById('patient-table-header');
    tbody.innerHTML = "";
    
    // Update statistics
    updateStatistics(patients);
    
    if (!patients.length) {
      tbody.innerHTML = `<tr><td class="p-6 text-center text-gray-500" colspan="10">
        <i class="fas fa-users text-4xl mb-4 opacity-50"></i><br>
        No patients found. Add your first patient using the form above.
      </td></tr>`;
      header.innerHTML = '';
      return;
    }

    const headers = ['Name', 'Docket', 'Modality', 'Procedure', 'Phone', 'DOB', 'Source', 'Health Card', 'Next Apt.', 'Actions'];
    header.innerHTML = headers.map(h => `<th class="p-4 font-semibold text-left text-gray-700">${h}</th>`).join('');

    patients.forEach((p, index) => {
      const tr = document.createElement('tr');
      tr.className = 'table-row';
      tr.style.animationDelay = `${index * 0.1}s`;
      tr.innerHTML = `
        <td class="p-4 whitespace-nowrap font-medium text-gray-800">
          <i class="fas fa-user-circle mr-2 text-indigo-500"></i>${escapeHtml(p.patient_name)}
        </td>
        <td class="p-4 whitespace-nowrap text-gray-600">${escapeHtml(p.docket_number)}</td>
        <td class="p-4 whitespace-nowrap">
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
            ${escapeHtml(p.modality)}
          </span>
        </td>
        <td class="p-4 whitespace-nowrap text-gray-600">${escapeHtml(p.procedure)}</td>
        <td class="p-4 whitespace-nowrap text-gray-600">
          <i class="fas fa-phone mr-1 text-green-500"></i>${escapeHtml(p.phone_number)}
        </td>
        <td class="p-4 whitespace-nowrap text-gray-600">${escapeHtml(p.dob)}</td>
        <td class="p-4 whitespace-nowrap text-gray-600">${escapeHtml(p.coming_from)}</td>
        <td class="p-4 whitespace-nowrap">
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
            ${escapeHtml(p.health_card)}
          </span>
        </td>
        <td class="p-4 whitespace-nowrap text-gray-600">
          ${p.next_clinic_appointment ? `<i class="fas fa-calendar mr-1 text-yellow-500"></i>${new Date(p.next_clinic_appointment).toLocaleString([], {year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'})}` : '<span class="text-gray-400">Not scheduled</span>'}
        </td>
        <td class="p-4 flex items-center gap-2">
          <button class="gradient-btn success-btn text-xs px-3 py-1" onclick="editPatient(${p.id})" title="Edit Patient">
            <i class="fas fa-edit"></i>
          </button>
          <button class="gradient-btn danger-btn text-xs px-3 py-1" onclick="deletePatient(${p.id})" title="Delete Patient">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch(err) {
    console.error("Failed to load patients:", err);
    showStatus("Error: Could not load patient list.", 'error');
  }
}

function updateStatistics(patients) {
  const total = patients.length;
  const today = new Date().toDateString();
  const todayAppointments = patients.filter(p => 
    p.next_clinic_appointment && new Date(p.next_clinic_appointment).toDateString() === today
  ).length;
  
  const upcoming = patients.filter(p => 
    p.next_clinic_appointment && new Date(p.next_clinic_appointment) > new Date()
  ).length;
  
  // Animate number changes
  animateNumber('totalPatients', total);
  animateNumber('todayAppointments', todayAppointments);
  animateNumber('upcomingAppointments', upcoming);
  
  // Calculate growth (mock calculation for demo)
  const growth = total > 0 ? Math.floor(Math.random() * 20) + 5 : 0;
  document.getElementById('monthlyGrowth').textContent = `+${growth}%`;
}

function animateNumber(elementId, targetNumber) {
  const element = document.getElementById(elementId);
  const startNumber = parseInt(element.textContent) || 0;
  const duration = 1000;
  const stepTime = 50;
  const steps = duration / stepTime;
  const increment = (targetNumber - startNumber) / steps;
  
  let currentNumber = startNumber;
  const timer = setInterval(() => {
    currentNumber += increment;
    if (increment > 0 ? currentNumber >= targetNumber : currentNumber <= targetNumber) {
      currentNumber = targetNumber;
      clearInterval(timer);
    }
    element.textContent = Math.round(currentNumber);
  }, stepTime);
}

function showLoadingState() {
  const tbody = document.getElementById('patientTbody');
  tbody.innerHTML = `<tr><td class="p-6 text-center text-gray-500" colspan="11">
    <div class="loading-spinner"></div>Loading patients...
  </td></tr>`;
}

function showStatus(message, type = 'success') {
  const statusEl = document.getElementById('patientStatus');
  statusEl.textContent = message;
  statusEl.className = `text-sm font-medium mt-6 ${type === 'success' ? 'status-success' : 'status-error'}`;
  
  setTimeout(() => {
    statusEl.textContent = "";
    statusEl.className = 'text-sm mt-6 font-medium';
  }, 4000);
}

function getPatientFormData() {
    const data = {};
    patientFormFields.forEach(field => {
        data[field] = document.getElementById(field).value;
    });
    return data;
}

async function handlePatientSubmit(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('patientSubmitBtn');
  const originalText = submitBtn.innerHTML;
  
  // Show loading state
  submitBtn.innerHTML = '<div class="loading-spinner"></div>Processing...';
  submitBtn.disabled = true;
  
  try {
    const patientId = document.getElementById('patientId').value;
    const url = patientId ? `/api/patient/${patientId}` : '/api/patient';
    const method = patientId ? 'PUT' : 'POST';
    
    const formData = getPatientFormData();
    
    const resp = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    const result = await resp.json();
    
    if (resp.ok) {
      resetPatientForm();
      loadPatients();
      showStatus(result.message, 'success');
    } else {
      showStatus(result.message, 'error');
    }
  } catch (error) {
    showStatus('An error occurred while processing your request.', 'error');
  } finally {
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
  }
}

function resetPatientForm() {
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
    document.getElementById('patientSubmitBtn').innerHTML = '<i class="fas fa-plus mr-2"></i>Add Patient';
    // Manually trigger the onchange for selects to reset their value attribute for styling
    document.getElementById('modality').setAttribute('value', '');
    document.getElementById('health_card').setAttribute('value', '');
}

async function editPatient(id) {
    const resp = await fetch(`/api/patient/${id}`);
    if (!resp.ok) { 
      showStatus('Failed to fetch patient data.', 'error');
      return; 
    }
    const patient = await resp.json();
    
    patientFormFields.forEach(field => {
        const el = document.getElementById(field);
        if (el) {
            el.value = patient[field] || '';
            if(el.tagName === 'SELECT') {
                el.setAttribute('value', patient[field] || '');
            }
        }
    });
    document.getElementById('patientId').value = patient.id;
    document.getElementById('patientSubmitBtn').innerHTML = '<i class="fas fa-save mr-2"></i>Update Patient';
    
    // Smooth scroll to form
    document.querySelector('#patientForm').scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    });
}

async function deletePatient(id) {
  // Create a custom modal-style confirmation
  if (!await customConfirm('Are you sure you want to delete this patient record?', 'This action cannot be undone.')) {
    return;
  }
  
  const resp = await fetch(`/api/patient/${id}`, { method: 'DELETE' });
  const result = await resp.json();
  
  if (resp.ok) {
    loadPatients();
    showStatus(result.message, 'success');
  } else {
    showStatus(result.message, 'error');
  }
}

function customConfirm(title, message) {
  return new Promise((resolve) => {
    const confirmed = confirm(`${title}\n\n${message}`);
    resolve(confirmed);
  });
}

// -------------------- New Enhanced Functions --------------------
function exportPatientData() {
  fetch('/api/patients')
    .then(response => response.json())
    .then(patients => {
      const csvContent = generateCSV(patients);
      downloadCSV(csvContent, 'patient_records.csv');
      showStatus('Patient data exported successfully!', 'success');
    })
    .catch(error => {
      showStatus('Failed to export patient data.', 'error');
    });
}

function generateCSV(patients) {
  const headers = ['Name', 'Docket Number', 'Modality', 'Procedure', 'Phone', 'DOB', 'Source', 'Health Card', 'Next Appointment'];
  const csvRows = [headers.join(',')];
  
  patients.forEach(patient => {
    const row = [
      `"${patient.patient_name || ''}"`,
      `"${patient.docket_number || ''}"`,
      `"${patient.modality || ''}"`,
      `"${patient.procedure || ''}"`,
      `"${patient.phone_number || ''}"`,
      `"${patient.dob || ''}"`,
      `"${patient.coming_from || ''}"`,
      `"${patient.health_card || ''}"`,
      `"${patient.next_clinic_appointment || ''}"`
    ];
    csvRows.push(row.join(','));
  });
  
  return csvRows.join('\n');
}

function downloadCSV(csvContent, filename) {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function refreshPatients() {
  showStatus('Refreshing patient data...', 'success');
  loadPatients();
}

function addNewPatient() {
  resetPatientForm();
  document.querySelector('#patientForm').scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start' 
  });
  document.getElementById('patient_name').focus();
}

function scrollToTop() {
  window.scrollTo({ 
    top: 0, 
    behavior: 'smooth' 
  });
}

function escapeHtml(s){
  if (s === null || s === undefined) return '';
  return s.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

// -------------------- Enhanced Form Interactions --------------------
function initializePage() {
  loadPatients();
  
  // Add smooth focus transitions to form inputs
  const inputs = document.querySelectorAll('.form-input');
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.style.transform = 'translateY(-2px)';
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.style.transform = 'translateY(0)';
    });
  });
  
  // Add keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      document.getElementById('patientForm').dispatchEvent(new Event('submit'));
    }
    if (e.ctrlKey && e.key === 'r') {
      e.preventDefault();
      refreshPatients();
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.readyState === 'loading') {
    // Document hasn't finished loading yet
  } else {
    // Document already loaded
    initializePage();
  }
});
</script>
</body>
</html>
"""

# -------------------- API & Web Routes --------------------

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, app_name=APP_NAME)

# --- Patient API Routes ---
@app.route("/api/patients", methods=['GET'])
def get_patients():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY patient_name")
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(patients)

@app.route("/api/patient/<int:patient_id>", methods=['GET'])
def get_patient(patient_id):
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    if patient is None:
        return jsonify({"message": "Patient not found"}), 404
    return jsonify(dict(patient))

@app.route("/api/patient", methods=['POST'])
def add_patient():
    data = request.json
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patients (patient_name, docket_number, modality, procedure, phone_number, dob, coming_from, health_card, next_clinic_appointment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('patient_name'), data.get('docket_number'), data.get('modality'), data.get('procedure'),
            data.get('phone_number'), data.get('dob'), data.get('coming_from'), data.get('health_card'),
            data.get('next_clinic_appointment')
        ))
        conn.commit()
        return jsonify({"message": "Patient added successfully!"}), 201
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route("/api/patient/<int:patient_id>", methods=['PUT'])
def update_patient(patient_id):
    data = request.json
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE patients SET
            patient_name = ?, docket_number = ?, modality = ?, procedure = ?, phone_number = ?,
            dob = ?, coming_from = ?, health_card = ?, next_clinic_appointment = ?
            WHERE id = ?
        """, (
            data.get('patient_name'), data.get('docket_number'), data.get('modality'), data.get('procedure'),
            data.get('phone_number'), data.get('dob'), data.get('coming_from'), data.get('health_card'),
            data.get('next_clinic_appointment'), patient_id
        ))
        conn.commit()
        if cursor.rowcount == 0:
             return jsonify({"message": "Patient not found"}), 404
        return jsonify({"message": "Patient updated successfully!"})
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route("/api/patient/<int:patient_id>", methods=['DELETE'])
def delete_patient(patient_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        if cursor.rowcount == 0:
             return jsonify({"message": "Patient not found"}), 404
        return jsonify({"message": "Patient deleted successfully."})
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

# -------------------- Main --------------------
if __name__ == "__main__":
    init_db()  # Ensure the database is ready
    app.run(debug=True, host='0.0.0.0', port=5000)