# Classroom Availability Finder (Cloud Computing Project)

A Flask web service that tells students and staff which classrooms, labs and halls are free
for a chosen date and time. It checks the weekly timetable plus one-off bookings, and lets
users book a free room. Packaged with Docker so it can run on any cloud.

## Features
- Search free rooms by date, time range, building, room type and minimum capacity
- "Free right now" one-click search (server timezone defaults to Asia/Kolkata, change with `APP_TZ`)
- Book / cancel rooms with conflict detection (HTTP 409 on clashes)
- REST API + single-page responsive UI (light/dark)
- `/health` endpoint for load balancer health checks
- Seeded sample data: 12 rooms across Blocks A, B, C with a Mon-Sat timetable

## Architecture
Browser -> Load balancer / reverse proxy -> Gunicorn + Flask (container) -> SQLite (file on a volume).
For multi-instance production, swap SQLite for a managed database (e.g. Amazon RDS / Cloud SQL).

## Run locally
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
python -m unittest discover tests
```

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/availability?date=YYYY-MM-DD&start=HH:MM&end=HH:MM&building=&type=&min_capacity=` | Free and occupied rooms |
| GET | `/api/rooms` | List all rooms |
| GET/POST | `/api/bookings` | List (`?date=`) / create booking |
| DELETE | `/api/bookings/<id>` | Cancel booking |
| GET | `/health` | Health check |

POST body: `{"room_id":1,"date":"2026-10-26","start":"14:00","end":"15:00","booked_by":"Name","purpose":"Study group"}`

## Deploy to the cloud
**Docker (any VM, e.g. AWS EC2):**
```
docker build -t classroom-finder .
docker run -d -p 80:8080 -v classroom-data:/data classroom-finder
```
**AWS EC2:** launch an Ubuntu t2.micro, open port 80 in the security group, install Docker, run the commands above.
**AWS Elastic Beanstalk:** `eb init -p python-3.12 classroom-finder && eb create classroom-env` (uses `Procfile`).
**Google Cloud Run:** `gcloud run deploy classroom-finder --source . --allow-unauthenticated --region asia-south1`
(Cloud Run storage is ephemeral, so use Cloud SQL for persistent data.)
**Render / Railway:** connect the Git repo; build command `pip install -r requirements.txt`, start command from `Procfile`.

## Cloud concepts demonstrated
IaaS/PaaS deployment, containerization, stateless web tier, health checks, environment-based configuration,
horizontal scaling (with a managed DB), REST over HTTP.
