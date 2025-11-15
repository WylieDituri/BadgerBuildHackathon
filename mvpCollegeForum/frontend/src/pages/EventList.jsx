import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function EventList() {
  const { collegeId } = useParams();
  const [college, setCollege] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getCollege(collegeId),
      api.getEvents(collegeId)
    ])
      .then(([collegeRes, eventsRes]) => {
        setCollege(collegeRes.data);
        setEvents(eventsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [collegeId]);

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getEventTypeColor = (type) => {
    const colors = {
      'Career Fair': '#667eea',
      'Hackathon': '#f093fb',
      'Talk': '#4facfe',
      'Workshop': '#43e97b',
      'Club Meeting': '#fa709a',
      'Networking': '#764ba2'
    };
    return colors[type] || '#667eea';
  };

  if (loading) return <div className="loading">Loading events...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / <Link to={`/college/${collegeId}`}>{college?.name}</Link> / Events
      </div>
      <h1 className="page-title">Upcoming Events at {college?.name}</h1>
      
      {events.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
          No upcoming events found.
        </div>
      ) : (
        <div>
          {events.map(event => (
            <div key={event.id} className="event-card">
              <span 
                className="event-type" 
                style={{ background: getEventTypeColor(event.event_type) }}
              >
                {event.event_type}
              </span>
              <h2 style={{ fontSize: '1.5rem', color: '#333', margin: '0.5rem 0' }}>
                {event.title}
              </h2>
              <p style={{ color: '#666', lineHeight: '1.6', margin: '0.5rem 0' }}>
                {event.description}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.85rem', color: '#888' }}>📅 Date & Time</div>
                  <div style={{ color: '#333', fontWeight: '500' }}>
                    {formatDateTime(event.start_time)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', color: '#888' }}>📍 Location</div>
                  <div style={{ color: '#333', fontWeight: '500' }}>{event.location}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', color: '#888' }}>👥 Organizer</div>
                  <div style={{ color: '#333', fontWeight: '500' }}>{event.organizer}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EventList;
