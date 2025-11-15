import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

function ProfessorList() {
  const { collegeId } = useParams();
  const [college, setCollege] = useState(null);
  const [professors, setProfessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.getCollege(collegeId),
      api.getProfessorsByCollege(collegeId)
    ])
      .then(([collegeRes, profsRes]) => {
        setCollege(collegeRes.data);
        setProfessors(profsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [collegeId]);

  if (loading) return <div className="loading">Loading professors...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / <Link to={`/college/${collegeId}`}>{college?.name}</Link> / Professors
      </div>
      <h1 className="page-title">Professors at {college?.name}</h1>
      
      <div className="card-grid">
        {professors.map(professor => (
          <div key={professor.id} className="card" onClick={() => navigate(`/professor/${professor.id}`)}>
            <h2 className="card-title">{professor.name}</h2>
            <div className="card-subtitle">{professor.department}</div>
            <div className="card-description">
              📧 {professor.email}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProfessorList;
