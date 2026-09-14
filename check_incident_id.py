from backend.app.main import generate_incident_id


for _ in range(5):
    print(generate_incident_id())