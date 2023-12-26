from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

conn = sqlite3.connect('archospital.db')
cursor = conn.cursor()
assigned_doctors = set()
assigned_patients = set()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR,
        specialty VARCHAR
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR,
        medical_history TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY,
        doctor_id INTEGER,
        patient_id INTEGER,
        scheduled_time TIMESTAMP,
        status VARCHAR,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        details TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
''')

conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctors')
def doctors():
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctors')
    doctors_data = cursor.fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors_data)

@app.route('/patients')
def patients():
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients')
    patients_data = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients_data)

@app.route('/appointments')
def appointments():
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT appointments.id, doctors.name AS doctor_name, patients.name AS patient_name, 
        scheduled_time, status
        FROM appointments
        JOIN doctors ON appointments.doctor_id = doctors.id
        JOIN patients ON appointments.patient_id = patients.id
    ''')
    appointments_data = cursor.fetchall()

    cursor.execute('SELECT * FROM doctors')
    doctors_data = cursor.fetchall()

    cursor.execute('SELECT * FROM patients')
    patients_data = cursor.fetchall()

    conn.close()
    return render_template('appointments.html', appointments=appointments_data, doctors=doctors_data, patients=patients_data)

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['doctor_name']
        email = request.form['doctor_email']
        specialty = request.form['doctor_specialty']
        
        conn = sqlite3.connect('archospital.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO doctors (name, email, specialty) VALUES (?, ?, ?)', (name, email, specialty))
        conn.commit()
        conn.close()
    
    return redirect(url_for('doctors'))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['patient_name']
        email = request.form['patient_email']
        medical_history = request.form['patient_medical_history']
        
        conn = sqlite3.connect('archospital.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO patients (name, email, medical_history) VALUES (?, ?, ?)', (name, email, medical_history))
        conn.commit()
        conn.close()
    
    return redirect(url_for('patients'))

@app.route('/assign_appointment', methods=['POST'])
def assign_appointment():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        patient_id = request.form['patient_id']
        scheduled_time = request.form['scheduled_time']
        status = 'Scheduled'
        
        conn = sqlite3.connect('archospital.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO appointments (doctor_id, patient_id, scheduled_time, status) VALUES (?, ?, ?, ?)', 
                       (doctor_id, patient_id, scheduled_time, status))
        conn.commit()
        conn.close()

    return redirect(url_for('appointments'))

@app.route('/delete_doctor/<int:id>', methods=['POST'])
def delete_doctor(id):
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM doctors WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('doctors'))

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM patients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patients'))

@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM appointments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('appointments'))

@app.route('/auto_assign', methods=['POST'])
def auto_assign():
    global assigned_doctors
    global assigned_patients

    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, specialty FROM doctors')
    doctors = cursor.fetchall()
    cursor.execute('SELECT id, medical_history FROM patients')
    patients = cursor.fetchall()
    conn.close()

    assigned_appointments = []

    random.shuffle(doctors)
    random.shuffle(patients)

    for patient in patients:
        if patient[0] not in assigned_patients:
            for doctor in doctors:
                if doctor[0] not in assigned_doctors and doctor[1].lower() in patient[1].lower():
                    assigned_appointments.append((doctor[0], patient[0]))
                    assigned_doctors.add(doctor[0])
                    assigned_patients.add(patient[0])
                    break

    conn = sqlite3.connect('archospital.db')
    cursor = conn.cursor()
    for appointment in assigned_appointments:
        scheduled_time = "2024-01-01 12:00:00"
        status = "Auto-Assigned"
        cursor.execute('INSERT INTO appointments (doctor_id, patient_id, scheduled_time, status) VALUES (?, ?, ?, ?)',
                       (appointment[0], appointment[1], scheduled_time, status))
    conn.commit()
    conn.close()

    return redirect(url_for('appointments'))

if __name__ == '__main__':
    app.run(debug=True)