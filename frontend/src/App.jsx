import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = "https://kinship-dashboard-app.onrender.com";

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'grid' },
  { id: 'academic-reports', label: 'Academic Reports', icon: 'file-text' },
  { id: 'school-visits', label: 'School Visits', icon: 'map-pin' },
  { id: 'school-fees', label: 'School Fees', icon: 'credit-card' },
  { id: 'missing-aadhaar', label: 'Missing Aadhaar', icon: 'alert-circle' },
  { id: 'missing-profile', label: 'Missing Profile', icon: 'user-x' },
  { id: 'child-data', label: 'Child Data', icon: 'database' },
];

// ─── Icon component ──────────────────────────────────────────────────────────
function Icon({ name, size = 20 }) {
  const icons = {
    grid: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
    'file-text': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14,2 14,8 20,8" />
        <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10,9 9,9 8,9" />
      </svg>
    ),
    'map-pin': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
        <circle cx="12" cy="10" r="3" />
      </svg>
    ),
    'credit-card': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
        <line x1="1" y1="10" x2="23" y2="10" />
      </svg>
    ),
    'alert-circle': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
    ),
    'user-x': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8.5" cy="7" r="4" />
        <line x1="18" y1="8" x2="23" y2="13" /><line x1="23" y1="8" x2="18" y2="13" />
      </svg>
    ),
    users: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
    'check-circle': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22,4 12,14.01 9,11.01" />
      </svg>
    ),
    'chevron-down': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="6,9 12,15 18,9" />
      </svg>
    ),
    'chevron-left': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="15,18 9,12 15,6" />
      </svg>
    ),
    'chevron-right': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="9,18 15,12 9,6" />
      </svg>
    ),
    database: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
      </svg>
    ),
    'arrow-left': (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="19" y1="12" x2="5" y2="12" /><polyline points="12,19 5,12 12,5" />
      </svg>
    ),
  };
  return icons[name] || null;
}

