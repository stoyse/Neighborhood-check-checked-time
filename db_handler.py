import sqlite3

# Database file path
DB_PATH = 'database.db'

def write_to_neighbors(data):
    query = """
    INSERT INTO neighbors (
        id, pfp, slackId, slackFullName, githubUsername, 
        totalTimeCombinedHours, totalTimeHackatimeHours, 
        totalTimeStopwatchHours, fullName, totalCheckedTime, airport
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        data['id'], data['pfp'], data['slackId'], data['slackFullName'], 
        data['githubUsername'], data['totalTimeCombinedHours'], 
        data['totalTimeHackatimeHours'], data['totalTimeStopwatchHours'], 
        data['fullName'], data['totalCheckedTime'], data['airport']
    )
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()

def write_to_neighbors_checked_time_update(data):
    query = """
    INSERT INTO neighbors_checked_time_update (
        id, pfp, slackId, slackFullName, githubUsername, 
        totalTimeCombinedHours, totalTimeHackatimeHours, 
        totalTimeStopwatchHours, fullName, totalCheckedTime, 
        totalCheckedTimeUpdate, airport
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        data['id'], data['pfp'], data['slackId'], data['slackFullName'], 
        data['githubUsername'], data['totalTimeCombinedHours'], 
        data['totalTimeHackatimeHours'], data['totalTimeStopwatchHours'], 
        data['fullName'], data['totalCheckedTime'], 
        data['totalCheckedTimeUpdate'], data['airport']
    )
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()