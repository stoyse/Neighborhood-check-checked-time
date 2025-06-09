CREATE TABLE neighbors (
    id TEXT PRIMARY KEY,
    pfp TEXT,
    slackId TEXT, -- JSON array stored as TEXT
    slackFullName TEXT, -- JSON array stored as TEXT
    githubUsername TEXT,
    totalTimeCombinedHours REAL,
    totalTimeHackatimeHours REAL,
    totalTimeStopwatchHours REAL,
    fullName TEXT,
    totalCheckedTime REAL,
    airport TEXT
);

CREATE TABLE neighbors_checked_time_update (
    id TEXT PRIMARY KEY,
    pfp TEXT,
    slackId TEXT, -- JSON array stored as TEXT
    slackFullName TEXT, -- JSON array stored as TEXT
    githubUsername TEXT,
    totalTimeCombinedHours REAL,
    totalTimeHackatimeHours REAL,
    totalTimeStopwatchHours REAL,
    fullName TEXT,
    totalCheckedTime REAL,
    totalCheckedTimeUpdate REAL,
    airport TEXT
);