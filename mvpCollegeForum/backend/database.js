const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const db = new sqlite3.Database(path.join(__dirname, 'forum.db'), (err) => {
  if (err) {
    console.error('Error connecting to database:', err);
  } else {
    console.log('Connected to SQLite database');
    initializeDatabase();
  }
});

function initializeDatabase() {
  db.serialize(() => {
    // Colleges table
    db.run(`CREATE TABLE IF NOT EXISTS colleges (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      abbreviation TEXT NOT NULL,
      location TEXT,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Majors table
    db.run(`CREATE TABLE IF NOT EXISTS majors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      college_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      code TEXT,
      description TEXT,
      FOREIGN KEY (college_id) REFERENCES colleges(id)
    )`);

    // Classes table
    db.run(`CREATE TABLE IF NOT EXISTS classes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      major_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      code TEXT NOT NULL,
      credits INTEGER,
      description TEXT,
      FOREIGN KEY (major_id) REFERENCES majors(id)
    )`);

    // Professors table
    db.run(`CREATE TABLE IF NOT EXISTS professors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      college_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      department TEXT,
      email TEXT,
      FOREIGN KEY (college_id) REFERENCES colleges(id)
    )`);

    // Professor Ratings table
    db.run(`CREATE TABLE IF NOT EXISTS professor_ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      professor_id INTEGER NOT NULL,
      class_id INTEGER,
      rating REAL NOT NULL,
      difficulty REAL,
      would_take_again INTEGER,
      comment TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (professor_id) REFERENCES professors(id),
      FOREIGN KEY (class_id) REFERENCES classes(id)
    )`);

    // Grade Distributions table
    db.run(`CREATE TABLE IF NOT EXISTS grade_distributions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_id INTEGER NOT NULL,
      professor_id INTEGER,
      semester TEXT,
      a_percentage REAL,
      b_percentage REAL,
      c_percentage REAL,
      d_percentage REAL,
      f_percentage REAL,
      FOREIGN KEY (class_id) REFERENCES classes(id),
      FOREIGN KEY (professor_id) REFERENCES professors(id)
    )`);

    // Forum Posts table
    db.run(`CREATE TABLE IF NOT EXISTS forum_posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      author TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (class_id) REFERENCES classes(id)
    )`);

    // Forum Comments table
    db.run(`CREATE TABLE IF NOT EXISTS forum_comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id INTEGER NOT NULL,
      content TEXT NOT NULL,
      author TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (post_id) REFERENCES forum_posts(id)
    )`);

    // Events table
    db.run(`CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      college_id INTEGER NOT NULL,
      major_id INTEGER,
      title TEXT NOT NULL,
      description TEXT,
      event_type TEXT,
      location TEXT,
      start_time DATETIME,
      end_time DATETIME,
      organizer TEXT,
      FOREIGN KEY (college_id) REFERENCES colleges(id),
      FOREIGN KEY (major_id) REFERENCES majors(id)
    )`);

    console.log('Database tables initialized');
  });
}

module.exports = db;
