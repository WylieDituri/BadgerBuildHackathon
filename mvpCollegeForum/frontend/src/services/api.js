import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export const api = {
  // Colleges
  getColleges: () => axios.get(`${API_BASE_URL}/colleges`),
  getCollege: (id) => axios.get(`${API_BASE_URL}/colleges/${id}`),

  // Majors
  getMajorsByCollege: (collegeId) => axios.get(`${API_BASE_URL}/colleges/${collegeId}/majors`),
  getMajor: (id) => axios.get(`${API_BASE_URL}/majors/${id}`),

  // Classes
  getClassesByMajor: (majorId) => axios.get(`${API_BASE_URL}/majors/${majorId}/classes`),
  getClass: (id) => axios.get(`${API_BASE_URL}/classes/${id}`),
  getClassGrades: (classId) => axios.get(`${API_BASE_URL}/classes/${classId}/grades`),

  // Professors
  getProfessorsByCollege: (collegeId) => axios.get(`${API_BASE_URL}/colleges/${collegeId}/professors`),
  getProfessor: (id) => axios.get(`${API_BASE_URL}/professors/${id}`),
  getProfessorRatings: (professorId) => axios.get(`${API_BASE_URL}/professors/${professorId}/ratings`),
  getProfessorSummary: (professorId) => axios.get(`${API_BASE_URL}/professors/${professorId}/rating-summary`),
  addProfessorRating: (professorId, data) => axios.post(`${API_BASE_URL}/professors/${professorId}/ratings`, data),

  // Forum
  getForumPosts: (classId) => axios.get(`${API_BASE_URL}/classes/${classId}/posts`),
  createForumPost: (classId, data) => axios.post(`${API_BASE_URL}/classes/${classId}/posts`, data),
  getComments: (postId) => axios.get(`${API_BASE_URL}/posts/${postId}/comments`),
  addComment: (postId, data) => axios.post(`${API_BASE_URL}/posts/${postId}/comments`, data),

  // Events
  getEvents: (collegeId, majorId) => axios.get(`${API_BASE_URL}/colleges/${collegeId}/events`, {
    params: { major_id: majorId }
  }),
  createEvent: (collegeId, data) => axios.post(`${API_BASE_URL}/colleges/${collegeId}/events`, data),

  // AI Recommendations
  getRecommendations: (majorId) => axios.get(`${API_BASE_URL}/majors/${majorId}/recommendations`)
};
