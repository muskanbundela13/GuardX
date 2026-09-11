import json
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


test_event = {
    "event_type": "RESTRICTED_ZONE_ENTRY",
    "timestamp": 1789150383.70733,
    "track_id": 43,
    "zone": "restricted_area",
    "confidence": None,
    "reliability_score": 80,
    "details": {
        "source": "GuardX CV pipeline",
        "test": True,
        "frame_number": 120
    }
}


def post_event():
    url = f"{BASE_URL}/api/events/ingest"

    request = urllib.request.Request(
        url,
        data=json.dumps(test_event).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    print("\nPOST EVENT")
    print(json.dumps(result, indent=2))

    assert response.status == 200
    assert result["status"] == "success"
    assert result["event"]["event_type"] == (
        "RESTRICTED_ZONE_ENTRY"
    )
    assert "event_id" in result["event"]
    assert "received_at" in result["event"]
    assert "evidence" in result["event"]
    assert result["risk"]["risk_level"] == "HIGH"
    assert result["response"]["response_type"] == "ALERT"

    return result


def post_duplicate_event():
    url = f"{BASE_URL}/api/events/ingest"

    request = urllib.request.Request(
        url,
        data=json.dumps(test_event).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    print("\nDUPLICATE EVENT")
    print(json.dumps(result, indent=2))

    assert response.status == 200
    assert result["status"] == "ignored"

    return result


def get_events():
    url = f"{BASE_URL}/api/events"

    with urllib.request.urlopen(url) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    print("\nGET EVENTS")
    print(json.dumps(result, indent=2))

    assert response.status == 200
    assert result["total_events"] >= 1

    for event in result["events"]:
        assert "event_id" in event
        assert "received_at" in event
        assert "risk" in event
        assert "response" in event


if __name__ == "__main__":
    first_result = post_event()
    duplicate_result = post_duplicate_event()
    get_events()

    print("\nComplete GuardX backend validation passed.")