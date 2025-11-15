# College Forum MVP

A comprehensive college forum platform combining features from MadGrades, RateMyProfessor, and Reddit-style forums. This MVP supports 2 colleges (UW-Madison and UC Berkeley) with a complete navigation system: College → Major → Classes.

## Features

### ✅ Implemented in MVP
- **📚 College/Major/Class Navigation** - Hierarchical browsing from college to specific classes
- **💬 Forum System** - Reddit-style discussion forums for each class with posts and comments
- **⭐ Professor Ratings** - Rate and review professors (like RateMyProfessor)
- **📊 Grade Distributions** - View grade distributions by class and professor (like MadGrades)
- **📅 Events & Organizations** - Browse upcoming career fairs, hackathons, club meetings
- **🤖 AI Recommendations** - Personalized suggestions for classes, professors, and events based on your major

## Tech Stack

- **Frontend**: React 18 + Vite
- **Backend**: Node.js + Express
- **Database**: SQLite
- **Routing**: React Router v6
- **HTTP Client**: Axios

## Project Structure

```
mvpCollegeForum/
├── backend/
│   ├── server.js          # Express server with all API routes
│   ├── database.js        # Database schema and initialization
│   ├── seed.js            # Sample data for 2 colleges
│   ├── package.json
│   └── forum.db          # SQLite database (created on first run)
├── frontend/
│   ├── src/
│   │   ├── pages/        # React page components
│   │   ├── services/     # API service layer
│   │   ├── App.jsx       # Main app with routing
│   │   └── main.jsx      # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Start the server:
```bash
npm start
```

The backend will run on `http://localhost:5000`

4. Seed the database (in a new terminal):
```bash
node seed.js
```

This will populate the database with:
- 2 colleges (UW-Madison, UC Berkeley)
- Multiple majors (CS, Data Science, Business, EECS)
- Sample classes, professors, ratings, forum posts, and events

### Frontend Setup

1. Navigate to the frontend directory (in a new terminal):
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Browse Colleges**: Start at the home page and select a college
2. **Choose Major**: Select your major to see available classes
3. **View AI Recommendations**: See personalized suggestions for popular classes, top professors, and upcoming events
4. **Explore Classes**: Click on any class to view:
   - Grade distributions by professor and semester
   - Forum discussions with posts and comments
   - Class details and credits
5. **Rate Professors**: Navigate to Professors page to view and rate professors
6. **Check Events**: View upcoming events, career fairs, and club meetings

## API Endpoints

### Colleges
- `GET /api/colleges` - Get all colleges
- `GET /api/colleges/:id` - Get specific college

### Majors
- `GET /api/colleges/:collegeId/majors` - Get majors for a college
- `GET /api/majors/:id` - Get specific major

### Classes
- `GET /api/majors/:majorId/classes` - Get classes for a major
- `GET /api/classes/:id` - Get specific class
- `GET /api/classes/:classId/grades` - Get grade distributions

### Professors
- `GET /api/colleges/:collegeId/professors` - Get professors
- `GET /api/professors/:id` - Get specific professor
- `GET /api/professors/:professorId/ratings` - Get all ratings
- `GET /api/professors/:professorId/rating-summary` - Get average ratings
- `POST /api/professors/:professorId/ratings` - Add new rating

### Forum
- `GET /api/classes/:classId/posts` - Get forum posts for a class
- `POST /api/classes/:classId/posts` - Create new post
- `GET /api/posts/:postId/comments` - Get comments on a post
- `POST /api/posts/:postId/comments` - Add comment to post

### Events
- `GET /api/colleges/:collegeId/events` - Get events for a college
- `POST /api/colleges/:collegeId/events` - Create new event

### AI Recommendations
- `GET /api/majors/:majorId/recommendations` - Get personalized recommendations

## Sample Data

The MVP includes realistic sample data for:
- **UW-Madison** with CS, Data Science, and Business majors
- **UC Berkeley** with CS and EECS majors
- 5+ classes per major with descriptions
- 5 professors with ratings and reviews
- Grade distributions for multiple semesters
- Forum posts with comments
- Upcoming events (career fairs, hackathons, club meetings)

## Future Enhancements

- User authentication and profiles
- Upvoting/downvoting forum posts
- Advanced AI recommendations using ML
- Search functionality across classes and professors
- Real-time chat features
- Mobile app
- Integration with real university APIs
- Course prerequisite visualization
- Study group matching

## Development

### Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-restart
```

### Frontend Development
```bash
cd frontend
npm run dev  # Vite hot reload
```

### Building for Production
```bash
cd frontend
npm run build
npm run preview
```

## Notes

- This is an MVP built for demonstration purposes
- Sample data is included for 2 colleges
- The AI recommendations use simple heuristics (forum activity, ratings)
- For production, consider:
  - Adding authentication (JWT, OAuth)
  - Migrating to PostgreSQL or MongoDB
  - Implementing proper error handling
  - Adding data validation
  - Setting up proper CORS policies
  - Deploying to cloud services (AWS, Heroku, Vercel)

## License

MIT License - feel free to use this project as a starting point for your own college forum application!
