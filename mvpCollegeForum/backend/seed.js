const db = require('./database');

function seedDatabase() {
  console.log('Starting database seeding...');

  // Wait for database to initialize
  setTimeout(() => {
    db.serialize(() => {
      // Insert Colleges
      db.run(`INSERT INTO colleges (name, abbreviation, location, description) VALUES 
        ('University of Wisconsin-Madison', 'UW-Madison', 'Madison, WI', 'A top-tier public research university'),
        ('University of California, Berkeley', 'UC Berkeley', 'Berkeley, CA', 'A leading public research university')
      `, (err) => {
        if (err) console.error('Error inserting colleges:', err);
        else console.log('✓ Colleges inserted');
      });

      // Insert Majors for UW-Madison
      db.run(`INSERT INTO majors (college_id, name, code, description) VALUES 
        (1, 'Computer Science', 'CS', 'Study of computation, algorithms, and information systems'),
        (1, 'Data Science', 'DS', 'Interdisciplinary field combining statistics and CS'),
        (1, 'Business', 'BUS', 'Study of management, finance, and entrepreneurship'),
        (2, 'Computer Science', 'CS', 'Leading CS program with focus on AI and systems'),
        (2, 'Electrical Engineering', 'EECS', 'Study of electrical systems and computer engineering')
      `, (err) => {
        if (err) console.error('Error inserting majors:', err);
        else console.log('✓ Majors inserted');
      });

      // Insert Classes for CS major at UW-Madison
      db.run(`INSERT INTO classes (major_id, name, code, credits, description) VALUES 
        (1, 'Introduction to Programming', 'CS 200', 3, 'First course in computer science using Java'),
        (1, 'Data Structures', 'CS 300', 3, 'Study of fundamental data structures and algorithms'),
        (1, 'Algorithms', 'CS 400', 3, 'Advanced algorithms and complexity analysis'),
        (1, 'Operating Systems', 'CS 537', 3, 'Principles of operating system design'),
        (1, 'Machine Learning', 'CS 540', 3, 'Introduction to machine learning techniques'),
        (2, 'Introduction to Data Science', 'DS 201', 3, 'Foundations of data science and analytics'),
        (2, 'Statistical Methods', 'DS 300', 3, 'Statistical analysis for data science'),
        (3, 'Introduction to Business', 'BUS 101', 3, 'Fundamentals of business management')
      `, (err) => {
        if (err) console.error('Error inserting classes:', err);
        else console.log('✓ Classes inserted');
      });

      // Insert Professors
      db.run(`INSERT INTO professors (college_id, name, department, email) VALUES 
        (1, 'Dr. Sarah Johnson', 'Computer Science', 'sjohnson@wisc.edu'),
        (1, 'Dr. Michael Chen', 'Computer Science', 'mchen@wisc.edu'),
        (1, 'Dr. Emily Rodriguez', 'Data Science', 'erodriguez@wisc.edu'),
        (1, 'Dr. James Wilson', 'Computer Science', 'jwilson@wisc.edu'),
        (2, 'Dr. David Kim', 'Computer Science', 'dkim@berkeley.edu')
      `, (err) => {
        if (err) console.error('Error inserting professors:', err);
        else console.log('✓ Professors inserted');
      });

      // Insert Professor Ratings
      db.run(`INSERT INTO professor_ratings (professor_id, class_id, rating, difficulty, would_take_again, comment) VALUES 
        (1, 1, 4.5, 3.0, 1, 'Great intro professor! Very clear explanations.'),
        (1, 1, 4.0, 3.5, 1, 'Helpful and engaging lectures'),
        (2, 2, 4.8, 4.0, 1, 'Challenging but rewarding. Really knows the material.'),
        (2, 2, 4.2, 4.5, 1, 'Tough grader but fair'),
        (3, 6, 5.0, 2.5, 1, 'Amazing professor! Makes data science fun and accessible.'),
        (4, 4, 3.8, 4.5, 0, 'Very difficult class, not great at explaining concepts'),
        (4, 5, 4.5, 4.0, 1, 'Tough but excellent ML course')
      `, (err) => {
        if (err) console.error('Error inserting ratings:', err);
        else console.log('✓ Professor ratings inserted');
      });

      // Insert Grade Distributions
      db.run(`INSERT INTO grade_distributions (class_id, professor_id, semester, a_percentage, b_percentage, c_percentage, d_percentage, f_percentage) VALUES 
        (1, 1, 'Fall 2024', 35.5, 40.2, 18.3, 4.0, 2.0),
        (2, 2, 'Fall 2024', 28.0, 38.5, 25.0, 6.5, 2.0),
        (3, 2, 'Spring 2024', 25.5, 35.0, 28.0, 8.5, 3.0),
        (4, 4, 'Fall 2024', 20.0, 35.0, 30.0, 10.0, 5.0),
        (5, 4, 'Spring 2024', 30.0, 35.0, 25.0, 7.0, 3.0),
        (6, 3, 'Fall 2024', 40.0, 35.0, 20.0, 3.0, 2.0)
      `, (err) => {
        if (err) console.error('Error inserting grades:', err);
        else console.log('✓ Grade distributions inserted');
      });

      // Insert Forum Posts
      db.run(`INSERT INTO forum_posts (class_id, title, content, author) VALUES 
        (1, 'How difficult is CS 200?', 'Im thinking about taking this course next semester. How much time should I expect to spend on it?', 'student123'),
        (1, 'Study group for CS 200?', 'Anyone want to form a study group? Im struggling with the recursion concepts.', 'BadgerCS'),
        (2, 'Best resources for data structures?', 'Looking for good online resources to supplement the lectures. Any recommendations?', 'techie2024'),
        (3, 'CS 400 project partners', 'Looking for a partner for the final project. Anyone interested?', 'codeguru'),
        (5, 'ML prerequisites', 'Is CS 540 manageable without taking linear algebra first?', 'aiEnthusiast')
      `, (err) => {
        if (err) console.error('Error inserting posts:', err);
        else console.log('✓ Forum posts inserted');
      });

      // Insert Forum Comments
      db.run(`INSERT INTO forum_comments (post_id, content, author) VALUES 
        (1, 'Its pretty manageable if you have some programming experience. Expect to spend 8-10 hours/week.', 'seniorCS'),
        (1, 'Dr. Johnson is a great professor! The course is well-structured.', 'alumBadger'),
        (2, 'Im down! Let me know when and where.', 'studyBuddy'),
        (3, 'Check out visualgo.net - its amazing for visualizing data structures!', 'helpfulPeer'),
        (3, 'I also recommend the book "Cracking the Coding Interview"', 'csGrad')
      `, (err) => {
        if (err) console.error('Error inserting comments:', err);
        else console.log('✓ Forum comments inserted');
      });

      // Insert Events (last operation, exit after completion)
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const nextWeek = new Date(now);
      nextWeek.setDate(nextWeek.getDate() + 7);
      const twoWeeks = new Date(now);
      twoWeeks.setDate(twoWeeks.getDate() + 14);

      db.run(`INSERT INTO events (college_id, major_id, title, description, event_type, location, start_time, end_time, organizer) VALUES 
        (1, 1, 'CS Career Fair', 'Meet with top tech companies recruiting CS students', 'Career Fair', 'Memorial Union', '${tomorrow.toISOString()}', '${tomorrow.toISOString()}', 'Career Services'),
        (1, 1, 'Hackathon: BadgerBuild', '48-hour hackathon with prizes and mentorship', 'Hackathon', 'CS Building', '${nextWeek.toISOString()}', '${nextWeek.toISOString()}', 'CS Club'),
        (1, NULL, 'Tech Talk: AI in Healthcare', 'Guest speaker from Mayo Clinic on AI applications', 'Talk', 'Engineering Hall', '${twoWeeks.toISOString()}', '${twoWeeks.toISOString()}', 'AI Student Org'),
        (1, 2, 'Data Science Workshop', 'Hands-on workshop for data visualization with Python', 'Workshop', 'Discovery Building', '${nextWeek.toISOString()}', '${nextWeek.toISOString()}', 'Data Science Club'),
        (1, 1, 'CS Club Meeting', 'Weekly meeting - discussing upcoming events and projects', 'Club Meeting', 'CS Lounge', '${tomorrow.toISOString()}', '${tomorrow.toISOString()}', 'CS Club'),
        (2, 4, 'EECS Industry Night', 'Networking event with Bay Area tech companies', 'Networking', 'Cory Hall', '${nextWeek.toISOString()}', '${nextWeek.toISOString()}', 'EECS Department')
      `, (err) => {
        if (err) {
          console.error('Error inserting events:', err);
        } else {
          console.log('✓ Events inserted');
          console.log('\n✅ Database seeded successfully!');
        }
        // Close database connection and exit after final operation
        db.close((closeErr) => {
          if (closeErr) console.error('Error closing database:', closeErr);
          process.exit(err ? 1 : 0);
        });
      });
    });
  }, 1500); // Increased timeout for database initialization
}

seedDatabase();
