import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
import app as appmod


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.c = appmod.app.test_client()

    def test_health(self):
        self.assertEqual(self.c.get("/health").get_json()["status"], "ok")

    def test_rooms_seeded(self):
        self.assertGreaterEqual(len(self.c.get("/api/rooms").get_json()), 10)

    def test_availability_partitions_rooms(self):
        d = self.c.get("/api/availability?date=2026-10-26&start=09:00&end=10:00").get_json()
        self.assertEqual(len(d["free"]) + len(d["busy"]), 12)

    def test_bad_input(self):
        self.assertEqual(self.c.get("/api/availability?date=bad&start=09:00").status_code, 400)
        self.assertEqual(self.c.get("/api/availability?date=2026-10-26&start=10:00&end=09:00").status_code, 400)

    def test_booking_conflict_and_cancel(self):
        free = self.c.get("/api/availability?date=2026-11-01&start=09:00&end=10:00").get_json()["free"]  # Sunday: no classes
        rid = free[0]["id"]
        body = dict(room_id=rid, date="2026-11-01", start="09:00", end="10:00", booked_by="Tester")
        r = self.c.post("/api/bookings", json=body)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.c.post("/api/bookings", json=body).status_code, 409)
        self.assertEqual(self.c.delete(f"/api/bookings/{r.get_json()['id']}").status_code, 200)
        self.assertEqual(self.c.post("/api/bookings", json=body).status_code, 201)


if __name__ == "__main__":
    unittest.main()
