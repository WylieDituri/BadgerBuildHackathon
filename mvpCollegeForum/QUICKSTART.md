# Quick Start Guide

## 🚀 Running the Application

### Step 1: Start Backend Server
Open a terminal and run:
```bash
cd backend
npm start
```

The backend API will be running at `http://localhost:5000`

### Step 2: Start Frontend Server
Open a **NEW** terminal window and run:
```bash
cd frontend
npm run dev
```

The frontend will be running at `http://localhost:3000`

### Step 3: Open Your Browser
Navigate to: `http://localhost:3000`

## ✅ Already Done
- ✅ Dependencies installed for both backend and frontend
- ✅ Database seeded with sample data (UW-Madison and UC Berkeley)
- ✅ Sample professors, classes, forum posts, and events added

## 🎯 Try These Features

1. **Browse Colleges** 
   - Click on UW-Madison or UC Berkeley

2. **Explore Majors**
   - Click on "Computer Science" or "Data Science"
   - See AI-powered recommendations for popular classes

3. **View a Class**
   - Click on any class (e.g., "CS 200")
   - See grade distributions
   - Read and create forum posts
   - Add comments to discussions

4. **Rate Professors**
   - Click "View Professors" button
   - Click on any professor
   - View ratings or add your own

5. **Check Events**
   - Click "View Events" button
   - See upcoming hackathons, career fairs, and club meetings

## 🛠️ Development Tips

### Backend Hot Reload
For automatic server restart on file changes:
```bash
cd backend
npm run dev
```

### View Database
The SQLite database is located at:
```
backend/forum.db
```

You can open it with any SQLite viewer or command line:
```bash
cd backend
sqlite3 forum.db
.tables
SELECT * FROM colleges;
```

### API Testing
Test API endpoints directly:
```bash
curl http://localhost:5000/api/colleges
curl http://localhost:5000/api/colleges/1/majors
```

## 📝 Sample Data Overview

### Colleges
- University of Wisconsin-Madison (ID: 1)
- University of California, Berkeley (ID: 2)

### Sample Majors
- Computer Science
- Data Science  
- Business
- Electrical Engineering

### Sample Classes
- CS 200: Introduction to Programming
- CS 300: Data Structures
- CS 400: Algorithms
- CS 537: Operating Systems
- CS 540: Machine Learning
- And more...

### Sample Professors
- Dr. Sarah Johnson (CS)
- Dr. Michael Chen (CS)
- Dr. Emily Rodriguez (Data Science)
- Dr. James Wilson (CS)
- Dr. David Kim (CS at Berkeley)

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 or 3000 is already in use:

**Backend (port 5000):**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

**Frontend (port 3000):**
Vite will automatically try the next available port (3001, 3002, etc.)

### Database Issues
If you need to reset the database:
```bash
cd backend
rm forum.db
node seed.js
```

### Dependencies Issues
If something isn't working, try reinstalling:
```bash
cd backend && rm -rf node_modules && npm install
cd ../frontend && rm -rf node_modules && npm install
```

## 🎉 Happy Building!

Your MVP is ready to go. Start building amazing features on top of this foundation!
