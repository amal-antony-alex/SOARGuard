import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [summary, setSummary] = useState(null)
  const [recentAlerts, setRecentAlerts] = useState([])
  const [activeIncidents, setActiveIncidents] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedCase, setSelectedCase] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [caseLoading, setCaseLoading] = useState(false)
  const [caseError, setCaseError] = useState('')

  // ==================================================
  // FETCH DASHBOARD DATA
  // ==================================================

  const fetchDashboardData = async () => {
    try {
      setError('')

      const [
        summaryResponse,
        alertsResponse,
        incidentsResponse
      ] = await Promise.all([
        fetch(`${API_BASE}/dashboard/summary`),
        fetch(`${API_BASE}/dashboard/recent-alerts`),
        fetch(`${API_BASE}/dashboard/active-incidents`)
      ])

      if (
        !summaryResponse.ok ||
        !alertsResponse.ok ||
        !incidentsResponse.ok
      ) {
        throw new Error('Failed to fetch dashboard data')
      }

      const summaryData = await summaryResponse.json()
      const alertsData = await alertsResponse.json()
      const incidentsData = await incidentsResponse.json()

      setSummary(summaryData)
      setRecentAlerts(alertsData)
      setActiveIncidents(incidentsData)

    } catch (err) {
      setError(
        'Unable to connect to SOARGuard backend. Make sure FastAPI is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  // ==================================================
  // AUTO REFRESH
  // ==================================================

  useEffect(() => {
    fetchDashboardData()

    const interval = setInterval(() => {
      fetchDashboardData()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  // ==================================================
  // OPEN INCIDENT CASE
  // ==================================================

  const openIncidentCase = async (incidentId) => {
    try {
      setCaseLoading(true)
      setCaseError('')
      setSelectedCase(null)
      setTimeline([])

      const [
        caseResponse,
        timelineResponse
      ] = await Promise.all([
        fetch(`${API_BASE}/incidents/${incidentId}/case`),
        fetch(`${API_BASE}/incidents/${incidentId}/timeline`)
      ])

      if (!caseResponse.ok) {
        throw new Error('Failed to load incident case')
      }

      if (!timelineResponse.ok) {
        throw new Error('Failed to load incident timeline')
      }

      const caseData = await caseResponse.json()
      const timelineData = await timelineResponse.json()

      setSelectedCase(caseData)
      setTimeline(timelineData.timeline || [])

    } catch (err) {
      console.error(err)

      setCaseError(
        'Unable to load incident investigation data.'
      )
    } finally {
      setCaseLoading(false)
    }
  }

  // ==================================================
  // OPEN ALERT CASE
  // ==================================================

  const openAlertCase = async (alert) => {
    if (!alert.incident_id) {
      setCaseError(
        'This alert is not associated with an incident.'
      )
      return
    }

    await openIncidentCase(alert.incident_id)
  }

  // ==================================================
  // CLOSE CASE
  // ==================================================

  const closeCase = () => {
    setSelectedCase(null)
    setTimeline([])
    setCaseError('')
  }

  // ==================================================
  // TIMELINE EVENT TITLE
  // ==================================================

  const getTimelineEventTitle = (event) => {
    switch (event.event) {
      case 'incident_created':
        return 'Incident Created'

      case 'alert_ingested':
        return 'Alert Ingested'

      case 'playbook_executed':
        return 'Playbook Executed'

      default:
        if (event.type === 'approval') {
          return 'Approval Decision'
        }

        if (event.type === 'incident_action') {
          return 'Incident Action'
        }

        return event.event
    }
  }

  // ==================================================
  // FORMAT TIMESTAMP
  // ==================================================

  const formatTimestamp = (timestamp) => {
    if (!timestamp) {
      return 'Unknown time'
    }

    return new Date(timestamp).toLocaleString()
  }

  // ==================================================
  // LOADING SCREEN
  // ==================================================

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">
          Loading SOARGuard dashboard...
        </div>
      </div>
    )
  }

  // ==================================================
  // MAIN APPLICATION
  // ==================================================

  return (
    <div className="dashboard">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="dashboard-header">

        <div>
          <h1>SOARGuard</h1>

          <p>
            Security Orchestration, Automation & Response
          </p>
        </div>

        <div
          className={`system-status ${error ? 'offline' : ''}`}
        >

          <span className="status-dot"></span>

          {error
            ? 'Backend Offline'
            : 'Backend Connected'}

        </div>

      </header>


      {/* ==================================================
          ERROR
      ================================================== */}

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}


      {/* ==================================================
          SUMMARY
      ================================================== */}

      <section className="summary-grid">

        <div className="summary-card">
          <span className="card-label">
            Total Alerts
          </span>

          <strong>
            {summary?.alerts?.total ?? 0}
          </strong>
        </div>


        <div className="summary-card critical">
          <span className="card-label">
            Critical Alerts
          </span>

          <strong>
            {summary?.alerts?.critical ?? 0}
          </strong>
        </div>


        <div className="summary-card risk">
          <span className="card-label">
            High Risk Alerts
          </span>

          <strong>
            {summary?.alerts?.high_risk ?? 0}
          </strong>
        </div>


        <div className="summary-card approval">
          <span className="card-label">
            Awaiting Approval
          </span>

          <strong>
            {summary?.alerts?.awaiting_approval ?? 0}
          </strong>
        </div>


        <div className="summary-card">
          <span className="card-label">
            Active Incidents
          </span>

          <strong>
            {summary?.incidents?.active ?? 0}
          </strong>
        </div>


        <div className="summary-card">
          <span className="card-label">
            Resolved Incidents
          </span>

          <strong>
            {summary?.incidents?.resolved ?? 0}
          </strong>
        </div>


        <div className="summary-card">
          <span className="card-label">
            Closed Incidents
          </span>

          <strong>
            {summary?.incidents?.closed ?? 0}
          </strong>
        </div>


        <div className="summary-card">
          <span className="card-label">
            Total Incidents
          </span>

          <strong>
            {summary?.incidents?.total ?? 0}
          </strong>
        </div>

      </section>


      {/* ==================================================
          MAIN DASHBOARD
      ================================================== */}

      <section className="dashboard-grid">


        {/* ==================================================
            ACTIVE INCIDENTS
        ================================================== */}

        <div className="panel">

          <div className="panel-header">

            <div>
              <h2>
                Active Incidents
              </h2>

              <p>
                Click an incident to investigate
              </p>
            </div>

            <span className="panel-count">
              {activeIncidents.length}
            </span>

          </div>


          {activeIncidents.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ✓
              </div>

              <h3>
                No Active Incidents
              </h3>

              <p>
                There are currently no open,
                investigating, or contained incidents.
              </p>

            </div>

          ) : (

            <div className="incident-list">

              {activeIncidents.map((incident) => (

                <button
                  className="incident-row clickable"
                  key={incident.id}
                  onClick={() =>
                    openIncidentCase(incident.id)
                  }
                >

                  <div className="incident-main">

                    <strong>
                      #{incident.id} — {incident.title}
                    </strong>

                    <span>
                      {incident.description}
                    </span>

                  </div>


                  <div className="incident-meta">

                    <span
                      className={`severity ${incident.severity}`}
                    >
                      {incident.severity}
                    </span>

                    <span className="priority">
                      {incident.priority}
                    </span>

                    <span className="incident-status">
                      {incident.status}
                    </span>

                    <strong>
                      Risk {incident.risk_score}
                    </strong>

                  </div>

                </button>

              ))}

            </div>

          )}

        </div>


        {/* ==================================================
            RECENT ALERTS
        ================================================== */}

        <div className="panel">

          <div className="panel-header">

            <div>
              <h2>
                Recent Alerts
              </h2>

              <p>
                Click an alert to investigate
              </p>
            </div>

            <span className="panel-count">
              {recentAlerts.length}
            </span>

          </div>


          {recentAlerts.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ✓
              </div>

              <h3>
                No Recent Alerts
              </h3>

              <p>
                No alerts have been recorded yet.
              </p>

            </div>

          ) : (

            <div className="alert-table-wrapper">

              <table className="alert-table">

                <thead>

                  <tr>
                    <th>ID</th>
                    <th>Event</th>
                    <th>Severity</th>
                    <th>Priority</th>
                    <th>Risk</th>
                    <th>Status</th>
                  </tr>

                </thead>


                <tbody>

                  {recentAlerts.map((alert) => (

                    <tr
                      key={alert.id}
                      className="clickable-alert"
                      onClick={() =>
                        openAlertCase(alert)
                      }
                    >

                      <td>
                        #{alert.id}
                      </td>


                      <td>

                        <strong>
                          {alert.event_type}
                        </strong>

                        <small>
                          {alert.source}
                        </small>

                      </td>


                      <td>

                        <span
                          className={`severity ${alert.severity}`}
                        >
                          {alert.severity}
                        </span>

                      </td>


                      <td>

                        <span className="priority">
                          {alert.priority}
                        </span>

                      </td>


                      <td>

                        <strong>
                          {alert.risk_score}
                        </strong>

                      </td>


                      <td>

                        <span className="alert-status">
                          {alert.status}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </section>


      {/* ==================================================
          FOOTER
      ================================================== */}

      <footer className="dashboard-footer">

        <span>
          SOARGuard SOC Platform
        </span>

        <span>
          Auto-refresh: 10 seconds
        </span>

      </footer>


      {/* ==================================================
          INCIDENT CASE MODAL
      ================================================== */}

      {(selectedCase || caseLoading || caseError) && (

        <div
          className="modal-overlay"
          onClick={closeCase}
        >

          <div
            className="case-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            {/* ==================================================
                CASE HEADER
            ================================================== */}

            <div className="case-header">

              <div>

                <span className="case-label">
                  SOC INVESTIGATION CASE
                </span>

                <h2>
                  {selectedCase
                    ? selectedCase.incident.title
                    : 'Loading Case...'}
                </h2>

              </div>

              <button
                className="close-button"
                onClick={closeCase}
              >
                ×
              </button>

            </div>


            {/* ==================================================
                CASE LOADING
            ================================================== */}

            {caseLoading && (

              <div className="case-loading">
                Loading investigation data...
              </div>

            )}


            {/* ==================================================
                CASE ERROR
            ================================================== */}

            {caseError && (

              <div className="case-error">
                {caseError}
              </div>

            )}


            {/* ==================================================
                CASE CONTENT
            ================================================== */}

            {selectedCase && (

              <div className="case-content">


                {/* ==================================================
                    INCIDENT OVERVIEW
                ================================================== */}

                <section className="case-section">

                  <h3>
                    Incident Overview
                  </h3>

                  <div className="case-overview">

                    <div>
                      <span>
                        Status
                      </span>

                      <strong>
                        {selectedCase.incident.status}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Severity
                      </span>

                      <strong>
                        {selectedCase.incident.severity}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Priority
                      </span>

                      <strong>
                        {selectedCase.incident.priority}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Risk Score
                      </span>

                      <strong>
                        {selectedCase.incident.risk_score}
                      </strong>
                    </div>

                  </div>


                  <p className="case-description">
                    {selectedCase.incident.description}
                  </p>

                </section>


                {/* ==================================================
                    INVESTIGATION TIMELINE
                ================================================== */}

                <section className="case-section">

                  <div className="section-title-row">

                    <h3>
                      Investigation Timeline
                    </h3>

                    <span className="section-count">
                      {timeline.length}
                    </span>

                  </div>


                  {timeline.length === 0 ? (

                    <p className="muted">
                      No timeline events recorded.
                    </p>

                  ) : (

                    <div className="timeline">

                      {timeline.map((event, index) => (

                        <div
                          className="timeline-item"
                          data-type={event.type}
                          key={`${event.type}-${event.event}-${index}`}
                        >

                          <div className="timeline-marker">
                            <span></span>
                          </div>


                          <div className="timeline-content">

                            <div className="timeline-header">

                              <strong>
                                {getTimelineEventTitle(event)}
                              </strong>

                              <small>
                                {formatTimestamp(
                                  event.timestamp
                                )}
                              </small>

                            </div>


                            <p>
                              {event.description ||
                                `${getTimelineEventTitle(event)}`}
                            </p>


                            {event.alert_id && (

                              <span className="timeline-meta">
                                Alert #{event.alert_id}
                              </span>

                            )}


                            {event.playbook_name && (

                              <span className="timeline-meta">
                                {event.playbook_name}
                              </span>

                            )}


                            {event.status && (

                              <span className="timeline-meta">
                                Status: {event.status}
                              </span>

                            )}


                            {event.analyst && (

                              <span className="timeline-meta">
                                Analyst: {event.analyst}
                              </span>

                            )}


                            {event.previous_status &&
                              event.new_status && (

                                <span className="timeline-meta">
                                  {event.previous_status}
                                  {' → '}
                                  {event.new_status}
                                </span>

                              )}


                            {event.comments && (

                              <p className="timeline-comments">
                                {event.comments}
                              </p>

                            )}

                          </div>

                        </div>

                      ))}

                    </div>

                  )}

                </section>


                {/* ==================================================
                    ALERTS
                ================================================== */}

                <section className="case-section">

                  <div className="section-title-row">

                    <h3>
                      Alerts
                    </h3>

                    <span className="section-count">
                      {selectedCase.alerts.length}
                    </span>

                  </div>


                  {selectedCase.alerts.length === 0 ? (

                    <p className="muted">
                      No alerts associated with this incident.
                    </p>

                  ) : (

                    <div className="case-list">

                      {selectedCase.alerts.map((alert) => (

                        <div
                          className="case-item"
                          key={alert.id}
                        >

                          <div>

                            <strong>
                              #{alert.id} — {alert.event_type}
                            </strong>

                            <small>
                              {alert.source}
                            </small>

                          </div>


                          <div className="case-item-meta">

                            <span
                              className={`severity ${alert.severity}`}
                            >
                              {alert.severity}
                            </span>

                            <span className="priority">
                              {alert.priority}
                            </span>

                            <strong>
                              Risk {alert.risk_score}
                            </strong>

                          </div>

                        </div>

                      ))}

                    </div>

                  )}

                </section>


                {/* ==================================================
                    PLAYBOOK EXECUTIONS
                ================================================== */}

                <section className="case-section">

                  <div className="section-title-row">

                    <h3>
                      Playbook Executions
                    </h3>

                    <span className="section-count">
                      {selectedCase.playbook_executions.length}
                    </span>

                  </div>


                  {selectedCase.playbook_executions.length === 0 ? (

                    <p className="muted">
                      No playbook executions recorded.
                    </p>

                  ) : (

                    <div className="case-list">

                      {selectedCase.playbook_executions.map(
                        (execution) => (

                          <div
                            className="case-item"
                            key={execution.id}
                          >

                            <div>

                              <strong>
                                Playbook Execution #{execution.id}
                              </strong>

                              <small>
                                Alert #{execution.alert_id}
                              </small>

                            </div>

                            <span className="incident-status">
                              {execution.status}
                            </span>

                          </div>

                        )
                      )}

                    </div>

                  )}

                </section>


                {/* ==================================================
                    APPROVAL DECISIONS
                ================================================== */}

                <section className="case-section">

                  <div className="section-title-row">

                    <h3>
                      Approval Decisions
                    </h3>

                    <span className="section-count">
                      {selectedCase.approval_decisions.length}
                    </span>

                  </div>


                  {selectedCase.approval_decisions.length === 0 ? (

                    <p className="muted">
                      No analyst decisions recorded.
                    </p>

                  ) : (

                    <div className="case-list">

                      {selectedCase.approval_decisions.map(
                        (decision) => (

                          <div
                            className="case-item"
                            key={decision.id}
                          >

                            <div>

                              <strong>
                                {decision.decision}
                              </strong>

                              <small>
                                Analyst: {decision.analyst}
                              </small>

                            </div>


                            <span>
                              {decision.comments ||
                                'No comments'}
                            </span>

                          </div>

                        )
                      )}

                    </div>

                  )}

                </section>


                {/* ==================================================
                    INCIDENT ACTIONS
                ================================================== */}

                <section className="case-section">

                  <div className="section-title-row">

                    <h3>
                      Incident Actions
                    </h3>

                    <span className="section-count">
                      {selectedCase.incident_actions.length}
                    </span>

                  </div>


                  {selectedCase.incident_actions.length === 0 ? (

                    <p className="muted">
                      No incident actions recorded.
                    </p>

                  ) : (

                    <div className="case-list">

                      {selectedCase.incident_actions.map(
                        (action) => (

                          <div
                            className="case-item"
                            key={action.id}
                          >

                            <div>

                              <strong>
                                {action.action}
                              </strong>

                              <small>
                                {action.previous_status}
                                {' → '}
                                {action.new_status}
                              </small>

                            </div>


                            <div>

                              <strong>
                                {action.analyst}
                              </strong>

                              <small>
                                {action.comments ||
                                  'No comments'}
                              </small>

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  )}

                </section>

              </div>

            )}

          </div>

        </div>

      )}

    </div>
  )
}

export default App