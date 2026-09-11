from risk_engine import risk_engine


test_events = [
    {
        "event_type": "RESTRICTED_ZONE_ENTRY"
    },
    {
        "event_type": "AGGRESSION_LIKE_EVENT"
    },
    {
        "event_type": "CROWD_ANOMALY"
    },
    {
        "event_type": "FALL_DETECTED"
    }
]


for event in test_events:
    result = risk_engine.calculate_risk(event)
    print(result)


print("\nRisk engine test passed.")