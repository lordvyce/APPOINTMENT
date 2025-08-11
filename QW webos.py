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
<style>
  .form-input-group { position: relative; }
  .form-input {
    border: 1px solid #D1D5DB; border-radius: 0.5rem;
    padding: 0.75rem 1rem; width: 100%; transition: border-color 0.2s;
    background-color: white; /* Ensure bg is white for label to cover */
  }
  .form-label {
    position: absolute; left: 1rem; top: 0.75rem; color: #6B7280;
    pointer-events: none; transition: all 0.2s ease-out;
    background-color: white; padding: 0 0.25rem;
  }
  /* Adjust label for select and date inputs */
  select.form-input:not([value=""]) + .form-label,
  input[type="date"].form-input:not(:placeholder-shown) + .form-label {
    top: -0.5rem; left: 0.75rem; font-size: 0.75rem; color: #4F46E5;
  }
  .form-input:focus + .form-label,
  .form-input:not(:placeholder-shown) + .form-label {
    top: -0.5rem; left: 0.75rem; font-size: 0.75rem; color: #4F46E5;
  }
</style>
</head>
<body class="bg-gray-100 text-gray-800" onload="loadPatients()">
  <div class="container mx-auto p-4 md:p-8 space-y-8">
    <header class="text-center">
      <h1 class="text-4xl font-bold text-gray-900">{{ app_name }}</h1>
      <p class="text-gray-500 mt-2">A simple solution for patient record management.</p>
    </header>

    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-semibold mb-6">Patient Management</h2>
      <form id="patientForm" onsubmit="handlePatientSubmit(event)" class="space-y-6">
        <input type="hidden" id="patientId" name="patientId">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="form-input-group">
            <input class="form-input" type="text" id="patient_name" placeholder=" " required>
            <label class="form-label" for="patient_name">Patient Name</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="docket_number" placeholder=" ">
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
            <label class="form-label" for="modality">Modality</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="procedure" placeholder=" ">
            <label class="form-label" for="procedure">Procedure</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="tel" id="phone_number" placeholder=" ">
            <label class="form-label" for="phone_number">Phone Number</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="date" id="dob" placeholder=" ">
            <label class="form-label" for="dob">Date of Birth</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="text" id="coming_from" placeholder=" ">
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
             <label class="form-label" for="health_card">Health Card</label>
          </div>
          <div class="form-input-group">
            <input class="form-input" type="datetime-local" id="next_clinic_appointment" placeholder=" ">
            <label class="form-label" for="next_clinic_appointment">Next Appointment</label>
          </div>
        </div>
        <div class="flex items-center flex-wrap gap-4 pt-4">
          <button id="patientSubmitBtn" type="submit" class="bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Add Patient</button>
          <button type="button" class="text-gray-600 hover:text-gray-900" onclick="resetPatientForm()">Clear Form</button>
        </div>
      </form>
      <div id="patientStatus" class="text-sm mt-4 font-medium"></div>
      
      <h3 class="text-xl font-semibold mt-10 mb-4">Current Patients</h3>
      <div class="overflow-x-auto border rounded-lg">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50 text-left"><tr id="patient-table-header"></tr></thead>
          <tbody id="patientTbody" class="divide-y bg-white">
            <tr><td class="p-4 text-center text-gray-500" colspan="11">Loading patients...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

<script>
// -------------------- State --------------------
const patientFormFields = ['patient_name', 'docket_number', 'modality', 'procedure', 'phone_number', 'dob', 'coming_from', 'health_card', 'next_clinic_appointment'];

// -------------------- Patient Management JS --------------------
async function loadPatients() {
  try {
    const resp = await fetch('/api/patients');
    if (!resp.ok) throw new Error(`Server error: ${resp.statusText}`);
    const patients = await resp.json();
    const tbody = document.getElementById('patientTbody');
    const header = document.getElementById('patient-table-header');
    tbody.innerHTML = "";
    
    if (!patients.length) {
      tbody.innerHTML = `<tr><td class="p-4 text-center text-gray-500" colspan="10">No patients found. Add one using the form above.</td></tr>`;
      header.innerHTML = '';
      return;
    }

    const headers = ['Name', 'Docket', 'Modality', 'Procedure', 'Phone', 'DOB', 'Source', 'Health Card', 'Next Apt.', 'Actions'];
    header.innerHTML = headers.map(h => `<th class="p-3 font-semibold text-left">${h}</th>`).join('');

    patients.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.patient_name)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.docket_number)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.modality)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.procedure)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.phone_number)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.dob)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.coming_from)}</td>
        <td class="p-3 whitespace-nowrap">${escapeHtml(p.health_card)}</td>
        <td class="p-3 whitespace-nowrap">${p.next_clinic_appointment ? new Date(p.next_clinic_appointment).toLocaleString([], {year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}) : ''}</td>
        <td class="p-3 flex items-center gap-2">
          <button class="text-sm bg-blue-100 text-blue-800 font-semibold py-1 px-3 rounded-lg hover:bg-blue-200" onclick="editPatient(${p.id})">Edit</button>
          <button class="text-sm bg-red-100 text-red-800 font-semibold py-1 px-3 rounded-lg hover:bg-red-200" onclick="deletePatient(${p.id})">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch(err) {
    console.error("Failed to load patients:", err);
    document.getElementById('patientStatus').textContent = "Error: Could not load patient list.";
  }
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
  const statusEl = document.getElementById('patientStatus');
  statusEl.textContent = result.message;
  
  if (resp.ok) {
    resetPatientForm();
    loadPatients();
    statusEl.className = 'text-sm font-medium text-green-600 mt-3';
  } else {
    statusEl.className = 'text-sm font-medium text-red-600 mt-3';
  }
  setTimeout(() => statusEl.textContent = "", 4000);
}

function resetPatientForm() {
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
    document.getElementById('patientSubmitBtn').textContent = 'Add Patient';
    // Manually trigger the onchange for selects to reset their value attribute for styling
    document.getElementById('modality').setAttribute('value', '');
    document.getElementById('health_card').setAttribute('value', '');
}

async function editPatient(id) {
    const resp = await fetch(`/api/patient/${id}`);
    if (!resp.ok) { alert('Failed to fetch patient data.'); return; }
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
    document.getElementById('patientSubmitBtn').textContent = 'Update Patient';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deletePatient(id) {
  if (!confirm('Are you sure you want to delete this patient record?')) return;
  
  const resp = await fetch(`/api/patient/${id}`, { method: 'DELETE' });
  const result = await resp.json();
  alert(result.message);
  if (resp.ok) {
    loadPatients();
  }
}

function escapeHtml(s){
  if (s === null || s === undefined) return '';
  return s.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}
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