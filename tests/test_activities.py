import pytest


def test_activity_logging_on_lifecycle(client, developer_headers, developer_user, tester_user):
    # 1. Create issue
    create_res = client.post("/api/issues", json={
        "title": "Issue with activity lifecycle",
        "priority": "LOW",
        "issue_type": "TASK"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]

    # 2. Update status
    client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=developer_headers
    )

    # 3. Assign
    client.patch(
        f"/api/issues/{issue_id}/assign",
        json={"assignee_id": tester_user.id},
        headers=developer_headers
    )

    # 4. Fetch activities for this issue
    act_res = client.get(f"/api/issues/{issue_id}/activities")
    assert act_res.status_code == 200
    activities = act_res.json()
    assert len(activities) >= 3

    action_types = [a["action_type"] for a in activities]
    assert "CREATED" in action_types
    assert "STATUS_CHANGE" in action_types
    assert "ASSIGNEE_CHANGE" in action_types

    # 5. Global recent activities endpoint
    recent_res = client.get("/api/activities/recent")
    assert recent_res.status_code == 200
    recent = recent_res.json()
    assert len(recent) >= 3
