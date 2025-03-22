const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  documents: `${API_BASE_URL}/api/documents`,
  auth: `${API_BASE_URL}/api/auth`,
  search: `${API_BASE_URL}/api/documents/search`,
  upload: `${API_BASE_URL}/api/documents/upload`,
  batchUpload: `${API_BASE_URL}/api/documents/batch-upload`,
  analyze: (id) => `${API_BASE_URL}/api/documents/${id}/analyze`,
  extractReferences: (id) => `${API_BASE_URL}/api/documents/${id}/extract-references`,
  suggestClassifications: (id) => `${API_BASE_URL}/api/documents/${id}/suggest-classifications`,
  // Admin endpoints
  admin: {
    stats: `${API_BASE_URL}/admin/stats`,
    pendingDocuments: `${API_BASE_URL}/admin/pending-documents`,
    approveDocument: (id) => `${API_BASE_URL}/admin/documents/${id}/approve`,
    upload: `${API_BASE_URL}/admin/upload`
  },
  // Resource endpoints
  resources: {
    madhabs: `${API_BASE_URL}/api/madhabs`,
    categories: `${API_BASE_URL}/api/categories`
  }
};

export default API_ENDPOINTS;