const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  return response.json();
}

export function getHealth() {
  return request("/health");
}

export function getEvents() {
  return request("/api/events");
}

export function getAnalytics() {
  return request("/api/analytics");
}

export function getIncidents() {
  return request("/api/incidents");
}

export function getResponders() {
  return request("/api/responders");
}

export function getVideoSession() {
  return request("/api/video/session");
}

export function startVideoSession() {
  return request("/api/video/start", {
    method: "POST",
  });
}

export function stopVideoSession() {
  return request("/api/video/stop", {
    method: "POST",
  });
}

export function resetVideoSession() {
  return request("/api/video/reset", {
    method: "POST",
  });
}

export function updateVideoProgress(progress) {
  return request("/api/video/progress", {
    method: "POST",
    body: JSON.stringify(progress),
  });
}