import pytest


def test_add_and_list_comments(client, developer_headers, developer_user):
    # Create issue
    create_res = client.post("/api/issues", json={
        "title": "Issue for comment discussion",
        "priority": "MEDIUM"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]

    # Add comment
    comment_payload = {"content": "This is a detailed comment about the reproduction steps."}
    comment_res = client.post(
        f"/api/issues/{issue_id}/comments",
        json=comment_payload,
        headers=developer_headers
    )
    assert comment_res.status_code == 201
    comment_data = comment_res.json()
    assert comment_data["content"] == comment_payload["content"]
    assert comment_data["author_id"] == developer_user.id
    comment_id = comment_data["id"]

    # Fetch comments
    list_res = client.get(f"/api/issues/{issue_id}/comments")
    assert list_res.status_code == 200
    comments = list_res.json()
    assert len(comments) == 1
    assert comments[0]["id"] == comment_id

    # Verify detail view includes comment
    detail_res = client.get(f"/api/issues/{issue_id}")
    assert detail_res.status_code == 200
    assert len(detail_res.json()["comments"]) == 1


def test_delete_comment_authorization(client, developer_headers, tester_headers):
    # Developer creates issue and comment
    create_res = client.post("/api/issues", json={
        "title": "Issue with comment to delete",
        "priority": "LOW"
    }, headers=developer_headers)
    issue_id = create_res.json()["id"]

    comment_res = client.post(
        f"/api/issues/{issue_id}/comments",
        json={"content": "Author comment to test deletion"},
        headers=developer_headers
    )
    comment_id = comment_res.json()["id"]

    # Tester tries to delete developer's comment (forbidden)
    del_forbidden = client.delete(f"/api/comments/{comment_id}", headers=tester_headers)
    assert del_forbidden.status_code == 403

    # Developer deletes their own comment (allowed)
    del_ok = client.delete(f"/api/comments/{comment_id}", headers=developer_headers)
    assert del_ok.status_code == 200

    # Ensure comment is removed
    get_res = client.get(f"/api/issues/{issue_id}/comments")
    assert len(get_res.json()) == 0
