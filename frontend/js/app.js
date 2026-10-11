/**
 * IssueFlow — Core Client Application Logic
 * State management, views routing, Kanban drag & drop, charts, and modal interactions.
 */

const App = {
  state: {
    currentUser: null,
    users: [],
    issues: [],
    activeView: 'dashboard',
    selectedIssue: null,
    filters: {
      search: '',
      status: 'ALL',
      priority: 'ALL',
      type: 'ALL',
      assignee_id: 'ALL'
    }
  },

  async init() {
    this.bindEvents();

    // Check if authenticated, otherwise log in as demo lead by default for seamless out-of-the-box demo
    const storedUser = API.getCurrentUser();
    if (storedUser && API.getToken()) {
      this.state.currentUser = storedUser;
    } else {
      try {
        const loginData = await API.login('admin@issueflow.dev', 'admin123');
        this.state.currentUser = loginData.user;
      } catch (e) {
        console.warn('Demo login failed, falling back:', e);
      }
    }

    this.updateUserUI();
    await this.loadUsers();
    await this.refreshAllData();
  },

  bindEvents() {
    // Navigation items
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const view = item.getAttribute('data-view');
        if (view) {
          e.preventDefault();
          this.switchView(view);
        }
      });
    });

    // Mobile nav toggle
    const mobileBtn = document.getElementById('mobile-toggle');
    const sidebar = document.getElementById('sidebar');
    if (mobileBtn && sidebar) {
      mobileBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }

    // Global Search
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      let timeout = null;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.state.filters.search = e.target.value;
          this.renderIssues();
          this.renderKanban();
        }, 200);
      });
    }

    // Hotkeys
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput && !this.isModalOpen()) {
        e.preventDefault();
        searchInput?.focus();
      }
      if (e.key === 'Escape') {
        this.closeAllModals();
      }
    });

    // User profile menu
    const userBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');
    if (userBtn && userDropdown) {
      userBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('show');
      });
      window.addEventListener('click', () => {
        userDropdown.classList.remove('show');
      });
    }

    // Switch Account & Logout
    document.getElementById('btn-quick-login')?.addEventListener('click', () => {
      this.openModal('modal-auth');
    });

    document.getElementById('btn-logout')?.addEventListener('click', () => {
      API.clearAuth();
      this.state.currentUser = null;
      this.showToast('Signed out successfully', 'info');
      this.openModal('modal-auth');
    });

    // Demo Switcher buttons
    document.getElementById('btn-demo-admin')?.addEventListener('click', async () => {
      await this.performLogin('admin@issueflow.dev', 'admin123');
    });
    document.getElementById('btn-demo-alex')?.addEventListener('click', async () => {
      await this.performLogin('alex@issueflow.dev', 'dev12345');
    });
    document.getElementById('btn-demo-priya')?.addEventListener('click', async () => {
      await this.performLogin('priya@issueflow.dev', 'qa123456');
    });

    // Auth Login Form
    document.getElementById('form-auth-login')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const pw = document.getElementById('login-password').value;
      await this.performLogin(email, pw);
    });

    // New Issue Button & Form
    document.getElementById('btn-create-issue')?.addEventListener('click', () => {
      this.openCreateIssueModal();
    });

    document.getElementById('form-create-issue')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.handleSaveIssue();
    });

    // Refresh Dashboard Button
    document.getElementById('btn-refresh-dashboard')?.addEventListener('click', async () => {
      await this.loadDashboard();
      this.showToast('Dashboard metrics refreshed', 'info');
    });

    // Filters on Issues Table
    ['filter-status', 'filter-priority', 'filter-type', 'filter-assignee'].forEach(id => {
      document.getElementById(id)?.addEventListener('change', (e) => {
        const field = id.replace('filter-', '');
        this.state.filters[field === 'assignee' ? 'assignee_id' : field] = e.target.value;
        this.renderIssues();
      });
    });

    document.getElementById('btn-clear-filters')?.addEventListener('click', () => {
      ['filter-status', 'filter-priority', 'filter-type', 'filter-assignee'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = 'ALL';
      });
      this.state.filters = { search: '', status: 'ALL', priority: 'ALL', type: 'ALL', assignee_id: 'ALL' };
      if (searchInput) searchInput.value = '';
      this.renderIssues();
      this.renderKanban();
    });

    // Kanban Board quick filters
    document.getElementById('btn-board-filter-my')?.addEventListener('click', () => {
      if (this.state.currentUser) {
        this.state.filters.assignee_id = this.state.currentUser.id;
        this.renderKanban();
        this.showToast(`Filtered by ${this.state.currentUser.full_name}`, 'info');
      }
    });

    document.getElementById('btn-board-filter-all')?.addEventListener('click', () => {
      this.state.filters.assignee_id = 'ALL';
      this.renderKanban();
    });

    // Export CSV
    document.getElementById('btn-export-csv')?.addEventListener('click', () => {
      this.exportIssuesCSV();
    });

    // Modal Close Buttons
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.closeAllModals();
      });
    });

    // Close modal on background click
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.closeAllModals();
        }
      });
    });

    // Detail Drawer: Tabs
    document.getElementById('tab-comments-btn')?.addEventListener('click', () => {
      this.switchDetailTab('comments');
    });
    document.getElementById('tab-activities-btn')?.addEventListener('click', () => {
      this.switchDetailTab('activities');
    });

    // Detail Drawer: Add Comment
    document.getElementById('form-add-comment')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.handleAddComment();
    });

    // Detail Drawer: Inline Selectors (Status, Priority, Assignee)
    document.getElementById('detail-status-select')?.addEventListener('change', async (e) => {
      if (this.state.selectedIssue) {
        await this.handleUpdateIssueField(this.state.selectedIssue.id, { status: e.target.value });
      }
    });

    document.getElementById('detail-priority-select')?.addEventListener('change', async (e) => {
      if (this.state.selectedIssue) {
        await this.handleUpdateIssueField(this.state.selectedIssue.id, { priority: e.target.value });
      }
    });

    document.getElementById('detail-assignee-select')?.addEventListener('change', async (e) => {
      if (this.state.selectedIssue) {
        const val = e.target.value ? parseInt(e.target.value) : null;
        await this.handleUpdateIssueField(this.state.selectedIssue.id, { assignee_id: val });
      }
    });

    // Detail Drawer: Edit and Delete Buttons
    document.getElementById('btn-edit-current-issue')?.addEventListener('click', () => {
      if (this.state.selectedIssue) {
        this.openEditIssueModal(this.state.selectedIssue);
      }
    });

    document.getElementById('btn-delete-current-issue')?.addEventListener('click', async () => {
      if (this.state.selectedIssue && confirm(`Are you sure you want to delete ${this.state.selectedIssue.issue_key}?`)) {
        try {
          await API.deleteIssue(this.state.selectedIssue.id);
          this.showToast(`Issue ${this.state.selectedIssue.issue_key} deleted`, 'success');
          this.closeAllModals();
          await this.refreshAllData();
        } catch (err) {
          this.showToast(err.message, 'error');
        }
      }
    });

    // Kanban Drag & Drop setup
    this.initKanbanDragDrop();
  },

  async performLogin(emailOrUsername, password) {
    try {
      const data = await API.login(emailOrUsername, password);
      this.state.currentUser = data.user;
      this.updateUserUI();
      this.closeAllModals();
      this.showToast(`Signed in as ${data.user.full_name}`, 'success');
      await this.refreshAllData();
    } catch (err) {
      this.showToast(err.message || 'Login failed', 'error');
    }
  },

  updateUserUI() {
    const user = this.state.currentUser;
    const nameEl = document.getElementById('header-username');
    const avatarEl = document.getElementById('header-avatar');
    if (user && nameEl && avatarEl) {
      nameEl.textContent = user.full_name;
      const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      avatarEl.textContent = initials;
      avatarEl.style.backgroundColor = user.avatar_color || '#6366f1';
    }
  },

  switchView(viewName) {
    this.state.activeView = viewName;
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-view') === viewName);
    });

    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const targetSec = document.getElementById(`view-${viewName}`);
    if (targetSec) {
      targetSec.classList.add('active');
    }

    if (viewName === 'dashboard') this.loadDashboard();
    if (viewName === 'board') this.renderKanban();
    if (viewName === 'issues') this.renderIssues();
    if (viewName === 'team') this.renderTeam();
  },

  async loadUsers() {
    try {
      this.state.users = await API.getUsers();
      this.populateUserDropdowns();
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  },

  populateUserDropdowns() {
    const selects = [
      document.getElementById('issue-assignee'),
      document.getElementById('filter-assignee'),
      document.getElementById('detail-assignee-select')
    ];

    selects.forEach(select => {
      if (!select) return;
      const currentVal = select.value;
      const isFilter = select.id === 'filter-assignee';
      
      select.innerHTML = isFilter 
        ? '<option value="ALL">Assignee: All</option><option value="-1">Unassigned</option>'
        : '<option value="">Unassigned</option>';

      this.state.users.forEach(u => {
        const opt = document.createElement('option');
        opt.value = u.id;
        opt.textContent = `${u.full_name} (${u.role})`;
        select.appendChild(opt);
      });

      if (currentVal) select.value = currentVal;
    });
  },

  async refreshAllData() {
    try {
      const issuesRes = await API.getIssues({ page_size: 100 });
      this.state.issues = issuesRes.items || [];
      await this.loadDashboard();
      this.renderKanban();
      this.renderIssues();
      this.renderTeam();
    } catch (err) {
      console.error('Failed to refresh data:', err);
    }
  },

  // --------------------------------------------------------------------------
  // Dashboard Metrics & Charts
  // --------------------------------------------------------------------------
  async loadDashboard() {
    try {
      const stats = await API.getDashboardStats();

      // Update KPI Counter Cards
      this.animateCounter('kpi-total', stats.total_issues);
      this.animateCounter('kpi-open', stats.open_issues);
      this.animateCounter('kpi-progress', stats.in_progress_issues);
      document.getElementById('kpi-resolution').textContent = `${stats.resolution_rate_percent}%`;
      document.getElementById('kpi-resolved-count').textContent = `${stats.resolved_issues + stats.closed_issues} resolved / closed`;
      this.animateCounter('kpi-overdue', stats.overdue_issues);

      // Render Donut Chart
      this.renderDonutChart(stats.status_counts, stats.total_issues);

      // Render Priority Bars
      this.renderPriorityBars(stats.priority_counts, stats.total_issues);

      // Render Activity Stream
      this.renderDashboardActivities(stats.recent_activities || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  },

  animateCounter(id, targetVal) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = targetVal;
  },

  renderDonutChart(counts, total) {
    const circumference = 2 * Math.PI * 36; // 226.19
    let accumulatedOffset = 0;

    const segments = [
      { id: 'donut-open', count: counts.OPEN || 0, color: '#10b981' },
      { id: 'donut-progress', count: counts.IN_PROGRESS || 0, color: '#f59e0b' },
      { id: 'donut-resolved', count: counts.RESOLVED || 0, color: '#6366f1' },
      { id: 'donut-closed', count: counts.CLOSED || 0, color: '#64748b' }
    ];

    segments.forEach(seg => {
      const circle = document.getElementById(seg.id);
      if (!circle) return;

      const fraction = total > 0 ? seg.count / total : 0;
      const length = fraction * circumference;
      circle.style.strokeDasharray = `${length} ${circumference - length}`;
      circle.style.strokeDashoffset = -accumulatedOffset;
      accumulatedOffset += length;
    });

    // Update legend counters
    document.getElementById('legend-count-open').textContent = counts.OPEN || 0;
    document.getElementById('legend-count-progress').textContent = counts.IN_PROGRESS || 0;
    document.getElementById('legend-count-resolved').textContent = counts.RESOLVED || 0;
    document.getElementById('legend-count-closed').textContent = counts.CLOSED || 0;
  },

  renderPriorityBars(counts, total) {
    const container = document.getElementById('priority-bars-container');
    if (!container) return;

    const priorities = [
      { key: 'CRITICAL', label: 'Critical Priority', color: 'var(--prio-critical)' },
      { key: 'HIGH', label: 'High Priority', color: 'var(--prio-high)' },
      { key: 'MEDIUM', label: 'Medium Priority', color: 'var(--prio-medium)' },
      { key: 'LOW', label: 'Low Priority', color: 'var(--prio-low)' }
    ];

    container.innerHTML = priorities.map(p => {
      const count = counts[p.key] || 0;
      const pct = total > 0 ? Math.round((count / total) * 100) : 0;
      return `
        <div class="bar-row">
          <div class="bar-header">
            <span>${p.label}</span>
            <span><strong>${count}</strong> (${pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%; background: ${p.color};"></div>
          </div>
        </div>
      `;
    }).join('');
  },

  renderDashboardActivities(activities) {
    const container = document.getElementById('dashboard-activity-feed');
    if (!container) return;

    if (!activities.length) {
      container.innerHTML = `<div style="color:var(--text-dim); text-align:center; padding:1.5rem;">No recent activities logged yet.</div>`;
      return;
    }

    container.innerHTML = activities.map(act => {
      const timeStr = this.formatDate(act.created_at);
      return `
        <div class="activity-item">
          <div class="activity-dot"></div>
          <div class="activity-content">
            <div class="activity-text">${this.escapeHtml(act.description)}</div>
            <div class="activity-time">${timeStr}</div>
          </div>
        </div>
      `;
    }).join('');
  },

  // --------------------------------------------------------------------------
  // Kanban Board Logic
  // --------------------------------------------------------------------------
  renderKanban() {
    const statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'];
    const filtered = this.getFilteredIssues();

    statuses.forEach(st => {
      const container = document.getElementById(`cards-${st.toLowerCase()}`);
      const countEl = document.getElementById(`count-${st.toLowerCase()}`);
      if (!container) return;

      const columnIssues = filtered.filter(i => i.status === st);
      if (countEl) countEl.textContent = columnIssues.length;

      container.innerHTML = columnIssues.map(issue => this.createKanbanCardHtml(issue)).join('');

      // Add click listeners to cards
      container.querySelectorAll('.kanban-card').forEach(card => {
        card.addEventListener('click', () => {
          const issueId = parseInt(card.getAttribute('data-id'));
          this.openIssueDetail(issueId);
        });
      });
    });
  },

  createKanbanCardHtml(issue) {
    const typeBadge = `<span class="badge badge-${issue.issue_type.toLowerCase()}">${issue.issue_type}</span>`;
    const prioBadge = `<span class="badge badge-${issue.priority.toLowerCase()}">${issue.priority}</span>`;
    const tagsHtml = issue.tags 
      ? issue.tags.split(',').map(t => `<span class="tag-badge">#${t.trim()}</span>`).join('') 
      : '';
    const assigneeInitial = issue.assignee 
      ? issue.assignee.full_name.split(' ').map(n=>n[0]).join('').substring(0,2)
      : '?';
    const assigneeColor = issue.assignee ? issue.assignee.avatar_color : '#475569';
    const assigneeTitle = issue.assignee ? issue.assignee.full_name : 'Unassigned';

    return `
      <div class="kanban-card" draggable="true" data-id="${issue.id}">
        <div class="card-top">
          <span class="issue-key">${issue.issue_key}</span>
          ${prioBadge}
        </div>
        <div class="card-title-text">${this.escapeHtml(issue.title)}</div>
        <div class="card-tags">${tagsHtml}</div>
        <div class="card-meta">
          ${typeBadge}
          <div style="display:flex; align-items:center; gap:0.4rem;">
            ${issue.comments_count > 0 ? `<span style="font-size:0.75rem; color:var(--text-dim);">💬 ${issue.comments_count}</span>` : ''}
            <div class="user-avatar" style="width:24px; height:24px; background:${assigneeColor}; font-size:0.7rem;" title="${assigneeTitle}">
              ${assigneeInitial}
            </div>
          </div>
        </div>
      </div>
    `;
  },

  initKanbanDragDrop() {
    let draggedId = null;

    document.addEventListener('dragstart', (e) => {
      const card = e.target.closest('.kanban-card');
      if (card) {
        draggedId = card.getAttribute('data-id');
        card.classList.add('dragging');
        e.dataTransfer.setData('text/plain', draggedId);
        e.dataTransfer.effectAllowed = 'move';
      }
    });

    document.addEventListener('dragend', (e) => {
      const card = e.target.closest('.kanban-card');
      if (card) {
        card.classList.remove('dragging');
      }
    });

    document.querySelectorAll('.board-column').forEach(col => {
      col.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        col.style.background = 'rgba(99, 102, 241, 0.08)';
      });

      col.addEventListener('dragleave', () => {
        col.style.background = '';
      });

      col.addEventListener('drop', async (e) => {
        e.preventDefault();
        col.style.background = '';
        const targetStatus = col.getAttribute('data-status');
        const issueId = parseInt(e.dataTransfer.getData('text/plain'));

        if (issueId && targetStatus) {
          const issue = this.state.issues.find(i => i.id === issueId);
          if (issue && issue.status !== targetStatus) {
            try {
              await API.updateIssueStatus(issueId, targetStatus);
              issue.status = targetStatus;
              this.renderKanban();
              await this.loadDashboard();
              this.showToast(`${issue.issue_key} transitioned to ${targetStatus}`, 'success');
            } catch (err) {
              this.showToast(err.message, 'error');
            }
          }
        }
      });
    });
  },

  // --------------------------------------------------------------------------
  // Issues Table View
  // --------------------------------------------------------------------------
  renderIssues() {
    const tbody = document.getElementById('issues-table-body');
    if (!tbody) return;

    const filtered = this.getFilteredIssues();

    if (!filtered.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align:center; padding:2rem; color:var(--text-dim);">
            No issues match current filters.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = filtered.map(issue => {
      const statusBadge = `<span class="badge badge-${issue.status.toLowerCase()}">${issue.status}</span>`;
      const prioBadge = `<span class="badge badge-${issue.priority.toLowerCase()}">${issue.priority}</span>`;
      const typeBadge = `<span class="badge badge-${issue.issue_type.toLowerCase()}">${issue.issue_type}</span>`;
      const assigneeName = issue.assignee ? issue.assignee.full_name : '<span style="color:var(--text-dim)">Unassigned</span>';
      const reporterName = issue.reporter ? issue.reporter.full_name : '-';
      const createdStr = this.formatDate(issue.created_at);

      return `
        <tr data-id="${issue.id}">
          <td class="issue-key">${issue.issue_key}</td>
          <td style="font-weight:600; color:var(--text-main);">${this.escapeHtml(issue.title)}</td>
          <td>${statusBadge}</td>
          <td>${prioBadge}</td>
          <td>${typeBadge}</td>
          <td>${assigneeName}</td>
          <td>${reporterName}</td>
          <td style="color:var(--text-dim); font-size:0.8rem;">${createdStr}</td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('tr').forEach(row => {
      row.addEventListener('click', () => {
        const id = parseInt(row.getAttribute('data-id'));
        if (id) this.openIssueDetail(id);
      });
    });
  },

  getFilteredIssues() {
    return this.state.issues.filter(issue => {
      const f = this.state.filters;

      // Search
      if (f.search) {
        const term = f.search.toLowerCase();
        const inTitle = issue.title.toLowerCase().includes(term);
        const inKey = issue.issue_key.toLowerCase().includes(term);
        const inDesc = (issue.description || '').toLowerCase().includes(term);
        const inTags = (issue.tags || '').toLowerCase().includes(term);
        if (!inTitle && !inKey && !inDesc && !inTags) return false;
      }

      // Status
      if (f.status !== 'ALL' && issue.status !== f.status) return false;

      // Priority
      if (f.priority !== 'ALL' && issue.priority !== f.priority) return false;

      // Type
      if (f.type !== 'ALL' && issue.issue_type !== f.type) return false;

      // Assignee
      if (f.assignee_id !== 'ALL') {
        if (f.assignee_id === '-1') {
          if (issue.assignee_id !== null) return false;
        } else if (issue.assignee_id !== parseInt(f.assignee_id)) {
          return false;
        }
      }

      return true;
    });
  },

  // --------------------------------------------------------------------------
  // Team Directory View
  // --------------------------------------------------------------------------
  renderTeam() {
    const container = document.getElementById('team-cards-grid');
    if (!container) return;

    container.innerHTML = this.state.users.map(user => {
      const assignedCount = this.state.issues.filter(i => i.assignee_id === user.id && !['RESOLVED', 'CLOSED'].includes(i.status)).length;
      const reportedCount = this.state.issues.filter(i => i.reporter_id === user.id).length;
      const initials = user.full_name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();

      return `
        <div class="kpi-card" style="padding:1.5rem;">
          <div style="display:flex; align-items:center; gap:0.85rem; margin-bottom:1rem;">
            <div class="user-avatar" style="width:44px; height:44px; background:${user.avatar_color || '#6366f1'}; font-size:1rem; font-weight:700;">
              ${initials}
            </div>
            <div>
              <div style="font-weight:700; font-size:1rem;">${this.escapeHtml(user.full_name)}</div>
              <div style="font-size:0.8rem; color:var(--text-muted); text-transform:capitalize;">${user.role} &bull; @${user.username}</div>
            </div>
          </div>
          <div style="display:flex; justify-content:space-between; border-top:1px solid var(--border-color); padding-top:0.75rem; font-size:0.85rem;">
            <div>
              <div style="color:var(--text-dim); font-size:0.75rem;">Active Assigned</div>
              <div style="font-weight:700; color:#818cf8; font-size:1.15rem;">${assignedCount}</div>
            </div>
            <div>
              <div style="color:var(--text-dim); font-size:0.75rem;">Reported</div>
              <div style="font-weight:700; color:var(--text-main); font-size:1.15rem;">${reportedCount}</div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  // --------------------------------------------------------------------------
  // Issue Detail Drawer
  // --------------------------------------------------------------------------
  async openIssueDetail(issueId) {
    try {
      const issue = await API.getIssue(issueId);
      this.state.selectedIssue = issue;

      document.getElementById('detail-key').textContent = issue.issue_key;
      document.getElementById('detail-title').textContent = issue.title;
      document.getElementById('detail-description').textContent = issue.description || 'No description provided.';
      
      document.getElementById('detail-status-select').value = issue.status;
      document.getElementById('detail-priority-select').value = issue.priority;
      document.getElementById('detail-assignee-select').value = issue.assignee_id || '';
      
      const typeBadge = document.getElementById('detail-type-badge');
      typeBadge.className = `badge badge-${issue.issue_type.toLowerCase()}`;
      typeBadge.textContent = issue.issue_type;

      document.getElementById('detail-reporter-name').textContent = issue.reporter ? issue.reporter.full_name : 'Unknown';
      document.getElementById('detail-created-at').textContent = this.formatDate(issue.created_at);

      // Tags
      const tagsBox = document.getElementById('detail-tags-list');
      tagsBox.innerHTML = issue.tags 
        ? issue.tags.split(',').map(t => `<span class="tag-badge">#${t.trim()}</span>`).join('') 
        : '<span style="color:var(--text-dim); font-size:0.75rem;">No tags</span>';

      // Comments & Activity counts
      document.getElementById('detail-comments-count').textContent = issue.comments?.length || 0;
      document.getElementById('detail-activities-count').textContent = issue.activities?.length || 0;

      this.renderDetailComments(issue.comments || []);
      this.renderDetailActivities(issue.activities || []);

      this.switchDetailTab('comments');
      this.openModal('modal-issue-detail');
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  renderDetailComments(comments) {
    const list = document.getElementById('detail-comments-list');
    if (!list) return;

    if (!comments.length) {
      list.innerHTML = `<div style="color:var(--text-dim); text-align:center; padding:1rem; font-size:0.85rem;">No comments yet. Start the discussion below.</div>`;
      return;
    }

    list.innerHTML = comments.map(c => {
      const authorName = c.author ? c.author.full_name : 'Unknown';
      const initials = authorName.split(' ').map(n=>n[0]).join('').substring(0,2);
      const avatarColor = c.author ? c.author.avatar_color : '#6366f1';
      const canDelete = this.state.currentUser && (this.state.currentUser.id === c.author_id || this.state.currentUser.role === 'admin');

      return `
        <div class="comment-bubble">
          <div class="comment-header">
            <div class="comment-author">
              <div class="user-avatar" style="width:22px; height:22px; background:${avatarColor}; font-size:0.65rem;">${initials}</div>
              ${this.escapeHtml(authorName)}
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span style="font-size:0.725rem; color:var(--text-dim);">${this.formatDate(c.created_at)}</span>
              ${canDelete ? `<button onclick="App.handleDeleteComment(${c.id})" style="background:none; border:none; color:#f87171; cursor:pointer; font-size:0.75rem;">&times;</button>` : ''}
            </div>
          </div>
          <div class="comment-body">${this.escapeHtml(c.content)}</div>
        </div>
      `;
    }).join('');
  },

  renderDetailActivities(activities) {
    const list = document.getElementById('detail-activities-list');
    if (!list) return;

    if (!activities.length) {
      list.innerHTML = `<div style="color:var(--text-dim); text-align:center; padding:1rem; font-size:0.85rem;">No audit logs recorded for this issue.</div>`;
      return;
    }

    list.innerHTML = activities.map(act => `
      <div class="activity-item">
        <div class="activity-dot"></div>
        <div class="activity-content">
          <div class="activity-text">${this.escapeHtml(act.description)}</div>
          <div class="activity-time">${this.formatDate(act.created_at)}</div>
        </div>
      </div>
    `).join('');
  },

  switchDetailTab(tabName) {
    document.getElementById('tab-comments-btn')?.classList.toggle('active', tabName === 'comments');
    document.getElementById('tab-activities-btn')?.classList.toggle('active', tabName === 'activities');
    
    document.getElementById('tab-content-comments').style.display = tabName === 'comments' ? 'block' : 'none';
    document.getElementById('tab-content-activities').style.display = tabName === 'activities' ? 'block' : 'none';
  },

  async handleAddComment() {
    const input = document.getElementById('comment-input');
    const content = input?.value.trim();
    if (!content || !this.state.selectedIssue) return;

    try {
      await API.addComment(this.state.selectedIssue.id, content);
      input.value = '';
      this.showToast('Comment posted', 'success');
      await this.openIssueDetail(this.state.selectedIssue.id);
      await this.refreshAllData();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  async handleDeleteComment(commentId) {
    if (!confirm('Delete this comment?')) return;
    try {
      await API.deleteComment(commentId);
      this.showToast('Comment deleted', 'info');
      if (this.state.selectedIssue) {
        await this.openIssueDetail(this.state.selectedIssue.id);
      }
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  async handleUpdateIssueField(issueId, fieldObj) {
    try {
      await API.updateIssue(issueId, fieldObj);
      this.showToast('Issue updated', 'success');
      await this.refreshAllData();
      if (this.state.selectedIssue && this.state.selectedIssue.id === issueId) {
        await this.openIssueDetail(issueId);
      }
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  // --------------------------------------------------------------------------
  // Issue Create / Edit Modal
  // --------------------------------------------------------------------------
  openCreateIssueModal() {
    document.getElementById('create-modal-title').textContent = 'Create New Issue';
    document.getElementById('edit-issue-id').value = '';
    document.getElementById('form-create-issue').reset();
    document.getElementById('issue-priority').value = 'MEDIUM';
    document.getElementById('issue-type').value = 'BUG';
    this.openModal('modal-create-issue');
  },

  openEditIssueModal(issue) {
    document.getElementById('create-modal-title').textContent = `Edit Issue: ${issue.issue_key}`;
    document.getElementById('edit-issue-id').value = issue.id;
    document.getElementById('issue-title').value = issue.title;
    document.getElementById('issue-type').value = issue.issue_type;
    document.getElementById('issue-priority').value = issue.priority;
    document.getElementById('issue-assignee').value = issue.assignee_id || '';
    document.getElementById('issue-tags').value = issue.tags || '';
    document.getElementById('issue-description').value = issue.description || '';
    this.closeModal('modal-issue-detail');
    this.openModal('modal-create-issue');
  },

  async handleSaveIssue() {
    const editId = document.getElementById('edit-issue-id').value;
    const title = document.getElementById('issue-title').value.trim();
    const issue_type = document.getElementById('issue-type').value;
    const priority = document.getElementById('issue-priority').value;
    const assigneeVal = document.getElementById('issue-assignee').value;
    const assignee_id = assigneeVal ? parseInt(assigneeVal) : null;
    const tags = document.getElementById('issue-tags').value.trim();
    const description = document.getElementById('issue-description').value.trim();

    const payload = { title, issue_type, priority, assignee_id, tags, description };

    try {
      if (editId) {
        await API.updateIssue(parseInt(editId), payload);
        this.showToast('Issue updated successfully', 'success');
      } else {
        const created = await API.createIssue(payload);
        this.showToast(`Issue ${created.issue_key} created`, 'success');
      }
      this.closeModal('modal-create-issue');
      await this.refreshAllData();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  // --------------------------------------------------------------------------
  // Export CSV
  // --------------------------------------------------------------------------
  exportIssuesCSV() {
    const filtered = this.getFilteredIssues();
    if (!filtered.length) {
      this.showToast('No issues to export', 'error');
      return;
    }

    const headers = ['Key', 'Title', 'Status', 'Priority', 'Type', 'Assignee', 'Reporter', 'Created'];
    const rows = filtered.map(i => [
      `"${i.issue_key}"`,
      `"${i.title.replace(/"/g, '""')}"`,
      `"${i.status}"`,
      `"${i.priority}"`,
      `"${i.issue_type}"`,
      `"${i.assignee ? i.assignee.full_name : 'Unassigned'}"`,
      `"${i.reporter ? i.reporter.full_name : ''}"`,
      `"${i.created_at}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `IssueFlow_Export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showToast(`Exported ${filtered.length} issues to CSV`, 'success');
  },

  // --------------------------------------------------------------------------
  // Modals & UI Helpers
  // --------------------------------------------------------------------------
  openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('show');
  },

  closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('show');
  },

  closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('show'));
  },

  isModalOpen() {
    return !!document.querySelector('.modal-overlay.show');
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✓' : type === 'error' ? '⚠' : 'ℹ';
    toast.innerHTML = `<span>${icon}</span> <span>${this.escapeHtml(message)}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(12px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  },

  formatDate(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  },

  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
};

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
