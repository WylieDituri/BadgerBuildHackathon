import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

function CollegeList() {
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getColleges()
      .then(res => {
        setColleges(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching colleges:', err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading colleges...</div>;

  return (
    <div>
      <h1 className="page-title">Select Your College</h1>
      <div className="card-grid">
        {colleges.map(college => (
          <div key={college.id} className="card" onClick={() => navigate(`/college/${college.id}`)}>
            <h2 className="card-title">{college.name}</h2>
            <div className="card-subtitle">{college.abbreviation}</div>
            <div className="card-description">
              📍 {college.location}
              <br />
              {college.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CollegeList;
