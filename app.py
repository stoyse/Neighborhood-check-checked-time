from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
import sqlite3
import json
import random
from datetime import datetime
from db_handler import DB_PATH
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging
from pytz import timezone

app = Flask(__name__)

# Logging für den Scheduler konfigurieren
logging.basicConfig(level=logging.INFO)

# min-Funktion für Jinja2-Templates verfügbar machen
app.jinja_env.globals.update(min=min)

def run_neighborhood_check():
    """Führt den Neighborhood Check aus"""
    try:
        print(f"[{datetime.now()}] Automatischer Neighborhood Check gestartet...")
        
        # Importiere und führe main aus
        from main import main
        main()
        
        print(f"[{datetime.now()}] Automatischer Neighborhood Check abgeschlossen!")
    except Exception as e:
        print(f"[{datetime.now()}] Fehler beim automatischen Check: {e}")

# Scheduler initialisieren
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=run_neighborhood_check,
    trigger="interval",
    minutes=30,
    id='neighborhood_check',
    name='Automatischer Neighborhood Check alle 30 Minuten'
)

# Scheduler starten
scheduler.start()

# Scheduler beim Beenden der App stoppen
atexit.register(lambda: scheduler.shutdown())

def get_neighbors():
    """Lädt alle Nachbarn aus der Datenbank"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM neighbors ORDER BY totalCheckedTime DESC")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        neighbors = []
        for row in rows:
            neighbor = dict(zip(columns, row))
            # JSON-Strings zurück zu Listen konvertieren
            for key, value in neighbor.items():
                if key in ['slackId', 'slackFullName'] and value:
                    try:
                        neighbor[key] = json.loads(value)
                    except:
                        neighbor[key] = [value] if value else []
            neighbors.append(neighbor)
        
        return neighbors

def get_recent_updates():
    """Lädt die neuesten Updates aus der Datenbank"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Zuerst prüfen welche Spalten existieren
        cursor.execute("PRAGMA table_info(neighbors_checked_time_update)")
        columns_info = cursor.fetchall()
        
        # Prüfen ob timestamp Spalte existiert
        has_timestamp = any(col[1] == 'timestamp' for col in columns_info)
        
        if has_timestamp:
            cursor.execute("""
                SELECT * FROM neighbors_checked_time_update 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
        else:
            # Fallback: alle Daten ohne timestamp ordering
            cursor.execute("""
                SELECT * FROM neighbors_checked_time_update 
                LIMIT 50
            """)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        updates = []
        for row in rows:
            update = dict(zip(columns, row))
            updates.append(update)
        
        return updates

def get_neighbor_updates(neighbor_id):
    """Lädt alle Updates für einen bestimmten Nachbarn"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Zuerst prüfen welche Spalten existieren
        cursor.execute("PRAGMA table_info(neighbors_checked_time_update)")
        columns_info = cursor.fetchall()
        
        # Prüfen ob timestamp Spalte existiert
        has_timestamp = any(col[1] == 'timestamp' for col in columns_info)
        
        if has_timestamp:
            cursor.execute("""
                SELECT * FROM neighbors_checked_time_update 
                WHERE id = ?
                ORDER BY timestamp DESC 
                LIMIT 100
            """, (neighbor_id,))
        else:
            cursor.execute("""
                SELECT * FROM neighbors_checked_time_update 
                WHERE id = ?
                LIMIT 100
            """, (neighbor_id,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        updates = []
        for row in rows:
            update = dict(zip(columns, row))
            updates.append(update)
        
        return updates

def get_neighbor_by_id(neighbor_id):
    """Lädt einen bestimmten Nachbarn aus der Datenbank"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM neighbors WHERE id = ?", (neighbor_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        if row:
            neighbor = dict(zip(columns, row))
            # JSON-Strings zurück zu Listen konvertieren
            for key, value in neighbor.items():
                if key in ['slackId', 'slackFullName'] and value:
                    try:
                        neighbor[key] = json.loads(value)
                    except:
                        neighbor[key] = [value] if value else []
            return neighbor
        return None

def get_user_stats(username):
    """Berechnet die Statistiken für einen bestimmten Benutzer"""
    neighbors = get_neighbors()
    user = next((n for n in neighbors if n.get('fullName') == username), None)
    if user:
        return {
            'total_checked_time': user.get('totalCheckedTime', 0),
            'total_time_hackatime': user.get('totalTimeHackatimeHours', 0),
            'total_time_stopwatch': user.get('totalTimeStopwatchHours', 0),
            'airport': user.get('airport', '-')
        }
    return None

# Füge aktuelles Datum zum Template Context hinzu
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    """Hauptseite mit Nachbarn-Übersicht"""
    username = request.cookies.get('username')
    user_stats = get_user_stats(username) if username else None
    neighbors = get_neighbors()
    total_neighbors = len(neighbors)
    total_checked_time = sum(n.get('totalCheckedTime', 0) for n in neighbors)
    
    return render_template('index.html', 
                           neighbors=neighbors,
                           total_neighbors=total_neighbors,
                           total_checked_time=total_checked_time,
                           user_stats=user_stats,
                           username=username)

@app.route('/updates')
def updates():
    """Page with the latest updates"""
    recent_updates = get_recent_updates()
    return render_template('updates.html', updates=recent_updates)

@app.route('/api/neighbors')
def api_neighbors():
    """API-Endpoint für Nachbarn-Daten"""
    neighbors = get_neighbors()
    return jsonify(neighbors)

@app.route('/api/stats')
def api_stats():
    """API-Endpoint für Statistiken"""
    neighbors = get_neighbors()
    stats = {
        'total_neighbors': len(neighbors),
        'total_checked_time': sum(n.get('totalCheckedTime', 0) for n in neighbors),
        'avg_checked_time': sum(n.get('totalCheckedTime', 0) for n in neighbors) / len(neighbors) if neighbors else 0,
        'top_performers': sorted(neighbors, key=lambda x: x.get('totalCheckedTime', 0), reverse=True)[:10]
    }
    return jsonify(stats)

@app.route('/manual-check')
def manual_check():
    """Manueller Check-Trigger"""
    try:
        run_neighborhood_check()
        return jsonify({
            'status': 'success',
            'message': 'Check successfully executed',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/scheduler-status')
def scheduler_status():
    """Displays the scheduler status"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'next_run_formatted': job.next_run_time.strftime('%d.%m.%Y %H:%M:%S') if job.next_run_time else None
        })
    
    return jsonify({
        'scheduler_running': scheduler.running,
        'jobs': jobs,
        'current_time': datetime.now().isoformat()
    })

@app.route('/next-check')
def next_check():
    """Returns the time of the next automatic check"""
    job = scheduler.get_job('neighborhood_check')
    if job and job.next_run_time:
        # Use timezone-aware datetime for comparison
        now = datetime.now(job.next_run_time.tzinfo)
        minutes_until = int((job.next_run_time - now).total_seconds() / 60)
        
        return jsonify({
            'next_run': job.next_run_time.isoformat(),
            'next_run_formatted': job.next_run_time.strftime('%d.%m.%Y at %H:%M:%S'),
            'minutes_until': minutes_until
        })
    else:
        return jsonify({
            'next_run': None,
            'next_run_formatted': 'Not available',
            'minutes_until': None
        })

@app.route('/neighbor/<neighbor_id>')
def neighbor_detail(neighbor_id):
    """Detail page for a single neighbor"""
    neighbor = get_neighbor_by_id(neighbor_id)
    if not neighbor:
        return "Neighbor not found", 404
    
    updates = get_neighbor_updates(neighbor_id)
    
    return render_template('neighbor_detail.html', 
                         neighbor=neighbor,
                         updates=updates)

# Easter Egg - Select a random neighbor
@app.route('/random-neighbor')
def random_neighbor():
    """Selects a random neighbor"""
    neighbors = get_neighbors()
    if not neighbors:
        return jsonify({"error": "No neighbors found"}), 404
    
    random_neighbor = random.choice(neighbors)
    return jsonify({
        "id": random_neighbor.get('id'),
        "name": random_neighbor.get('fullName', random_neighbor.get('id')),
        "redirect_url": f"/neighbor/{random_neighbor.get('id')}"
    })

# Fun Facts in English
@app.context_processor
def inject_fun_facts():
    return {
        'fun_facts': [
            'If {{ neighbor.fullName or "this neighbor" }} worked {{ neighbor.totalCheckedTime or 0 }} hours straight, that would be {{ (neighbor.totalCheckedTime / 24)|round }} days!',
            'With {{ neighbor.totalCheckedTime or 0 }} check hours, you could watch approximately {{ (neighbor.totalCheckedTime / 2.5)|round }} movies!',
            '{{ neighbor.totalCheckedTime or 0 }} hours equal about {{ (neighbor.totalCheckedTime / 168 * 100)|round }}% of a month!',
            'In {{ neighbor.totalCheckedTime or 0 }} hours, you could read approximately {{ (neighbor.totalCheckedTime / 5)|round }} books!',
            'With {{ neighbor.totalCheckedTime or 0 }} hours, you could almost run {{ (neighbor.totalCheckedTime / 3)|round }} marathons!'
        ]
    }

@app.route('/set-username', methods=['POST'])
def set_username():
    """Speichert den Benutzernamen in den Cookies"""
    username = request.form.get('username')
    if username:
        response = make_response(redirect(url_for('index')))
        response.set_cookie('username', username, max_age=30 * 24 * 60 * 60)  # 30 Tage
        return response
    return redirect(url_for('index'))

@app.context_processor
def inject_username():
    """Fügt den Benutzernamen aus den Cookies in den Template-Kontext ein"""
    username = request.cookies.get('username')
    return {'username': username}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8923)
