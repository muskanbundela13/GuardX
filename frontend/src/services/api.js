const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
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

export function getIncident(incidentId) {
  return request(`/api/incidents/${incidentId}`);
}

export function updateIncident(incidentId, update) {
  return request(`/api/incidents/${incidentId}/status`, {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}

export function resolveIncident(incidentId) {
  return request(`/api/incidents/${incidentId}/resolve`, {
    method: "POST",
  });
}

export function getResponders() {
  return request("/api/responders");
}

// Video session APIs
export function getVideoSession() {
  return request("/api/video/session");
}

export function startVideoSession(videoId = null) {
  return request("/api/video/start", {
    method: "POST",
    body: JSON.stringify(videoId ? { video_id: videoId } : {}),
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

// Demo Video Library APIs
export function getVideos() {
  return request("/api/videos");
}

export function getVideo(videoId) {
  return request(`/api/videos/${videoId}`);
}

export function uploadVideo(file, metadata = {}) {
  const formData = new FormData();

  formData.append("file", file);

  if (metadata.name) {
    formData.append("name", metadata.name);
  }

  if (metadata.description) {
    formData.append("description", metadata.description);
  }

  return request("/api/videos/upload", {
    method: "POST",
    body: formData,
  });
}

export function updateVideo(videoId, update) {
  return request(`/api/videos/${videoId}`, {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}

export function renameVideo(videoId, name) {
  return updateVideo(videoId, { name });
}

export function deleteVideo(videoId) {
  return request(`/api/videos/${videoId}`, {
    method: "DELETE",
  });
}

export function selectVideo(videoId) {
  return request(`/api/videos/${videoId}/select`, {
    method: "POST",
  });
}

export function resetDemoData() {
  return request("/api/demo/reset", {
    method: "POST",
  });
}