// ─── Sidebar ─────────────────────────────────────────────────────────────────
function Sidebar({ activeItem, onSelect }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">K</span>
          <span className="logo-text">Kinship</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-item ${activeItem === item.id ? 'active' : ''}`}
            onClick={() => onSelect(item.id)}
          >
            <Icon name={item.icon} size={18} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">A</div>
          <div className="user-info">
            <span className="user-name">Admin</span>
            <span className="user-role">Administrator</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

// ─── Dropdown ────────────────────────────────────────────────────────────────
function Dropdown({ label, value, onChange, options, placeholder }) {
  return (
    <div className="dropdown-container">
      <label className="dropdown-label">{label}</label>
      <div className="dropdown-wrapper">
        <select className="dropdown-select" value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">{placeholder}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <Icon name="chevron-down" size={16} />
      </div>
    </div>
  );
}

// ─── KPICard ─────────────────────────────────────────────────────────────────
function KPICard({ title, value, icon, description, onClick, clickable }) {
  return (
    <div
      className="kpi-card"
      onClick={onClick}
      style={clickable ? { cursor: 'pointer' } : undefined}
    >
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        <div className="kpi-icon"><Icon name={icon} size={20} /></div>
      </div>
      <div className="kpi-value">{value}</div>
      {description && <p className="kpi-description">{description}</p>}
    </div>
  );
}

// ─── SummaryTable ────────────────────────────────────────────────────────────
function SummaryTable({ data }) {
  const rows = [
    { metric: 'Academic Reports', completed: data.academicCompleted ?? 0, pending: data.academicPending ?? 0 },
    { metric: 'School Visits',    completed: data.schoolVisitCompleted ?? 0, pending: data.schoolVisitPending ?? 0 },
    { metric: 'School Fees',      completed: data.schoolFeeCompleted ?? 0, pending: data.schoolFeePending ?? 0 },
  ];
  return (
    <div className="table-card">
      <div className="table-header"><h3 className="table-title">Monitoring Summary</h3></div>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr><th>Metric</th><th>Completed</th><th>Pending</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.metric}>
                <td className="metric-cell">{row.metric}</td>
                <td><span className="status-badge completed">{row.completed}</span></td>
                <td><span className="status-badge pending">{row.pending}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Pagination ──────────────────────────────────────────────────────────────
function Pagination({ page, totalPages, onPage }) {
  if (totalPages <= 1) return null;
  return (
    <div className="pagination">
      <button className="page-btn" onClick={() => onPage(page - 1)} disabled={page === 1}>
        <Icon name="chevron-left" size={16} />
      </button>
      <span className="page-info">Page {page} of {totalPages}</span>
      <button className="page-btn" onClick={() => onPage(page + 1)} disabled={page === totalPages}>
        <Icon name="chevron-right" size={16} />
      </button>
    </div>
  );
}

// ─── GenericListTable ────────────────────────────────────────────────────────
function GenericListTable({ title, columns, rows, total, page, totalPages, onPage, loading }) {
  return (
    <div className="table-card">
      <div className="table-header">
        <h3 className="table-title">{title}</h3>
        <span className="table-count">{total} record{total !== 1 ? 's' : ''}</span>
      </div>
      <div className="table-wrapper">
        {loading ? (
          <div className="loading-state">Loading...</div>
        ) : rows.length === 0 ? (
          <div className="empty-state">No records found.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={row.ROW_ID ?? i}>
                  {columns.map((c) => (
                    <td key={c.key} className={c.key === 'CHILD_NAME' ? 'metric-cell' : ''}>
                      {row[c.key] ?? '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <Pagination page={page} totalPages={totalPages} onPage={onPage} />
    </div>
  );
}

// ─── Worker breakdown table ──────────────────────────────────────────────────
function WorkerBreakdownTable({ title, rows, loading }) {
  if (loading) return <div className="loading-state">Loading...</div>;
  if (!rows || rows.length === 0) return <div className="empty-state">No data available.</div>;

  return (
    <div className="table-card" style={{ marginTop: 24 }}>
      <div className="table-header"><h3 className="table-title">{title}</h3></div>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Social Worker</th>
              <th>Total Children</th>
              <th>Completed</th>
              <th>Pending</th>
              <th>Completion %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.sw_id ?? i}>
                <td className="metric-cell">{row.social_worker}</td>
                <td>{row.total_children}</td>
                <td><span className="status-badge completed">{row.completed}</span></td>
                <td><span className="status-badge pending">{row.pending}</span></td>
                <td>
                  <div className="pct-cell">
                    <div className="pct-bar-track">
                      <div
                        className="pct-bar-fill"
                        style={{ width: `${row.completion_pct ?? 0}%` }}
                      />
                    </div>
                    <span className="pct-label">{row.completion_pct ?? 0}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Module: Dashboard ───────────────────────────────────────────────────────
function DashboardModule({ selectedYear, selectedWorker }) {
  const [summaryData, setSummaryData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedYear) return;
    setLoading(true);
    setError(null);

    const params = {};
    if (selectedWorker) params.sw_id = selectedWorker;

    axios
      .get(`${API_BASE}/academic-monitoring-summary/${selectedYear}`, { params })
      .then((res) => setSummaryData(res.data))
      .catch(() => setError('Failed to load monitoring data.'))
      .finally(() => setLoading(false));
  }, [selectedYear, selectedWorker]);

  if (loading) return <div className="loading-state">Loading data...</div>;

  return (
    <>
      {error && <div className="error-banner">{error}</div>}
      <section className="kpi-section">
        <KPICard title="Total Children" value={summaryData.totalChildren ?? 0} icon="users" description="Enrolled in monitoring program" />
        <KPICard title="Academic Reports" value={summaryData.academicCompleted ?? 0} icon="file-text" description="Reports completed this year" />
        <KPICard title="School Visits" value={summaryData.schoolVisitCompleted ?? 0} icon="map-pin" description="Visits completed this year" />
        <KPICard title="School Fees" value={summaryData.schoolFeeCompleted ?? 0} icon="credit-card" description="Fee records completed" />
      </section>
      <section className="table-section">
        <SummaryTable data={summaryData} />
      </section>
    </>
  );
}

// ─── Module: Academic Reports ────────────────────────────────────────────────
function AcademicReportsModule({ selectedYear, selectedWorker }) {
  const [summary, setSummary] = useState(null);
  const [missingRows, setMissingRows] = useState([]);
  const [missingTotal, setMissingTotal] = useState(0);
  const [missingPages, setMissingPages] = useState(1);
  const [missingPage, setMissingPage] = useState(1);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingMissing, setLoadingMissing] = useState(false);

  const fetchSummary = useCallback(() => {
    if (!selectedYear) return;
    setLoadingSummary(true);
    const params = {};
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/academic-reports/summary/${selectedYear}`, { params })
      .then((res) => setSummary(res.data))
      .finally(() => setLoadingSummary(false));
  }, [selectedYear, selectedWorker]);

  const fetchMissing = useCallback((page = 1) => {
    if (!selectedYear) return;
    setLoadingMissing(true);
    const params = { page, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/academic-reports/missing/${selectedYear}`, { params })
      .then((res) => {
        setMissingRows(res.data.data);
        setMissingTotal(res.data.total);
        setMissingPages(res.data.total_pages);
        setMissingPage(page);
      })
      .finally(() => setLoadingMissing(false));
  }, [selectedYear, selectedWorker]);

  useEffect(() => { fetchSummary(); fetchMissing(1); }, [fetchSummary, fetchMissing]);

  const s = summary?.summary;

  return (
    <>
      <section className="kpi-section">
        <KPICard title="Total Children" value={s?.total_children ?? 0} icon="users" description="Under monitoring" />
        <KPICard title="Reports Completed" value={s?.completed ?? 0} icon="check-circle" description={`For ${selectedYear}`} />
        <KPICard title="Reports Pending" value={s?.pending ?? 0} icon="file-text" description="Yet to submit" />
        <KPICard title="Completion Rate" value={`${s?.completion_pct ?? 0}%`} icon="check-circle" description="Overall completion" />
      </section>
      <section className="table-section">
        <WorkerBreakdownTable
          title="Completion by Social Worker"
          rows={summary?.by_worker ?? []}
          loading={loadingSummary}
        />
      </section>
      <section className="table-section">
        <GenericListTable
          title="Children Missing Academic Report"
          columns={[
            { key: 'ROW_ID', label: 'ID' },
            { key: 'CHILD_NAME', label: 'Child Name' },
            { key: 'fam_code', label: 'Family Code' },
            { key: 'social_worker', label: 'Social Worker' },
            { key: 'submitted_types', label: 'Submitted So Far' },
          ]}
          rows={missingRows}
          total={missingTotal}
          page={missingPage}
          totalPages={missingPages}
          onPage={fetchMissing}
          loading={loadingMissing}
        />
      </section>
    </>
  );
}

// ─── Module: School Visits ───────────────────────────────────────────────────
function SchoolVisitsModule({ selectedWorker }) {
  const [summary, setSummary] = useState(null);
  const [pendingRows, setPendingRows] = useState([]);
  const [pendingTotal, setPendingTotal] = useState(0);
  const [pendingPages, setPendingPages] = useState(1);
  const [pendingPage, setPendingPage] = useState(1);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingPending, setLoadingPending] = useState(false);

  const fetchSummary = useCallback(() => {
    setLoadingSummary(true);
    const params = {};
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/school-visits/summary`, { params })
      .then((res) => setSummary(res.data))
      .finally(() => setLoadingSummary(false));
  }, [selectedWorker]);

  const fetchPending = useCallback((page = 1) => {
    setLoadingPending(true);
    const params = { page, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/school-visits/pending`, { params })
      .then((res) => {
        setPendingRows(res.data.data);
        setPendingTotal(res.data.total);
        setPendingPages(res.data.total_pages);
        setPendingPage(page);
      })
      .finally(() => setLoadingPending(false));
  }, [selectedWorker]);

  useEffect(() => { fetchSummary(); fetchPending(1); }, [fetchSummary, fetchPending]);

  const s = summary?.summary;

  return (
    <>
      <section className="kpi-section">
        <KPICard title="Total Children" value={s?.total_children ?? 0} icon="users" description="Under monitoring" />
        <KPICard title="Visits Completed" value={s?.completed ?? 0} icon="check-circle" description="At least one visit recorded" />
        <KPICard title="Visits Pending" value={s?.pending ?? 0} icon="map-pin" description="No visit recorded yet" />
        <KPICard title="Completion Rate" value={`${s?.completion_pct ?? 0}%`} icon="check-circle" description="Overall completion" />
      </section>
      <section className="table-section">
        <WorkerBreakdownTable
          title="Visit Completion by Social Worker"
          rows={summary?.by_worker ?? []}
          loading={loadingSummary}
        />
      </section>
      <section className="table-section">
        <GenericListTable
          title="Children Pending School Visit"
          columns={[
            { key: 'ROW_ID', label: 'ID' },
            { key: 'CHILD_NAME', label: 'Child Name' },
            { key: 'fam_code', label: 'Family Code' },
            { key: 'social_worker', label: 'Social Worker' },
          ]}
          rows={pendingRows}
          total={pendingTotal}
          page={pendingPage}
          totalPages={pendingPages}
          onPage={fetchPending}
          loading={loadingPending}
        />
      </section>
    </>
  );
}

// ─── Module: School Fees ─────────────────────────────────────────────────────
function SchoolFeesModule({ selectedYear, selectedWorker }) {
  const [summary, setSummary] = useState(null);
  const [pendingRows, setPendingRows] = useState([]);
  const [pendingTotal, setPendingTotal] = useState(0);
  const [pendingPages, setPendingPages] = useState(1);
  const [pendingPage, setPendingPage] = useState(1);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingPending, setLoadingPending] = useState(false);

  const fetchSummary = useCallback(() => {
    if (!selectedYear) return;
    setLoadingSummary(true);
    const params = {};
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/school-fees/summary/${selectedYear}`, { params })
      .then((res) => setSummary(res.data))
      .finally(() => setLoadingSummary(false));
  }, [selectedYear, selectedWorker]);

  const fetchPending = useCallback((page = 1) => {
    if (!selectedYear) return;
    setLoadingPending(true);
    const params = { page, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/school-fees/pending/${selectedYear}`, { params })
      .then((res) => {
        setPendingRows(res.data.data);
        setPendingTotal(res.data.total);
        setPendingPages(res.data.total_pages);
        setPendingPage(page);
      })
      .finally(() => setLoadingPending(false));
  }, [selectedYear, selectedWorker]);

  useEffect(() => { fetchSummary(); fetchPending(1); }, [fetchSummary, fetchPending]);

  const s = summary?.summary;

  return (
    <>
      <section className="kpi-section">
        <KPICard title="Total Children" value={s?.total_children ?? 0} icon="users" description="Under monitoring" />
        <KPICard title="Fee Records Done" value={s?.completed ?? 0} icon="check-circle" description={`For ${selectedYear}`} />
        <KPICard title="Fee Records Pending" value={s?.pending ?? 0} icon="credit-card" description="No fee entry yet" />
        <KPICard title="Completion Rate" value={`${s?.completion_pct ?? 0}%`} icon="check-circle" description="Overall completion" />
      </section>
      <section className="table-section">
        <WorkerBreakdownTable
          title="Fee Completion by Social Worker"
          rows={summary?.by_worker ?? []}
          loading={loadingSummary}
        />
      </section>
      <section className="table-section">
        <GenericListTable
          title="Children Pending School Fees"
          columns={[
            { key: 'ROW_ID', label: 'ID' },
            { key: 'CHILD_NAME', label: 'Child Name' },
            { key: 'fam_code', label: 'Family Code' },
            { key: 'social_worker', label: 'Social Worker' },
          ]}
          rows={pendingRows}
          total={pendingTotal}
          page={pendingPage}
          totalPages={pendingPages}
          onPage={fetchPending}
          loading={loadingPending}
        />
      </section>
    </>
  );
}

// ─── Module: Missing Aadhaar ─────────────────────────────────────────────────
function MissingAadhaarModule({ selectedWorker }) {
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback((p = 1) => {
    setLoading(true);
    const params = { page: p, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/children/missing-aadhaar`, { params })
      .then((res) => {
        setRows(res.data.data);
        setTotal(res.data.total);
        setTotalPages(res.data.total_pages);
        setPage(p);
      })
      .finally(() => setLoading(false));
  }, [selectedWorker]);

  useEffect(() => { fetchData(1); }, [fetchData]);

  return (
    <section className="table-section">
      <GenericListTable
        title="Children with Missing Aadhaar"
        columns={[
          { key: 'ROW_ID', label: 'ID' },
          { key: 'CHILD_NAME', label: 'Child Name' },
          { key: 'fam_code', label: 'Family Code' },
          { key: 'social_worker', label: 'Social Worker' },
        ]}
        rows={rows}
        total={total}
        page={page}
        totalPages={totalPages}
        onPage={fetchData}
        loading={loading}
      />
    </section>
  );
}

