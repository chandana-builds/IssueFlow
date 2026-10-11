import pytest


def test_dashboard_stats_empty(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_issues"] == 0
    assert data["resolution_rate_percent"] == 0.0
    assert data["status_counts"]["OPEN"] == 0


def test_dashboard_stats_populated(client, developer_headers, developer_user):
    # Create 1 OPEN issue and 1 RESOLVED issue
    res1 = client.post("/api/issues", json={
        "title": "Bug 1",
        "priority": "HIGH",
        "issue_type": "BUG",
        "assignee_id": developer_user.id
    }, headers=developer_headers)

    res2 = client.post("/api/issues", json={
        "title": "Bug 2",
        "priority": "LOW",
        "issue_type": "FEATURE",
        "assignee_id": developer_user.id
    }, headers=developer_headers)
    issue2_id = res2.json()["id"]

    # Mark issue 2 as resolved
    client.patch(
        f"/api/issues/{issue2_id}/status",
        json={"status": "RESOLVED"},
        headers=developer_headers
    )

    # Fetch dashboard stats with auth headers
    stats_res = client.get("/api/dashboard/stats", headers=developer_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()

    assert stats["total_issues"] == 2
    assert stats["open_issues"] == 1
    assert stats["resolved_issues"] == 1
    assert stats["resolution_rate_percent"] == 50.0
    assert stats["priority_counts"]["HIGH"] == 1
    assert stats["priority_counts"]["LOW"] == 1
    assert stats["type_counts"]["BUG"] == 1
    assert stats["type_counts"]["FEATURE"] == 1

    # Personal metrics
    assert stats["my_assigned_open"] == 1  # 1 open assigned to developer_user
    assert stats["my_reported_total"] == 2
