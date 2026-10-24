# 🏫 Classroom Availability Finder

A web-based Cloud Computing project that helps users find available classrooms based on the day, time, seating capacity, and required facilities.

## 🌐 Live Demo

**Live Website:** https://classroom-availability-finder.onrender.com

**GitHub Repository:** https://github.com/pavanimandati13-jpg/classroom-availability-finder

## 📌 Project Overview

The Classroom Availability Finder is designed to simplify classroom selection by allowing users to search for suitable classrooms using specific requirements. Instead of manually checking classroom schedules, users can enter their preferences and view matching availability information.

The application is built using Python and Flask, with an HTML-based user interface. It is deployed on Render to make the application accessible through a public web link.

## 🎯 Objectives

- Find classrooms based on the selected day and time.
- Filter classrooms according to seating capacity.
- Search for classrooms with required facilities.
- Provide a simple and user-friendly interface.
- Demonstrate the deployment of a Python web application using cloud hosting.

## ✨ Features

- **Classroom Search:** Search for classrooms using scheduling requirements.
- **Day and Time Filtering:** Find classrooms for a selected schedule.
- **Capacity Filtering:** Identify classrooms that meet seating requirements.
- **Facility Filtering:** Search based on available classroom facilities.
- **Web-Based Interface:** Access the application through a browser.
- **Cloud Deployment:** Access the deployed application using a public URL.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | User interface styling |
| Gunicorn | Production application server |
| Render | Cloud hosting and deployment |
| Git and GitHub | Version control and source code hosting |

## ⚙️ System Requirements

- Python 3.10 or a compatible version
- pip package manager
- Git
- A web browser
- Internet connection for cloud deployment

## 📂 Project Structure

```text
classroom-availability-finder/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── Procfile
├── .gitignore
├── templates/
│   └── index.html
└── tests/
    └── test_app.py
```

## 🚀 Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/pavanimandati13-jpg/classroom-availability-finder.git
```

### 2. Navigate to the project folder

```bash
cd classroom-availability-finder
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Start the application

```bash
python app.py
```

### 7. Open the application

Visit:

http://127.0.0.1:5000

## ☁️ Cloud Deployment

The application is deployed using Render.

**Deployment configuration:**

- **Service Type:** Web Service
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

**Live URL:** https://classroom-availability-finder.onrender.com

## 🔍 How to Use

1. Open the live website or run the application locally.
2. Enter the required day and time.
3. Specify the required seating capacity.
4. Select any required classroom facilities.
5. Submit the search.
6. Review the matching classroom results.

The results depend on the schedule data configured in the application.

## 🧪 Testing

The project includes a test file at `tests/test_app.py`.

Run the tests using:

```bash
python -m pip install pytest
python -m pytest
```

## ⚠️ Current Limitations

- The application uses sample classroom schedule data.
- Availability results may not represent the actual timetable of a college.
- Live integration with college timetable systems is not currently included.

## 🔮 Future Enhancements

- Integrate a real-time college timetable database.
- Add administrator login and classroom schedule management.
- Allow authorized users to update classroom availability.
- Add booking requests and notifications.
- Integrate college authentication and access control.

## 🎓 Academic Project

**Project Title:** Classroom Availability Finder  
**Domain:** Cloud Computing  
**Backend:** Python and Flask  
**Deployment Platform:** Render

## 👩‍💻 Author

Developed as an academic Cloud Computing project.

---

*This project demonstrates web application development, classroom search functionality, version control, and cloud deployment.*
