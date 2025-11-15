/**
 * Simple in-memory storage for hackathon demo.
 * No Firebase needed - data is stored in backend memory.
 * 
 * For production, you could replace this with Firebase or another database.
 */

// Mock storage interface (data lives in backend memory)
export const storage = {
  // All data is stored in the backend's memory_store
  // Frontend just calls API endpoints
  getBackendUrl: () => process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
};

// Legacy exports for compatibility (if any components still reference these)
export const auth = null;
export const db = null;