// ─── Module: Missing Profile ─────────────────────────────────────────────────
function MissingProfileModule({ selectedWorker }) {
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback((p = 1) => {
    setLoading(true);
    const params = { page: p, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/children/missing-profile`, { params })
      .then((res) => {
        setRows(res.data.data);
        setTotal(res.data.total);
        setTotalPages(res.data.total_pages);
        setPage(p);
      })
      .finally(() => setLoading(false));
  }, [selectedWorker]);

  useEffect(() => { fetchData(1); }, [fetchData]);

  return (
    <section className="table-section">
      <GenericListTable
        title="Children with Missing Profile"
        columns={[
          { key: 'ROW_ID', label: 'ID' },
          { key: 'CHILD_NAME', label: 'Child Name' },
          { key: 'fam_code', label: 'Family Code' },
          { key: 'social_worker', label: 'Social Worker' },
        ]}
        rows={rows}
        total={total}
        page={page}
        totalPages={totalPages}
        onPage={fetchData}
        loading={loading}
      />
    </section>
  );
}

// ─── Module: Child Data (Missing Fields Explorer) ────────────────────────────
function ChildDataModule({ selectedWorker }) {
  const [counts, setCounts] = useState([]);
  const [loadingCounts, setLoadingCounts] = useState(false);

  const [selectedColumn, setSelectedColumn] = useState(null);
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loadingRows, setLoadingRows] = useState(false);

  const fetchCounts = useCallback(() => {
    setLoadingCounts(true);
    const params = {};
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/child-data/missing-counts`, { params })
      .then((res) => setCounts(res.data))
      .finally(() => setLoadingCounts(false));
  }, [selectedWorker]);

  useEffect(() => {
    fetchCounts();
    // Reset drill-down when worker filter changes
    setSelectedColumn(null);
  }, [fetchCounts]);

  const fetchRows = useCallback((column, p = 1) => {
    setLoadingRows(true);
    const params = { column, page: p, page_size: 20 };
    if (selectedWorker) params.sw_id = selectedWorker;
    axios
      .get(`${API_BASE}/child-data/missing-children`, { params })
      .then((res) => {
        setRows(res.data.data);
        setTotal(res.data.total);
        setTotalPages(res.data.total_pages);
        setPage(p);
      })
      .finally(() => setLoadingRows(false));
  }, [selectedWorker]);

  const handleCardClick = (column) => {
    setSelectedColumn(column);
    fetchRows(column, 1);
  };

  const handleBack = () => {
    setSelectedColumn(null);
  };

  // ── Drill-down view: show list of children missing the selected field ──
  if (selectedColumn) {
    const colMeta = counts.find((c) => c.column === selectedColumn);
    return (
      <>
        <button
          className="page-btn"
          style={{ width: 'auto', padding: '8px 16px', gap: 8, display: 'flex', alignItems: 'center', marginBottom: 20 }}
          onClick={handleBack}
        >
          <Icon name="arrow-left" size={16} />
          <span>Back to Child Data</span>
        </button>
        <section className="table-section">
          <GenericListTable
            title={`Children Missing: ${colMeta?.label ?? selectedColumn}`}
            columns={[
              { key: 'ROW_ID', label: 'ID' },
              { key: 'CHILD_NAME', label: 'Child Name' },
              { key: 'fam_code', label: 'Family Code' },
              { key: 'social_worker', label: 'Social Worker' },
            ]}
            rows={rows}
            total={total}
            page={page}
            totalPages={totalPages}
            onPage={(p) => fetchRows(selectedColumn, p)}
            loading={loadingRows}
          />
        </section>
      </>
    );
  }

  // ── Default view: grid of clickable cards, one per field ──
  if (loadingCounts) return <div className="loading-state">Loading data...</div>;

  return (
    <section className="kpi-section" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
      {counts.map((c) => (
        <KPICard
          key={c.column}
          title={c.label}
          value={c.missing_count}
          icon="database"
          description="Children missing this field — click to view"
          clickable
          onClick={() => handleCardClick(c.column)}
        />
      ))}
    </section>
  );
}

