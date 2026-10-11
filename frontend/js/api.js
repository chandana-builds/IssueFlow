/**
 * IssueFlow — API Client Wrapper
 * Handles JWT storage, headers, error responses, and REST endpoints.
 */

const API_BASE = '';

const API = {
  TOKEN_KEY: 'issueflow_token',
  USER_KEY: 'issueflow_user',

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  setAuth(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  },

  getCurrentUser() {
    const raw = localStorage.getItem(this.USER_KEY);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Token expired or invalid
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth:expired'));
      }

      const contentType = response.headers.get('content-type') || '';
      let data = null;
      if (contentType.includes('application/json')) {
        data = await response.json();
      }

      if (!response.ok) {
        const errorMsg = data?.detail || `Request failed with status ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err.message);
      throw err;
    }
  },

  // Auth Endpoints
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  async login(emailOrUsername, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email_or_username: emailOrUsername, password })
    });
    this.setAuth(data.access_token, data.user);
    return data;
  },

  async getMe() {
    return this.request('/api/auth/me');
  },

  async getUsers() {
    return this.request('/api/auth/users');
  },

  // Dashboard Endpoint
  async getDashboardStats() {
    return this.request('/api/dashboard/stats');
  },

  // Issues Endpoints
  async getIssues(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '' && v !== 'ALL') {
        query.append(k, v);
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/api/issues${qs}`);
  },

  async getIssue(id) {
    return this.request(`/api/issues/${id}`);
  },

  async createIssue(issueData) {
    return this.request('/api/issues', {
      method: 'POST',
      body: JSON.stringify(issueData)
    });
  },

  async updateIssue(id, issueData) {
    return this.request(`/api/issues/${id}`, {
      method: 'PUT',
      body: JSON.stringify(issueData)
    });
  },

  async updateIssueStatus(id, status) {
    return this.request(`/api/issues/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  },

  async assignIssue(id, assigneeId) {
    return this.request(`/api/issues/${id}/assign`, {
      method: 'PATCH',
      body: JSON.stringify({ assignee_id: assigneeId })
    });
  },

  async deleteIssue(id) {
    return this.request(`/api/issues/${id}`, {
      method: 'DELETE'
    });
  },

  // Comments Endpoints
  async addComment(issueId, content) {
    return this.request(`/api/issues/${issueId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
  },

  async deleteComment(commentId) {
    return this.request(`/api/comments/${commentId}`, {
      method: 'DELETE'
    });
  },

  // Activities
  async getIssueActivities(issueId) {
    return this.request(`/api/issues/${issueId}/activities`);
  },

  async getRecentActivities(limit = 10) {
    return this.request(`/api/activities/recent?limit=${limit}`);
  }
};
