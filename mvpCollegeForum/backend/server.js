const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const db = require('./database');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// ============= COLLEGES =============
app.get('/api/colleges', (req, res) => {
  db.all('SELECT * FROM colleges', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.get('/api/colleges/:id', (req, res) => {
  db.get('SELECT * FROM colleges WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(row);
  });
});

// ============= MAJORS =============
app.get('/api/colleges/:collegeId/majors', (req, res) => {
  db.all('SELECT * FROM majors WHERE college_id = ?', [req.params.collegeId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.get('/api/majors/:id', (req, res) => {
  db.get('SELECT * FROM majors WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(row);
  });
});

// ============= CLASSES =============
app.get('/api/majors/:majorId/classes', (req, res) => {
  db.all('SELECT * FROM classes WHERE major_id = ?', [req.params.majorId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.get('/api/classes/:id', (req, res) => {
  db.get('SELECT * FROM classes WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(row);
  });
});

// ============= GRADE DISTRIBUTIONS =============
app.get('/api/classes/:classId/grades', (req, res) => {
  const query = `
    SELECT gd.*, p.name as professor_name 
    FROM grade_distributions gd
    LEFT JOIN professors p ON gd.professor_id = p.id
    WHERE gd.class_id = ?
  `;
  db.all(query, [req.params.classId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// ============= PROFESSORS =============
app.get('/api/colleges/:collegeId/professors', (req, res) => {
  db.all('SELECT * FROM professors WHERE college_id = ?', [req.params.collegeId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.get('/api/professors/:id', (req, res) => {
  db.get('SELECT * FROM professors WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(row);
  });
});

// ============= PROFESSOR RATINGS =============
app.get('/api/professors/:professorId/ratings', (req, res) => {
  db.all('SELECT * FROM professor_ratings WHERE professor_id = ? ORDER BY created_at DESC', [req.params.professorId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/professors/:professorId/ratings', (req, res) => {
  const { rating, difficulty, would_take_again, comment, class_id } = req.body;
  const query = `
    INSERT INTO professor_ratings (professor_id, class_id, rating, difficulty, would_take_again, comment)
    VALUES (?, ?, ?, ?, ?, ?)
  `;
  db.run(query, [req.params.professorId, class_id, rating, difficulty, would_take_again, comment], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ id: this.lastID });
  });
});

// Get average rating for a professor
app.get('/api/professors/:professorId/rating-summary', (req, res) => {
  const query = `
    SELECT 
      AVG(rating) as avg_rating,
      AVG(difficulty) as avg_difficulty,
      COUNT(*) as total_ratings,
      SUM(CASE WHEN would_take_again = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as would_take_again_percent
    FROM professor_ratings
    WHERE professor_id = ?
  `;
  db.get(query, [req.params.professorId], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(row);
  });
});

// ============= FORUM POSTS =============
app.get('/api/classes/:classId/posts', (req, res) => {
  db.all('SELECT * FROM forum_posts WHERE class_id = ? ORDER BY created_at DESC', [req.params.classId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/classes/:classId/posts', (req, res) => {
  const { title, content, author } = req.body;
  const query = 'INSERT INTO forum_posts (class_id, title, content, author) VALUES (?, ?, ?, ?)';
  db.run(query, [req.params.classId, title, content, author], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ id: this.lastID });
  });
});

// ============= FORUM COMMENTS =============
app.get('/api/posts/:postId/comments', (req, res) => {
  db.all('SELECT * FROM forum_comments WHERE post_id = ? ORDER BY created_at ASC', [req.params.postId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/posts/:postId/comments', (req, res) => {
  const { content, author } = req.body;
  const query = 'INSERT INTO forum_comments (post_id, content, author) VALUES (?, ?, ?)';
  db.run(query, [req.params.postId, content, author], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ id: this.lastID });
  });
});

// ============= EVENTS =============
app.get('/api/colleges/:collegeId/events', (req, res) => {
  const { major_id } = req.query;
  let query = 'SELECT * FROM events WHERE college_id = ?';
  const params = [req.params.collegeId];
  
  if (major_id) {
    query += ' AND (major_id = ? OR major_id IS NULL)';
    params.push(major_id);
  }
  
  query += ' ORDER BY start_time ASC';
  
  db.all(query, params, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

app.post('/api/colleges/:collegeId/events', (req, res) => {
  const { title, description, event_type, location, start_time, end_time, organizer, major_id } = req.body;
  const query = `
    INSERT INTO events (college_id, major_id, title, description, event_type, location, start_time, end_time, organizer)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;
  db.run(query, [req.params.collegeId, major_id, title, description, event_type, location, start_time, end_time, organizer], function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ id: this.lastID });
  });
});

// ============= AI RECOMMENDATIONS =============
app.get('/api/majors/:majorId/recommendations', (req, res) => {
  // Simple recommendation engine based on major
  const majorId = req.params.majorId;
  
  const recommendations = {
    classes: [],
    events: [],
    professors: []
  };

  // Get popular classes in the major
  const classQuery = `
    SELECT c.*, COUNT(fp.id) as post_count
    FROM classes c
    LEFT JOIN forum_posts fp ON c.id = fp.class_id
    WHERE c.major_id = ?
    GROUP BY c.id
    ORDER BY post_count DESC
    LIMIT 5
  `;

  db.all(classQuery, [majorId], (err, classes) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    recommendations.classes = classes;

    // Get upcoming events for this major
    const eventQuery = `
      SELECT * FROM events
      WHERE major_id = ? OR major_id IS NULL
      AND start_time > datetime('now')
      ORDER BY start_time ASC
      LIMIT 5
    `;

    db.all(eventQuery, [majorId], (err, events) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      recommendations.events = events;

      // Get top-rated professors in related classes
      const profQuery = `
        SELECT p.*, AVG(pr.rating) as avg_rating, COUNT(pr.id) as rating_count
        FROM professors p
        JOIN professor_ratings pr ON p.id = pr.professor_id
        JOIN classes c ON pr.class_id = c.id
        WHERE c.major_id = ?
        GROUP BY p.id
        HAVING rating_count >= 2
        ORDER BY avg_rating DESC
        LIMIT 5
      `;

      db.all(profQuery, [majorId], (err, professors) => {
        if (err) {
          res.status(500).json({ error: err.message });
          return;
        }
        recommendations.professors = professors;
        res.json(recommendations);
      });
    });
  });
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
