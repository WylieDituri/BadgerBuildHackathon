import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

function ClassList() {
  const { majorId } = useParams();
  const [major, setMajor] = useState(null);
  const [classes, setClasses] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.getMajor(majorId),
      api.getClassesByMajor(majorId),
      api.getRecommendations(majorId)
    ])
      .then(([majorRes, classesRes, recsRes]) => {
        setMajor(majorRes.data);
        setClasses(classesRes.data);
        setRecommendations(recsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [majorId]);

  if (loading) return <div className="loading">Loading classes...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / <Link to={`/college/${major?.college_id}`}>College</Link> / {major?.name}
      </div>
      <h1 className="page-title">Classes in {major?.name}</h1>
      
      {/* AI Recommendations Section */}
      {recommendations && (
        <div className="recommendations">
          <h2 className="section-title">🤖 AI Recommendations for You</h2>
          
          {recommendations.classes && recommendations.classes.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '0.5rem' }}>Popular Classes</h3>
              {recommendations.classes.slice(0, 3).map(cls => (
                <div key={cls.id} className="recommendation-item">
                  <strong>{cls.code}</strong> - {cls.name}
                  {cls.post_count > 0 && <span style={{ color: '#667eea', marginLeft: '1rem' }}>
                    💬 {cls.post_count} discussions
                  </span>}
                </div>
              ))}
            </div>
          )}

          {recommendations.professors && recommendations.professors.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '0.5rem' }}>Top-Rated Professors</h3>
              {recommendations.professors.slice(0, 3).map(prof => (
                <div key={prof.id} className="recommendation-item">
                  <strong>{prof.name}</strong>
                  <span style={{ color: '#155724', marginLeft: '1rem' }}>
                    ⭐ {prof.avg_rating?.toFixed(1)} / 5.0
                  </span>
                </div>
              ))}
            </div>
          )}

          {recommendations.events && recommendations.events.length > 0 && (
            <div>
              <h3 style={{ marginBottom: '0.5rem' }}>Upcoming Events</h3>
              {recommendations.events.slice(0, 3).map(event => (
                <div key={event.id} className="recommendation-item">
                  <strong>{event.title}</strong>
                  <div style={{ fontSize: '0.9rem', color: '#666' }}>
                    {new Date(event.start_time).toLocaleDateString()} - {event.location}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <h2 className="section-title" style={{ marginTop: '2rem' }}>All Classes</h2>
      <div className="card-grid">
        {classes.map(cls => (
          <div key={cls.id} className="card" onClick={() => navigate(`/class/${cls.id}`)}>
            <div className="card-subtitle">{cls.code}</div>
            <h2 className="card-title">{cls.name}</h2>
            <div className="card-description">{cls.description}</div>
            <div className="card-meta">
              <span>📚 {cls.credits} credits</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ClassList;
