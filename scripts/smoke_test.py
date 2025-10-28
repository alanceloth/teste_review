import os
import shutil
import sys

# Ensure project root is on sys.path when running from scripts/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient


def main() -> int:
    # Backup existing DB, if any, to avoid altering user data during smoke test
    db_path = "tasks.db"
    backup_path = "tasks.db.backup"
    restored = False

    if os.path.exists(db_path):
        if os.path.exists(backup_path):
            os.remove(backup_path)
        shutil.move(db_path, backup_path)

    try:
        from app.main import app

        client = TestClient(app)

        # Register user
        reg = client.post(
            "/auth/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )
        assert reg.status_code in (200, 201), reg.text

        # Login form
        login = client.post(
            "/auth/login",
            data={"username": "alice", "password": "secret123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        auth = {"Authorization": f"Bearer {token}"}

        # Me
        me = client.get("/auth/me", headers=auth)
        assert me.status_code == 200, me.text
        assert me.json()["username"] == "alice"

        # Create task
        create = client.post(
            "/tasks/",
            json={"title": "Pagar contas", "description": "Luz e água"},
            headers=auth,
        )
        assert create.status_code == 201, create.text
        task = create.json()
        task_id = task["id"]

        # List tasks
        lst = client.get("/tasks/", headers=auth)
        assert lst.status_code == 200, lst.text
        assert any(t["id"] == task_id for t in lst.json())

        # Get by id
        get1 = client.get(f"/tasks/{task_id}", headers=auth)
        assert get1.status_code == 200, get1.text

        # Update
        upd = client.put(
            f"/tasks/{task_id}", json={"completed": True}, headers=auth
        )
        assert upd.status_code == 200, upd.text
        assert upd.json()["completed"] is True

        # Delete
        dele = client.delete(f"/tasks/{task_id}", headers=auth)
        assert dele.status_code == 204, dele.text

        # Confirm 404
        get2 = client.get(f"/tasks/{task_id}", headers=auth)
        assert get2.status_code == 404, get2.text

        print("SMOKE TEST OK")
        return 0
    finally:
        # Dispose engine to release SQLite file handles on Windows
        try:
            from app.database import engine as db_engine

            db_engine.dispose()
        except Exception:
            pass

        # Restore previous DB if it existed
        if os.path.exists(backup_path):
            if os.path.exists(db_path):
                os.remove(db_path)
            shutil.move(backup_path, db_path)
            restored = True
        if restored:
            print("Restored original tasks.db after test.")


if __name__ == "__main__":
    raise SystemExit(main())
