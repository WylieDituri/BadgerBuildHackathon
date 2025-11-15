import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function ClassView() {
  const { classId } = useParams();
  const [classData, setClassData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [grades, setGrades] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [newPost, setNewPost] = useState({ title: '', content: '', author: '' });
  const [newComment, setNewComment] = useState({ content: '', author: '' });

  useEffect(() => {
    Promise.all([
      api.getClass(classId),
      api.getForumPosts(classId),
      api.getClassGrades(classId)
    ])
      .then(([classRes, postsRes, gradesRes]) => {
        setClassData(classRes.data);
        setPosts(postsRes.data);
        setGrades(gradesRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setLoading(false);
      });
  }, [classId]);

  const loadComments = (postId) => {
    api.getComments(postId)
      .then(res => {
        setComments(res.data);
        setSelectedPost(postId);
      })
      .catch(err => console.error('Error fetching comments:', err));
  };

  const handleCreatePost = (e) => {
    e.preventDefault();
    api.createForumPost(classId, newPost)
      .then(() => {
        return api.getForumPosts(classId);
      })
      .then(res => {
        setPosts(res.data);
        setNewPost({ title: '', content: '', author: '' });
      })
      .catch(err => console.error('Error creating post:', err));
  };

  const handleAddComment = (e) => {
    e.preventDefault();
    api.addComment(selectedPost, newComment)
      .then(() => {
        return api.getComments(selectedPost);
      })
      .then(res => {
        setComments(res.data);
        setNewComment({ content: '', author: '' });
      })
      .catch(err => console.error('Error adding comment:', err));
  };

  const getRatingClass = (percent) => {
    if (percent >= 30) return 'high';
    if (percent >= 20) return 'medium';
    return 'low';
  };

  if (loading) return <div className="loading">Loading class data...</div>;

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Colleges</Link> / <Link to={`/major/${classData?.major_id}`}>Major</Link> / {classData?.code}
      </div>
      
      <div className="section">
        <h1 className="page-title">{classData?.code}: {classData?.name}</h1>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>{classData?.description}</p>
        <div style={{ marginTop: '1rem', color: '#888' }}>
          📚 {classData?.credits} credits
        </div>
      </div>

      {/* Grade Distributions */}
      {grades.length > 0 && (
        <div className="section">
          <h2 className="section-title">📊 Grade Distributions</h2>
          {grades.map((grade, idx) => (
            <div key={idx} style={{ marginBottom: '2rem' }}>
              <h3 style={{ color: '#667eea', marginBottom: '1rem' }}>
                {grade.professor_name} - {grade.semester}
              </h3>
              <div className="grade-chart">
                {['A', 'B', 'C', 'D', 'F'].map(letter => {
                  const percentage = grade[`${letter.toLowerCase()}_percentage`];
                  return (
                    <div key={letter} className="grade-bar">
                      <div className="grade-label">{letter}</div>
                      <div 
                        className="grade-bar-fill" 
                        style={{ width: `${percentage * 3}px` }}
                      />
                      <div className="grade-percentage">{percentage?.toFixed(1)}%</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Forum Section */}
      <div className="section">
        <h2 className="section-title">💬 Class Forum</h2>
        
        <form onSubmit={handleCreatePost} style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Create New Post</h3>
          <div className="form-group">
            <label>Your Name</label>
            <input
              type="text"
              value={newPost.author}
              onChange={(e) => setNewPost({ ...newPost, author: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Content</label>
            <textarea
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              required
            />
          </div>
          <button type="submit">Post</button>
        </form>

        <h3 style={{ marginBottom: '1rem' }}>Recent Discussions</h3>
        {posts.map(post => (
          <div key={post.id} className="list-item" style={{ cursor: 'pointer' }} onClick={() => loadComments(post.id)}>
            <h3 style={{ color: '#333', marginBottom: '0.5rem' }}>{post.title}</h3>
            <p style={{ color: '#666', marginBottom: '0.5rem' }}>{post.content}</p>
            <div style={{ fontSize: '0.85rem', color: '#888' }}>
              Posted by {post.author} on {new Date(post.created_at).toLocaleDateString()}
            </div>
            
            {selectedPost === post.id && (
              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #eee' }}>
                <h4 style={{ marginBottom: '1rem' }}>Comments</h4>
                {comments.map(comment => (
                  <div key={comment.id} style={{ background: '#f9f9f9', padding: '0.75rem', borderRadius: '6px', marginBottom: '0.5rem' }}>
                    <p style={{ color: '#333' }}>{comment.content}</p>
                    <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '0.5rem' }}>
                      {comment.author} - {new Date(comment.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
                
                <form onSubmit={handleAddComment} style={{ marginTop: '1rem' }}>
                  <div className="form-group">
                    <input
                      type="text"
                      placeholder="Your name"
                      value={newComment.author}
                      onChange={(e) => setNewComment({ ...newComment, author: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <textarea
                      placeholder="Add a comment..."
                      value={newComment.content}
                      onChange={(e) => setNewComment({ ...newComment, content: e.target.value })}
                      required
                    />
                  </div>
                  <button type="submit">Add Comment</button>
                </form>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ClassView;
