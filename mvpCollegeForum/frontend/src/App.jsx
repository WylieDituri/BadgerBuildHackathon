import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CollegeList from './pages/CollegeList';
import MajorList from './pages/MajorList';
import ClassList from './pages/ClassList';
import ClassView from './pages/ClassView';
import ProfessorList from './pages/ProfessorList';
import ProfessorView from './pages/ProfessorView';
import EventList from './pages/EventList';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              🎓 College Forum
            </Link>
            <div className="nav-links">
              <Link to="/">Colleges</Link>
            </div>
          </div>
        </nav>

        <div className="main-content">
          <Routes>
            <Route path="/" element={<CollegeList />} />
            <Route path="/college/:collegeId" element={<MajorList />} />
            <Route path="/major/:majorId" element={<ClassList />} />
            <Route path="/class/:classId" element={<ClassView />} />
            <Route path="/college/:collegeId/professors" element={<ProfessorList />} />
            <Route path="/professor/:professorId" element={<ProfessorView />} />
            <Route path="/college/:collegeId/events" element={<EventList />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
