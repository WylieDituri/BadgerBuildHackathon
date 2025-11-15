import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

function MajorList() {
  const { collegeId } = useParams();
  const [college, setCollege] = useState(null);
  const [majors, setMajors] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.getCollege(collegeId),
      api.getMajorsByCollege(collegeId)
    ])
      .then(([collegeRes, majorsRes]) => {
        setCollege(collegeRes.data);
        setMajors(majorsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [collegeId]);

  if (loading) return <div className="loading">Loading majors...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / {college?.name}
      </div>
      <h1 className="page-title">Select Your Major at {college?.name}</h1>
      
      <div style={{ marginBottom: '2rem' }}>
        <Link to={`/college/${collegeId}/professors`}>
          <button style={{ marginRight: '1rem' }}>View Professors</button>
        </Link>
        <Link to={`/college/${collegeId}/events`}>
          <button>View Events</button>
        </Link>
      </div>

      <div className="card-grid">
        {majors.map(major => (
          <div key={major.id} className="card" onClick={() => navigate(`/major/${major.id}`)}>
            <h2 className="card-title">{major.name}</h2>
            <div className="card-subtitle">{major.code}</div>
            <div className="card-description">{major.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MajorList;