// ─── App root ─────────────────────────────────────────────────────────────────
function App() {
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [socialWorkers, setSocialWorkers] = useState([]);
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedWorker, setSelectedWorker] = useState('');

  // Fetch reference data once
  useEffect(() => {
    axios.get(`${API_BASE}/social-workers`).then((res) => {
      setSocialWorkers(res.data.map((w) => ({ value: String(w.id), label: w.name })));
    }).catch(console.error);

    axios.get(`${API_BASE}/academic-years`).then((res) => {
      const years = res.data.map((y) => ({ value: y.year, label: y.year }));
      setAcademicYears(years);
      if (years.length > 0) setSelectedYear(years[0].value);
    }).catch(console.error);
  }, []);

  const handleYearChange = (val) => setSelectedYear(val);
  const handleWorkerChange = (val) => setSelectedWorker(val);

  const handleMenuSelect = (id) => {
    setActiveMenu(id);
  };

  const pageTitles = {
    'dashboard': 'Dashboard',
    'academic-reports': 'Academic Reports',
    'school-visits': 'School Visits',
    'school-fees': 'School Fees',
    'missing-aadhaar': 'Missing Aadhaar',
    'missing-profile': 'Missing Profile',
    'child-data': 'Child Data',
  };

  const renderModule = () => {
    switch (activeMenu) {
      case 'dashboard':
        return <DashboardModule selectedYear={selectedYear} selectedWorker={selectedWorker} />;
      case 'academic-reports':
        return <AcademicReportsModule selectedYear={selectedYear} selectedWorker={selectedWorker} />;
      case 'school-visits':
        return <SchoolVisitsModule selectedWorker={selectedWorker} />;
      case 'school-fees':
        return <SchoolFeesModule selectedYear={selectedYear} selectedWorker={selectedWorker} />;
      case 'missing-aadhaar':
        return <MissingAadhaarModule selectedWorker={selectedWorker} />;
      case 'missing-profile':
        return <MissingProfileModule selectedWorker={selectedWorker} />;
      case 'child-data':
        return <ChildDataModule selectedWorker={selectedWorker} />;
      default:
        return null;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeItem={activeMenu} onSelect={handleMenuSelect} />
      <main className="main-content">
        <header className="page-header">
          <div className="header-left">
            <h1 className="page-title">{pageTitles[activeMenu]}</h1>
            <p className="page-subtitle">Child Monitoring System</p>
          </div>
          <div className="header-right">
            <Dropdown
              label="Academic Year"
              value={selectedYear}
              onChange={handleYearChange}
              options={academicYears}
              placeholder="Select Year"
            />
            <Dropdown
              label="Social Worker"
              value={selectedWorker}
              onChange={handleWorkerChange}
              options={socialWorkers}
              placeholder="All Workers"
            />
          </div>
        </header>
        <div className="content-area">
          {renderModule()}
        </div>
      </main>
    </div>
  );
}

export default App;