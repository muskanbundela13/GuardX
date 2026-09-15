import { useEffect, useRef, useMemo, useState } from "react";
import { Activity, AlertTriangle, BarChart3, Bell, ChevronRight, LayoutDashboard, Map, Menu, Moon, Search, ShieldCheck, SlidersHorizontal, Sun, Users, X } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./App.css";
import logo from "./assets/guardx-logo.jpeg";
import {
  getHealth,
  getEvents,
  getAnalytics,
  getIncidents,
  getIncident,
  updateIncident,
  resolveIncident,
  getResponders,
  resetDemoData,
  getVideoSession,
  startVideoSession,
  stopVideoSession,
  resetVideoSession,
  updateVideoProgress,
  
} from "./services/api";

const pages = [
  ["Dashboard", LayoutDashboard], ["Live Monitoring", Activity], ["Incidents", AlertTriangle],
  ["Risk Analytics", BarChart3], ["Responders", Users], ["Security Map", Map], ["Simulation", SlidersHorizontal]
];

function formatEventType(value) {
  return String(value || "Unknown event")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatVideoTime(seconds) {
  if (!Number.isFinite(Number(seconds))) {
    return "00:00";
  }

  const totalSeconds = Math.max(0, Math.floor(Number(seconds)));
  const minutes = Math.floor(totalSeconds / 60);
  const remainingSeconds = totalSeconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(
    remainingSeconds
  ).padStart(2, "0")}`;
}

function displayValue(value) {
  return value === null || value === undefined || value === ""
    ? "Not available"
    : String(value);
}

export default function App() {
  const [page,setPage] = useState("Dashboard");
  const [dark,setDark] = useState(true);
  const [query,setQuery] = useState("");
  const [mobile,setMobile] = useState(false);
  const [selected,setSelected] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidentLoading, setIncidentLoading] = useState(false);
  const [incidentSaving, setIncidentSaving] = useState(false);
  const [incidentError, setIncidentError] = useState("");
  const [incidentSuccess, setIncidentSuccess] = useState("");
  const [incidentNotes, setIncidentNotes] = useState("");
  const [incidentStatus, setIncidentStatus] = useState("OPEN");
  const activeIncident = selectedIncident || selected;
  const [queuedVideoEvent, setQueuedVideoEvent] = useState(null);
  const [score,setScore] = useState(42);
  const [backendEvents, setBackendEvents] = useState([]);
  const [isResettingDemo, setIsResettingDemo] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [responders, setResponders] = useState([]);
  const [backendConnected, setBackendConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [startingVideo, setStartingVideo] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const [notification, setNotification] = useState(null);
  const [videoSession, setVideoSession] = useState(null);
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoError, setVideoError] = useState("");
  const videoRef = useRef(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [videoTime, setVideoTime] = useState(0);
  const [videoDuration, setVideoDuration] = useState(0);
  const lastProgressUpdate = useRef(0);
  

  useEffect(() => {
  async function testBackend() {
    try {
      const health = await getHealth();
      setBackendConnected(true);
      console.log("Backend connected:", health);
    } catch (error) {
      setBackendConnected(false);
      console.error("Backend connection failed:", error);
    }
  }

  testBackend();
}, []);


  useEffect(() => {
    async function loadEvents() {
      if (isResettingDemo) {
        return;
      }

      try {
        const data = await getEvents();

        console.log("Backend events loaded:", data);

        const freshEvents = Array.isArray(data)
          ? data
          : data?.events || [];

        setBackendEvents(freshEvents);
        setLastUpdated(new Date());
      } catch (error) {
        console.error("Could not load backend events:", error);
      }
    }

    loadEvents();

    const interval = setInterval(loadEvents, 2000);

    return () => clearInterval(interval);
  }, [isResettingDemo]);

  useEffect(() => {
async function loadBackendData() {
  try {
    const respondersData = await getResponders();

    const responderList = Array.isArray(respondersData)
      ? respondersData
      : respondersData?.responders || [];

    console.log("Responders loaded:", responderList);
    setResponders(responderList);
  } catch (error) {
    console.error("Could not load responders:", error);
    setResponders([]);
  }

  try {
    const incidentsData = await getIncidents();

    const incidentList = Array.isArray(incidentsData)
      ? incidentsData
      : incidentsData?.incidents || [];

    setIncidents(incidentList);
  } catch (error) {
    console.error("Could not load incidents:", error);
    setIncidents([]);
  }

  try {
    const analyticsData = await getAnalytics();
    setAnalytics(analyticsData);
  } catch (error) {
    console.error("Could not load analytics:", error);
    setAnalytics(null);
  }

  setLastUpdated(new Date());
}

  const interval = setInterval(loadBackendData, 2000);

  return () => clearInterval(interval);
}, []);

  useEffect(() => {
    loadVideoSession();
  }, []);

  useEffect(() => {
    if (!queuedVideoEvent || !videoRef.current || !videoDuration) return;
    jumpToEvent(queuedVideoEvent);
    setQueuedVideoEvent(null);
  }, [queuedVideoEvent, page, videoDuration]);

  async function handleResolveIncident() {
    const incidentId = activeIncident?.incident_id;

    if (!incidentId) {
      setIncidentError("Incident ID is missing");
      return;
    }

    setIncidentSaving(true);
    setIncidentError("");
    setIncidentSuccess("");

    try {
      const detail = await resolveIncident(incidentId);

      setSelected(detail);
      setSelectedIncident(detail);
      setIncidentStatus(detail.status || "RESOLVED");
      setIncidentNotes(detail.notes || "");
      setIncidentSuccess("Incident marked as resolved");

      const refreshedIncidents = await getIncidents();

      setIncidents(
        Array.isArray(refreshedIncidents)
          ? refreshedIncidents
          : refreshedIncidents.incidents || []
      );
    } catch (error) {
      setIncidentError(
        error.message || "Failed to resolve incident"
      );
    } finally {
      setIncidentSaving(false);
    }
  }

  async function handleSaveIncident() {
    const incident = selectedIncident || selected;

    console.log("Save button clicked:", incident);

    if (!incident?.incident_id) {
      setIncidentError("No selected incident");
      return;
    }

    await saveIncident({
      status: incidentStatus || incident.status || "OPEN",
      notes: incidentNotes,
    });
  }

  async function saveIncident(update) {
    const incident = selectedIncident || selected;
    const incidentId = incident?.incident_id;

    if (!incidentId) {
      setIncidentError("Incident ID is missing");
      return;
    }

    setIncidentSaving(true);
    setIncidentError("");
    setIncidentSuccess("");

    try {
      await updateIncident(incidentId, update);

      const detail = await getIncident(incidentId);

      setSelected(detail);
      setSelectedIncident(detail);
      setIncidentStatus(detail.status || update.status || "OPEN");
      setIncidentNotes(detail.notes || "");

      setIncidents((current) =>
        current.map((item) =>
          item.incident_id === detail.incident_id
            ? { ...item, ...detail }
            : item
        )
      );

      setIncidentSuccess("Incident saved successfully");
    } catch (error) {
      setIncidentError(
        error.message || "Could not save incident changes."
      );
    } finally {
      setIncidentSaving(false);
    }
  }

  
  async function openIncident(incident) {
    setIncidentLoading(true);
    setIncidentError("");
    setIncidentSuccess("");

    try {
      setSelected(incident);

      const detail = await getIncident(incident.incident_id);

      setSelected(detail);
      setSelectedIncident(detail);
      setIncidentStatus(detail.status || "OPEN");
      setIncidentNotes(detail.notes || "");
    } catch (error) {
      setIncidentError(error.message || "Failed to load incident");
    } finally {
      setIncidentLoading(false);
    }
  }

  function openLinkedIncidentEvent() {
    if (!selectedIncident) return;
    setPage("Dashboard");
    setSelectedIncident(null);
    setQueuedVideoEvent({
      id: selectedIncident.event_id,
      type: formatEventType(selectedIncident.event_type),
      location: selectedIncident.location || selectedIncident.zone_id || "Unassigned Zone",
      riskScore: selectedIncident.risk_score,
      riskLevel: selectedIncident.risk_level || "LOW",
      status: selectedIncident.status,
      videoTimestamp: getVideoTimestamp(selectedIncident),
    });
  }

  async function loadVideoSession() {
  try {
    const data = await getVideoSession();
    setVideoSession(data.session);
  } catch (error) {
    console.error("Could not load video session:", error);
    setVideoError("Could not connect to video session API.");
  }
}

  async function handleStartVideo() {
    if (videoLoading) {
      return;
    }

    if (videoSession?.status === "RUNNING") {
      return;
    }

    setVideoLoading(true);
    setVideoError("");

    try {
      const data = await startVideoSession();
      setVideoSession(data.session);
    } catch (error) {
      console.error("Could not start video:", error);
      setVideoError(error.message || "Could not start video analysis");
      throw error;
    } finally {
      setVideoLoading(false);
    }
  }
  async function handleStopVideo() {
    setVideoLoading(true);
    setVideoError("");

    try {
      const data = await stopVideoSession();
      setVideoSession(data.session);
    } catch (error) {
      console.error("Could not stop video:", error);
      setVideoError(error.message);
    } finally {
      setVideoLoading(false);
    }
  }

  async function handleResetVideo() {
    setVideoLoading(true);
    setVideoError("");

    try {
      const data = await resetVideoSession();
      setVideoSession(data.session);
    } catch (error) {
      console.error("Could not reset video:", error);
      setVideoError(error.message);
    } finally {
      setVideoLoading(false);
    }
  }

  async function handleVideoPlay() {
    try {
      if (!videoRef.current) {
        return;
      }

      const alreadyRunning = videoSession?.status === "RUNNING";

      if (!alreadyRunning) {
        await handleStartVideo();
      }

      await videoRef.current.play();
      setIsVideoPlaying(true);
    } catch (error) {
      console.error("Could not play video:", error);
      setVideoError(error.message || "Could not play video");
    }
  }

  async function handleResetDemo() {
    const confirmed = window.confirm(
      "This will delete all old events and incidents. Continue?"
    );

    if (!confirmed) {
      return;
    }

    setIsResettingDemo(true);

    try {
      // Clear the UI immediately.
      setBackendEvents([]);
      setIncidents([]);

      setAnalytics({
        total_events: 0,
        average_risk: 0,
        high_risk_events: 0,
        threat_distribution: {},
        event_type_distribution: {},
      });

      setSelected(null);
      setSelectedIncident(null);
      setQueuedVideoEvent(null);
      setAcknowledged(false);
      setNotification(null);
      setLastUpdated(new Date());

      // Delete backend events and incidents.
      await resetDemoData();

      // Confirm that the backend is empty.
      const [eventsData, incidentsData, analyticsData] = await Promise.all([
        getEvents(),
        getIncidents(),
        getAnalytics(),
      ]);

      const freshEvents = Array.isArray(eventsData)
        ? eventsData
        : eventsData?.events || [];

      const freshIncidents = Array.isArray(incidentsData)
        ? incidentsData
        : incidentsData?.incidents || [];

      setBackendEvents(freshEvents);
      setIncidents(freshIncidents);

      setAnalytics({
        ...(analyticsData || {}),
        total_events: freshEvents.length,
      });

      setLastUpdated(new Date());

      alert(
        freshEvents.length === 0
          ? "Demo reset successfully. Total events is now 0."
          : `Reset completed, but the backend returned ${freshEvents.length} events.`
      );
    } catch (error) {
      console.error("Reset failed:", error);

      alert(error.message || "Reset failed. Check the backend terminal.");
    } finally {
      setIsResettingDemo(false);
    }
  }

  async function handleVideoPause() {
    try {
      if (!videoRef.current) return;

      videoRef.current.pause();
      setIsVideoPlaying(false);

      await handleStopVideo();
    } catch (error) {
      setVideoError(error.message);
    }
  }

  async function handleVideoTimeUpdate() {
    if (!videoRef.current) return;

    const currentTime = videoRef.current.currentTime;
    const duration = videoRef.current.duration || 0;

    setVideoTime(currentTime);

    // Send progress only every 1 second
    if (currentTime - lastProgressUpdate.current < 1) {
      return;
    }

    lastProgressUpdate.current = currentTime;

    try {
      await updateVideoProgress({
        current_time: currentTime,
        duration: duration,
        current_frame: Math.floor(currentTime * 30),
        completed: false,
      });
    } catch (error) {
      console.error("Video progress update failed:", error);
    }
  }

  function handleVideoLoadedMetadata() {
    if (!videoRef.current) return;

    setVideoDuration(videoRef.current.duration);
  }

  async function handleVideoEnded() {
    setIsVideoPlaying(false);

  try {
    await updateVideoProgress({
      current_time: videoDuration,
      duration: videoDuration,
      current_frame: Math.floor(videoDuration * 30),
      completed: true,
    });

    await loadVideoSession();
  } catch (error) {
    console.error("Could not complete video session:", error);
  }
}

  function handleVideoSeek(event) {
    const nextTime = Number(event.target.value);

    if (!videoRef.current) return;

    videoRef.current.currentTime = nextTime;
    setVideoTime(nextTime);
  }

  function formatVideoTime(seconds) {
    const safeSeconds = Math.floor(Number(seconds) || 0);
    const minutes = Math.floor(safeSeconds / 60);
    const remainingSeconds = safeSeconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  }

  function getVideoTimestamp(event) {
    const value =
      event.videoTimestamp ??
      event.video_timestamp ??
      event.evidence?.video_timestamp ??
      event.evidence?.videoTimestamp ??
      event.video_time ??
      event.videoTime;

    const numericValue = Number(value);

    return Number.isFinite(numericValue) && numericValue >= 0
      ? numericValue
      : null;
  }

  function jumpToEvent(event) {
    const timestamp = getVideoTimestamp(event);

    if (
      !videoRef.current ||
      timestamp === null ||
      timestamp > videoDuration
    ) {
      setSelected(event);
      setNotification("Video position is not available for this event");
      return;
    }

    videoRef.current.currentTime = timestamp;
    setVideoTime(timestamp);
    setSelected(event);
    setAcknowledged(false);

    setNotification(
      `${event.type} opened at ${formatVideoTime(timestamp)}`
    );
  }

  const displayEvents = backendEvents.map((event, index) => ({
    id: event.event_id || `EVT-${index + 1}`,
    type: formatEventType(event.event_type),
    location: event.zone_id || event.zone || event.location || "Unassigned Zone",
    timestamp: event.timestamp,

    videoTimestamp: getVideoTimestamp(event),

    cameraId: event.camera_id ?? "CAM-01",
    zoneId: event.zone_id ?? event.zone ?? null,
    trackId: event.track_id ?? null,

    riskScore:
      event.risk?.risk_score ??
      event.risk_score ??
      event.reliability_score ??
      0,

    riskLevel:
      event.risk?.risk_level ??
      event.risk_level ??
      (Number(
        event.risk?.risk_score ??
          event.risk_score ??
          event.reliability_score ??
          0
      ) >= 70
        ? "HIGH"
        : "LOW"),

    confidence: event.confidence,
    reliability: event.reliability_score,
    action: event.risk?.recommended_action || "LOG_EVENT",
    status: "OPEN",
  }));

  const averageRisk = displayEvents.length
  ? (
      displayEvents.reduce(
        (total, event) => total + Number(event.riskScore || 0),
        0
      ) / displayEvents.length
    ).toFixed(1)
  : "0.0";

  const riskCounts = {
  LOW: displayEvents.filter((event) => event.riskLevel === "LOW").length,
  MEDIUM: displayEvents.filter((event) => event.riskLevel === "MEDIUM").length,
  HIGH: displayEvents.filter((event) => event.riskLevel === "HIGH").length,
  CRITICAL: displayEvents.filter((event) => event.riskLevel === "CRITICAL").length,
};

const totalRiskEvents = displayEvents.length || 1;

const riskDistribution = [
  {
    label: "Low",
    value: `${Math.round((riskCounts.LOW / totalRiskEvents) * 100)}%`,
  },
  {
    label: "Medium",
    value: `${Math.round((riskCounts.MEDIUM / totalRiskEvents) * 100)}%`,
  },
  {
    label: "High",
    value: `${Math.round((riskCounts.HIGH / totalRiskEvents) * 100)}%`,
  },
  {
    label: "Critical",
    value: `${Math.round((riskCounts.CRITICAL / totalRiskEvents) * 100)}%`,
  },
];

  

const filtered = useMemo(
  () =>
    displayEvents.filter((event) =>
      `${event.id} ${event.type} ${event.location} ${event.riskLevel}`
        .toLowerCase()
        .includes(query.toLowerCase())
    ),
  [displayEvents, query]
);

  return <div className={`app ${dark ? "dark" : "light"}`}>
    <aside className={`sidebar ${mobile ? "open" : ""}`}>
      <div className="brand"><img src={logo} alt="GuardX logo"/><div><b>GuardX</b><small>Security Intelligence</small></div><button className="icon mobile-close" onClick={()=>setMobile(false)}><X size={18}/></button></div>
      <div className="workspace"><ShieldCheck size={18}/><div><b>Command Center</b><small>Production workspace</small></div><ChevronRight size={16}/></div>
      <nav>{pages.map(([name,Icon],i)=><button key={name} className={page===name?"active":""} onClick={()=>{setPage(name);setMobile(false)}}><Icon size={18}/><span>{name}</span>{name === "Incidents" && <em>{incidents.length}</em>}</button>)}</nav>
      <div className="health"><i/> All systems operational</div>
    </aside>
    {mobile&&<button className="backdrop" onClick={()=>setMobile(false)}/>}
    <main>
      <header><div className="heading"><button className="icon mobile-menu" onClick={()=>setMobile(true)}><Menu size={20}/></button><div><small>SECURITY OPERATIONS CENTER</small><h1>{page}</h1><p>GuardX <ChevronRight size={12}/> {page}</p></div></div><div className="actions"><label><Search size={16}/><input placeholder="Search events..." value={query} onChange={e=>setQuery(e.target.value)}/></label><button className="icon" onClick={()=>setDark(!dark)}>{dark?<Sun size={18}/>:<Moon size={18}/>}</button><button className="icon"><Bell size={18}/></button><strong className="avatar">MB</strong></div></header>
      <section className="body">
<div className="hero">
  <div>
    <span>● LIVE ENVIRONMENT</span>

    <h2>
      {page === "Dashboard"
        ? "Good evening, Operator"
        : `${page} control room`}
    </h2>

    <p>
      Monitor risk, investigate incidents, and coordinate response from one
      intelligent security workspace.
    </p>
  </div>

  <div className="hero-score">
    <small>Current threat level</small>
    <b>LOW</b>
    <small>Updated a few seconds ago</small>

    <button
      className="primary-btn"
      disabled={startingVideo}
      onClick={async () => {
        try {
          setStartingVideo(true);

          await handleStartVideo();
          setNotification("Video analysis started");
        } catch (error) {
          console.error("Video analysis failed:", error);
          alert("Failed to start video analysis");
        } finally {
          setStartingVideo(false);
        }
      }}
    >
      {startingVideo ? "Starting..." : "Start Analysis"}
    </button>
  </div>
</div>

        {page === "Dashboard" && (
          <>

          <Panel title="CCTV video" eyebrow="CAMERA MONITORING">
            <div className="video-player-wrapper">
              <video
                ref={videoRef}
                className="guardx-video"
                src="/cctv_test.mp4"
                onTimeUpdate={handleVideoTimeUpdate}
                onLoadedMetadata={handleVideoLoadedMetadata}
                onEnded={handleVideoEnded}
              />

              <div className="video-player-info">
                <div>
                  <b>Camera 01</b>
                  <span>Campus Main Area</span>
                </div>

                <span
                  className={`processing-status ${
                    videoSession?.status?.toLowerCase() || "idle"
                  }`}
                >
                  {videoSession?.status || "IDLE"}
                </span>
              </div>

              <div className="video-controls">
                {videoError && (
                  <p className="video-error">
                    {videoError}
                  </p>
                )}
                <button
                  type="button"
                  onClick={isVideoPlaying ? handleVideoPause : handleVideoPlay}
                >
                  {isVideoPlaying ? "Pause" : "Play"}
                </button>

                <span>{formatVideoTime(videoTime)}</span>

                <input
                  type="range"
                  min="0"
                  max={videoDuration || 0}
                  step="0.1"
                  value={videoTime}
                  onChange={handleVideoSeek}
                  aria-label="Video progress"
                />

                <span>{formatVideoTime(videoDuration)}</span>

                <button
                  type="button"
                  onClick={async () => {
                    try {
                      if (!videoRef.current) return;

                      videoRef.current.currentTime = 0;
                      setVideoTime(0);

                      await handleResetVideo();
                      await handleStartVideo();

                      await videoRef.current.play();
                      setIsVideoPlaying(true);
                    } catch (error) {
                      setVideoError(error.message);
                    }
                  }}
                >
                  Replay
                </button>
              </div>
            </div>
          </Panel>

          <Panel title="Video session" eyebrow="SESSION MANAGEMENT">
            <div className="video-session">
              <div className="video-session-status">
                <span>Status</span>
                <strong className={videoSession?.status?.toLowerCase()}>
                  {videoSession?.status || "IDLE"}
                </strong>
              </div>

              <div className="video-session-grid">
                <div>
                  <small>Session ID</small>
                  <b>
                    {videoSession?.session_id
                      ? videoSession.session_id.slice(0, 8)
                      : "Not started"}
                  </b>
                </div>

                <div>
                  <small>Camera</small>
                  <b>{videoSession?.camera_name || "Unknown camera"}</b>
                </div>

                <div>
                  <small>Location</small>
                  <b>{videoSession?.camera_location || "Unknown location"}</b>
                </div>

                <div>
                  <small>Current time</small>
                  <b>{Number(videoSession?.current_time || 0).toFixed(1)} sec</b>
                </div>

                <div>
                  <small>Duration</small>
                  <b>{Number(videoSession?.duration || 0).toFixed(1)} sec</b>
                </div>

                <div>
                  <small>Frame</small>
                  <b>{videoSession?.current_frame || 0}</b>
                </div>
              </div>

              <p className="video-name">
                {videoSession?.video_name || "No video selected"}
              </p>

              <div className="video-actions">
                <button
                  type="button"
                  onClick={handleStartVideo}
                  disabled={videoLoading}
                >
                  Start session
                </button>

                <button
                  type="button"
                  onClick={handleStopVideo}
                  disabled={
                    videoLoading ||
                    !videoSession?.session_id ||
                    videoSession?.status !== "RUNNING"
                  }
                >
                  Stop session
                </button>

                <button
                  type="button"
                  onClick={handleResetVideo}
                  disabled={videoLoading}
                >
                  Reset
                </button>
              </div>

              {videoError && (
                <p className="video-error">
                  {videoError}
                </p>
              )}
            </div>
          </Panel>
            <div className="stats">
              {[
                ["Total events", backendEvents.length, "Live backend data"],
                ["Active incidents", incidents.length, "Backend incidents"],
                ["Average risk", averageRisk, "Calculated risk"],
                ["Responders", responders.length, "Backend responders"],
              ].map((s) => (
                <article className="stat" key={s[0]}>
                  <small>{s[0]}</small>
                  <b>{s[1]}</b>
                  <span>{s[2]}</span>
                </article>
              ))}
            </div>

            <div className="grid">
              <Panel title="Event activity" eyebrow="RISK INTELLIGENCE">
                <Chart events={displayEvents} />
              </Panel>

              <Panel title="Threat composition" eyebrow="RISK DISTRIBUTION">
                <div className="donut">
                  <div>
                    <b>{backendEvents.length}</b>
                    <small>Total events</small>
                  </div>
                </div>

                <Risk
                  label="Low"
                  value={`${Math.round((riskCounts.LOW / totalRiskEvents) * 100)}%`}
                  tone="low"
                />

                <Risk
                  label="Medium"
                  value={`${Math.round((riskCounts.MEDIUM / totalRiskEvents) * 100)}%`}
                  tone="medium"
                />

                <Risk
                  label="High"
                  value={`${Math.round((riskCounts.HIGH / totalRiskEvents) * 100)}%`}
                  tone="high"
                />

                <Risk
                  label="Critical"
                  value={`${Math.round((riskCounts.CRITICAL / totalRiskEvents) * 100)}%`}
                  tone="critical"
                />
              </Panel>
            </div>

            <div className="grid">


              <Panel title="Live event feed" eyebrow="REAL-TIME">
                <Table
                  data={filtered}
                  select={setSelected}
                  jumpToEvent={jumpToEvent}
                />
              </Panel>

              <Panel title="Priority queue" eyebrow="INCIDENT MANAGEMENT">
                <div className="priority">
                  {[...displayEvents]
                    .sort(
                      (a, b) =>
                        Number(b.riskScore || 0) - Number(a.riskScore || 0)
                    )
                    .slice(0, 3)
                    .map((event) => (
                      <button
                        className="priority-item"
                        key={event.id}
                        type="button"
                        onClick={() => {
                          console.log("Selected event:", event);
                          setSelected(event);
                          setAcknowledged(false);
                          setNotification(`${event.type} details opened`);
                        }}
                      >
                        <i className={event.riskLevel.toLowerCase()} />

                        <span>
                          <b>{event.type}</b>
                          <small>{event.location}</small>
                        </span>

                        <strong className={event.riskLevel.toLowerCase()}>
                          {event.riskScore}
                        </strong>
                      </button>
                    ))}
                </div>
              </Panel>

            </div>
          </>
        )}

        {page==="Live Monitoring"&&<Panel title="Live security events" eyebrow="REAL-TIME MONITORING"><Table
            data={filtered}
            select={setSelected}
            jumpToEvent={jumpToEvent}
          /></Panel>}
        {page === "Incidents" && (
          <Panel title="Active incidents" eyebrow="INCIDENT MANAGEMENT">
            <div className="cards">
              {incidents.length === 0 ? (
                <p>No incidents received yet.</p>
              ) : (
                incidents.slice(0, 3).map((event, index) => (
                  <article
                    key={event.event_id || `INC-${index + 1}`}
                    onClick={() => {
                      const selectedIncident =
                        displayEvents.find(
                          (item) => item.id === event.event_id
                        );

                      if (selectedIncident) {
                        jumpToEvent(selectedIncident);
                      } else {
                        setNotification("Linked event is no longer available");
                      }
                    }}
                  >
                    <small>{event.event_id || `INC-${index + 1}`}</small>

                    <h3>{formatEventType(event.event_type)}</h3>

                    <p>{event.zone_id || event.zone || event.location || "Unassigned Zone"}</p>

                    <strong className="high">
                    {event.risk?.risk_score ??
                      event.risk_score ??
                      event.reliability_score ??
                      0}
                      {" · "}
                      {event.risk?.risk_level ||
                        event.risk_level ||
                        (Number(
                          event.risk?.risk_score ??
                            event.risk_score ??
                            event.reliability_score ??
                            0
                        ) >= 70
                          ? "HIGH"
                          : "LOW")}
                    </strong>
                  </article>
                ))
              )}
            </div>
          </Panel>
        )}

        {page === "Risk Analytics" && (
          <Panel title="Risk analytics overview" eyebrow="RISK INTELLIGENCE">
            <Chart events={displayEvents} large />
          </Panel>
        )}

        {page === "Responders" && (
          <Panel title="Available responders" eyebrow="RESPONSE TEAM">
            <div className="cards">
              {responders.length === 0 ? (
                <p>No responders available.</p>
              ) : (
                responders.map((responder, index) => (
                  <article key={responder.id || responder.name || index}>
                    <div className="responder">
                      <b>
                        {responder.name
                          ? responder.name
                              .split(" ")
                              .map((word) => word[0])
                              .join("")
                              .slice(0, 2)
                              .toUpperCase()
                          : `R${index + 1}`}
                      </b>

                      <span>
                        <strong>
                          {responder.name || `Responder ${index + 1}`}
                        </strong>

                        <small>
                          {responder.zone || responder.location || "Campus Zone"}
                          {" · "}
                          {responder.role || "Patrol Unit"}
                        </small>
                      </span>

                      <em>{responder.status || "AVAILABLE"}</em>
                    </div>
                  </article>
                ))
              )}
            </div>
          </Panel>
        )}

        {page==="Security Map"&&<Panel title="Security zone overview" eyebrow="LOCATION INTELLIGENCE"><div className="map"><span>North Gate</span><span>Warehouse</span><span>Parking Area</span><i/><i/><i/></div></Panel>}

        {page==="Simulation"&&<Panel title="Risk simulation" eyebrow="SCENARIO TESTING"><p>Move the slider to simulate an incoming event.</p><label className="range">Risk score <b>{score}</b><input type="range" min="0" max="100" value={score} onChange={e=>setScore(+e.target.value)}/></label><div className={`simulation ${score>=70?"high":score>=35?"medium":"low"}`}><small>Predicted severity</small><b>{score>=70?"HIGH":score>=35?"MEDIUM":"LOW"}</b></div></Panel>}

        {selected && (
          <div className="selected">
            <div>
              <small>SELECTED EVENT</small>
              <h3>
                {formatEventType(
                  activeIncident?.event_type || activeIncident?.type
                )}
              </h3>
              <p>
                {selected.id} · {selected.location}
              </p>
            </div>

            <b className={selected.riskLevel.toLowerCase()}>
              {selected.riskScore}
            </b>

            <button className="icon" onClick={() => setSelected(null)}>
              <X size={17} />
            </button>
          </div>
        )}
      </section>
        {activeIncident && (
          <div className="incident-overlay">
            <div className="incident-modal">
              <button
                className="incident-close"
                type="button"
                onClick={() => {
                  setSelected(null);
                  setAcknowledged(false);
                }}
              >
                <X size={18} />
              </button>

              <button
                type="button"
                onClick={handleResolveIncident}
                disabled={
                  incidentSaving ||
                  selectedIncident?.status === "RESOLVED"
                }
              >
                {incidentSaving ? "Resolving..." : "Mark as Resolved"}
              </button>

              <p className="eyebrow">SELECTED INCIDENT</p>
              <h2>Incident details</h2>

              <div className="incident-details">
                <h3>{selected.type}</h3>

                <p>
                  <b>Location:</b>{" "}
                  {displayValue(
                    activeIncident?.location ||
                    activeIncident?.zone_id ||
                    activeIncident?.zone
                  )}
                </p>

                <p>
                  <b>Risk score:</b>{" "}
                  {displayValue(
                    activeIncident?.risk_score ??
                    activeIncident?.riskScore ??
                    activeIncident?.reliability_score
                  )}
                </p>

                <p>
                  <b>Risk level:</b>{" "}
                  {displayValue(
                    activeIncident?.risk_level ||
                    activeIncident?.riskLevel
                  )}
                </p>

                <p>
                  <b>Current status:</b>{" "}
                  {displayValue(
                    activeIncident?.status || incidentStatus
                  )}
                </p>

                <p>
              <strong>Event ID:</strong>{" "}
              {selectedIncident?.event_id || "N/A"}
            </p>

            <p>
              <strong>Video File:</strong>{" "}
              {selectedIncident?.video_file_id || "N/A"}
            </p>

            <p>
              <strong>Session ID:</strong>{" "}
              {selectedIncident?.session_id || "N/A"}
            </p>

            <p>
              <strong>Camera:</strong>{" "}
              {selectedIncident?.camera_id || "N/A"}
            </p>

            <p>
              <strong>Location:</strong>{" "}
              {selectedIncident?.location || "N/A"}
            </p>

            <p>
              <strong>Detection Time:</strong>{" "}
              {selectedIncident?.video_timestamp ?? "N/A"}
            </p>

                <label htmlFor="incident-status">
                  <b>Status</b>
                </label>

                <select
                  id="incident-status"
                  value={incidentStatus}
                  onChange={(event) => setIncidentStatus(event.target.value)}
                >
                  <option value="OPEN">Open</option>
                  <option value="ACKNOWLEDGED">Acknowledged</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="RESOLVED">Resolved</option>
                  <option value="CLOSED">Closed</option>
                </select>

                <label htmlFor="incident-notes">
                  <b>Notes</b>
                </label>

                <textarea
                  id="incident-notes"
                  value={incidentNotes}
                  onChange={(event) => setIncidentNotes(event.target.value)}
                  placeholder="Add incident notes"
                  rows={4}
                />
              </div>

              <div className="incident-actions">
                <button
                  type="button"
                  onClick={handleSaveIncident}
                  disabled={incidentSaving}
                >
                  {incidentSaving ? "Saving..." : "Save changes"}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSelected(null);
                    setAcknowledged(false);
                  }}
                >
                  Close details
                </button>
              </div>

              {incidentError && (
                <p className="error">{incidentError}</p>
              )}

              {incidentSuccess && (
                <p className="success">{incidentSuccess}</p>
              )}
            </div>
          </div>
        )}
      
    </main>
    {notification && (
          <div className="toast" role="status">
            <div>
              <b>Incident selected</b>
              <span>{notification}</span>
            </div>

            <button
              type="button"
              onClick={() => setNotification(null)}
            >
              <X size={16} />
            </button>
          </div>
        )}

        <button
          className="top"
          onClick={() =>
            window.scrollTo({ top: 0, behavior: "smooth" })
          }
        >↑</button>
  </div>
}

function Panel({title,eyebrow,children}){return <section className="panel"><div className="panel-head"><div><small>{eyebrow}</small><h2>{title}</h2></div><span>View details <ChevronRight size={13}/></span></div>{children}</section>}

function Chart({ events = [], large = false }) {
  const chartData = events
    .slice()
    .reverse()
    .map((event, index) => ({
      name: `E${index + 1}`,
      risk: Number(event.riskScore || 0),
    }));

  if (chartData.length === 0) {
    return (
      <div className="chart">
        <p>No event data available yet.</p>
        <small>
          The chart will update when the backend produces events.
        </small>
      </div>
    );
  }

  return (
    <div className={large ? "chart large" : "chart"}>
      <ResponsiveContainer width="100%" height={large ? 320 : 240}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="risk"
            stroke="#38bdf8"
            fill="#38bdf8"
            fillOpacity={0.2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
function Risk({label,value,tone}){return <div className="risk"><span><i className={tone}/>{label}</span><div><b className={tone} style={{width:value}}/></div><strong>{value}</strong></div>}

function Table({ data, select, jumpToEvent }) {
  return (
    <div className="table">
      <div className="tr head">
        <span>Event</span>
        <span>Location</span>
        <span>Risk</span>
        <span>Status</span>
      </div>

      {data.length === 0 ? (
        <div className="tr">
          <span>No events received yet.</span>
        </div>
      ) : (
        data.map((event) => (
          <button
            className="tr"
            key={event.id}
            onClick={() => {
              select(event);
              jumpToEvent?.(event);
            }}
          >
            <span>
              <b>{event.type}</b>
              <small>{event.id}</small>

              {event.videoTimestamp !== null && (
                <small>
                  Video: {formatVideoTime(event.videoTimestamp)}
                </small>
              )}
            </span>

            <span>{event.location}</span>

            <strong className={event.riskLevel.toLowerCase()}>
              {event.riskScore} · {event.riskLevel}
            </strong>

            <em>{event.status || "OPEN"}</em>
          </button>
        ))
      )}
    </div>
  );
}
