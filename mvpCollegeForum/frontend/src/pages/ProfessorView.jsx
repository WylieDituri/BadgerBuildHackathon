import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function ProfessorView() {
  const { professorId } = useParams();
  const [professor, setProfessor] = useState(null);
  const [summary, setSummary] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  const [newRating, setNewRating] = useState({
    rating: 5,
    difficulty: 3,
    would_take_again: 1,
    comment: '',
    class_id: null
  });

  useEffect(() => {
    Promise.all([
      api.getProfessor(professorId),
      api.getProfessorSummary(professorId),
      api.getProfessorRatings(professorId)
    ])
      .then(([profRes, summaryRes, ratingsRes]) => {
        setProfessor(profRes.data);
        setSummary(summaryRes.data);
        setRatings(ratingsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [professorId]);

  const handleSubmitRating = (e) => {
    e.preventDefault();
    api.addProfessorRating(professorId, newRating)
      .then(() => {
        return Promise.all([
          api.getProfessorSummary(professorId),
          api.getProfessorRatings(professorId)
        ]);
      })
      .then(([summaryRes, ratingsRes]) => {
        setSummary(summaryRes.data);
        setRatings(ratingsRes.data);
        setNewRating({
          rating: 5,
          difficulty: 3,
          would_take_again: 1,
          comment: '',
          class_id: null
        });
        setShowForm(false);
      })
      .catch(err => console.error('Error submitting rating:', err));
  };

  const getRatingClass = (rating) => {
    if (rating >= 4.0) return 'high';
    if (rating >= 3.0) return 'medium';
    return 'low';
  };

  if (loading) return <div className="loading">Loading professor data...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / <Link to={`/college/${professor?.college_id}/professors`}>Professors</Link> / {professor?.name}
      </div>
      
      <div className="section">
        <h1 className="page-title">{professor?.name}</h1>
        <div style={{ color: '#667eea', fontSize: '1.2rem', marginBottom: '0.5rem' }}>
          {professor?.department}
        </div>
        <div style={{ color: '#888' }}>
          📧 {professor?.email}
        </div>

        {summary && summary.total_ratings > 0 && (
          <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Overall Rating</div>
              <div className={`rating ${getRatingClass(summary.avg_rating)}`} style={{ fontSize: '1.5rem' }}>
                ⭐ {summary.avg_rating?.toFixed(1)} / 5.0
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Difficulty</div>
              <div className="rating" style={{ fontSize: '1.5rem' }}>
                {summary.avg_difficulty?.toFixed(1)} / 5.0
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Would Take Again</div>
              <div className="rating high" style={{ fontSize: '1.5rem' }}>
                {summary.would_take_again_percent?.toFixed(0)}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Total Ratings</div>
              <div style={{ fontSize: '1.5rem', fontWeight: '600', color: '#333' }}>
                {summary.total_ratings}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 className="section-title" style={{ marginBottom: 0 }}>Student Ratings</h2>
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Add Rating'}
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleSubmitRating} style={{ marginTop: '1.5rem', padding: '1.5rem', background: '#f9f9f9', borderRadius: '8px' }}>
            <h3 style={{ marginBottom: '1rem' }}>Rate This Professor</h3>
            <div className="form-group">
              <label>Overall Rating (1-5)</label>
              <input
                type="number"
                min="1"
                max="5"
                step="0.1"
                value={newRating.rating}
                onChange={(e) => setNewRating({ ...newRating, rating: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-group">
              <label>Difficulty (1-5)</label>
              <input
                type="number"
                min="1"
                max="5"
                step="0.1"
                value={newRating.difficulty}
                onChange={(e) => setNewRating({ ...newRating, difficulty: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-group">
              <label>Would Take Again?</label>
              <select
                value={newRating.would_take_again}
                onChange={(e) => setNewRating({ ...newRating, would_take_again: parseInt(e.target.value) })}
              >
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </div>
            <div className="form-group">
              <label>Comment</label>
              <textarea
                value={newRating.comment}
                onChange={(e) => setNewRating({ ...newRating, comment: e.target.value })}
                placeholder="Share your experience with this professor..."
                required
              />
            </div>
            <button type="submit">Submit Rating</button>
          </form>
        )}

        <div style={{ marginTop: '2rem' }}>
          {ratings.length === 0 ? (
            <p style={{ color: '#888', textAlign: 'center', padding: '2rem' }}>
              No ratings yet. Be the first to rate this professor!
            </p>
          ) : (
            ratings.map((rating, idx) => (
              <div key={idx} className="list-item" style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                  <span className={`rating ${getRatingClass(rating.rating)}`}>
                    ⭐ {rating.rating.toFixed(1)}
                  </span>
                  <span className="rating">
                    Difficulty: {rating.difficulty?.toFixed(1)}
                  </span>
                  {rating.would_take_again === 1 && (
                    <span className="rating high">Would take again</span>
                  )}
                </div>
                <p style={{ color: '#333', lineHeight: '1.6' }}>{rating.comment}</p>
                <div style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem' }}>
                  Posted on {new Date(rating.created_at).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfessorView;
