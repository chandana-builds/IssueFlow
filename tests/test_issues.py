import pytest


def test_create_issue_success(client, developer_headers, developer_user):
    payload = {
        "title": "Fix navbar CSS overflow on Safari",
        "description": "The flexbox wrapper causes horizontal scrolling on Webkit browsers.",
        "priority": "HIGH",
        "issue_type": "BUG",
        "tags": "frontend,safari,css"
    }
    response = client.post("/api/issues", json=payload, headers=developer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["issue_key"].startswith("ISF-")
    assert data["status"] == "OPEN"
    assert data["priority"] == "HIGH"
    assert data["reporter_id"] == developer_user.id


def test_create_issue_validation_error(client, developer_headers):
    # Short title should fail pydantic min_length=3
    response = client.post("/api/issues", json={"title": "hi"}, headers=developer_headers)
    assert response.status_code == 422


def test_list_and_filter_issues(client, developer_headers, developer_user, tester_user):
    # Create 3 issues with different status/priorities
    client.post("/api/issues", json={
        "title": "Issue 1 Critical Bug",
        "priority": "CRITICAL",
        "issue_type": "BUG",
        "assignee_id": developer_user.id
    }, headers=developer_headers)

    client.post("/api/issues", json={
        "title": "Issue 2 Low Feature",
        "priority": "LOW",
        "issue_type": "FEATURE",
        "assignee_id": tester_user.id
    }, headers=developer_headers)

    # Filter by priority
    res_crit = client.get("/api/issues?priority=CRITICAL")
    assert res_crit.status_code == 200
    crit_items = res_crit.json()["items"]
    assert len(crit_items) == 1
    assert crit_items[0]["priority"] == "CRITICAL"

    # Filter by assignee
    res_assignee = client.get(f"/api/issues?assignee_id={developer_user.id}")
    assert res_assignee.status_code == 200
    items = res_assignee.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Issue 1 Critical Bug"

    # Search filter
    res_search = client.get("/api/issues?search=Feature")
    assert res_search.status_code == 200
    assert len(res_search.json()["items"]) == 1


def test_update_issue_status(client, developer_headers):
    create_res = client.post("/api/issues", json={
        "title": "Issue to update status",
        "priority": "MEDIUM"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]

    # Transition to IN_PROGRESS
    patch_res = client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=developer_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "IN_PROGRESS"

    # Transition to RESOLVED
    res2 = client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "RESOLVED"},
        headers=developer_headers
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "RESOLVED"


def test_assign_issue(client, developer_headers, tester_user):
    create_res = client.post("/api/issues", json={
        "title": "Unassigned Issue",
        "priority": "MEDIUM"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]
    assert create_res.json()["assignee_id"] is None

    # Assign to tester
    assign_res = client.patch(
        f"/api/issues/{issue_id}/assign",
        json={"assignee_id": tester_user.id},
        headers=developer_headers
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assignee_id"] == tester_user.id


def test_delete_issue_permissions(client, developer_headers, admin_headers, tester_headers):
    # Developer creates issue
    create_res = client.post("/api/issues", json={
        "title": "Issue for deletion test",
        "priority": "LOW"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]

    # Tester tries to delete developer's issue (should be forbidden)
    del_forbidden = client.delete(f"/api/issues/{issue_id}", headers=tester_headers)
    assert del_forbidden.status_code == 403

    # Admin deletes issue (permitted)
    del_admin = client.delete(f"/api/issues/{issue_id}", headers=admin_headers)
    assert del_admin.status_code == 200

    # Ensure it is gone
    get_res = client.get(f"/api/issues/{issue_id}")
    assert get_res.status_code == 404
