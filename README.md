# DSCI 551 Project: Find Your New Place of Living

## Project Overview
This project aims to develop a distributed database system to manage a large-scale house rent dataset with MySQL. The web application allows administrators and end users to interact with the database efficiently, supporting scalability, performance, and reliability.

## Environment Setup
1. **Install Python Packages:** Ensure Python is installed on your system, then install the required packages:
   \```bash
   pip install -r requirements.txt
   \```

2. **Database Configuration:** Set up MySQL databases as described in the project report and ensure they are accessible through the configured connections in the application.

3. **Running the Application:**
   - Navigate to the project directory.
   - Run `Controller.py` to start the Flask server:
     \```bash
     python Controller.py
     \```

## Frontend Overview
The frontend is built using HTML, CSS, and JavaScript. It includes various pages like the login page, dashboard, and data management interfaces, which interact with the backend Flask application.

## Backend Overview
The backend is managed by `Controller.py`, which handles routing and interactions with the MySQL databases. It includes authentication mechanisms, data upload functionality, and CRUD operations on the house rent dataset.
