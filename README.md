# Clinical Intake Assistant

A Django-based AI-powered clinical intake assistant designed to guide patients through structured history taking, generate summaries, differentials, and provide triage recommendations.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Technologies Used](#technologies-used)  
- [Architecture](#architecture)  
- [Setup & Installation](#setup--installation)  
- [API Endpoints](#api-endpoints)  
- [Usage](#usage)  
---

## Project Overview

This project simulates a clinical intake workflow where patients provide their medical history through a chat interface. The system:

- Collects **biodata**, **presenting complaints**, **history of presenting complaint (HPC)**, **past medical history**, **drug/allergy history**, and **social history**.  
- Uses an **LLM (large language model)** to conduct HPC and generate final clinical summaries.  
- Provides **triage classification** using both hardcoded rules and LLM evaluation.  
- Stores structured session data for each patient.  

---

## Features

- Guided step-by-step patient history collection  
- LLM-powered history of presenting complaint  
- Automatic generation of:  
  - Clinical summary  
  - Differentials with confidence levels (High/Medium/Low)  
  - Triage level  
- Session persistence with ability to resume  
- Real-time triage detection during conversation  
- REST API endpoints for integration with frontend interfaces  

---

## Technologies Used

- **Backend:** Django, Django Ninja, Django Ninja JWT  
- **Database:** SQLite (or PostgreSQL)  
- **AI Integration:** OpenAI API for LLM-based HPC and summary  
- **Frontend (optional):** HTMX, Tailwind CSS, DaisyUI for chat interface  
- **Python Libraries:** `requests`, `pydantic`, `re`  

---

## Setup & Installation

Follow these steps to get the Clinical Intake Assistant up and running locally:

### 1. Clone the repository

git clone https://github.com/yourusername/clinical-intake-assistant.git
cd clinical-intake-assistant


### 2. Create a virtual environment

python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment variables

Create a .env file in the project root or export directly:

export OPENAI_API_KEY="your_openai_api_key"

### 5. Apply database migrations
python manage.py migrate

### 6. Run the development server
python manage.py runserver

The server should now be running at: http://127.0.0.1:8000/



## API Endpoints

### Authentication

| Endpoint           | Method | Description                                         |
|-------------------|--------|-----------------------------------------------------|
| `/register/`       | POST   | Register a new user                                 |
| `/token/pair/`     | POST   | Obtain JWT access and refresh tokens for a user    |

### Session Management

| Endpoint                          | Method | Description                                                      |
|----------------------------------|--------|------------------------------------------------------------------|
| `/sessions/`                      | POST   | Create a new session                                             |
| `/sessions/{session_id}/message/` | POST   | Send a message from the user and receive assistant response      |
| `/sessions/{session_id}/summary/` | GET    | Generate final summary, differentials, and triage for a completed session |



## Usage

1. Start a new session by calling `/sessions/`
2. Respond to assistant prompts using `/sessions/{session_id}/message/`
3. After completing all history sections, retrieve the final summary using `/sessions/{session_id}/summary/`


## Example JSON Interactions

### 1. Register a New User

**Endpoint:** `/register/`  
**Method:** POST  

**Request:**

{
  "username": "johndoe",
  "password": "strongpassword123"
}

**Response:**

{
  "message": "User registered successfully.",
  "username": user.username
}



### 2. Obtain JWT Token

Endpoint: /token/pair/
Method: POST

**Request:**

{
  "username": "johndoe",
  "password": "strongpassword123"
}


**Response:**

{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}

### 3. Create a New Session

Endpoint: /sessions/
Method: POST
Headers: Authorization: Bearer <jwt_access_token>

**Request:**

{
  "username": "johndoe",
  "password": "strongpassword123"
}


**Response:**

{
  "session_id": 1,
  "message": "Hello, What's your full name please?",
  "current_section": "biodata",
  "triage_level": "Routine",
  "session_active": true
}


### 4. Send Message

Endpoint: /sessions/{session_id}/message
Method: POST
Headers: Authorization: Bearer <jwt_access_token>

**Request:**

{
  "text": "John Doe"
}


**Response:**

{
  "message": "Please enter your age.",
  "current_section": "biodata",
  "triage_level": "Routine",
  "session_active": true
}


### 5. Get Summary (After Completing All Sections):

Endpoint: /sessions/{session_id}/summary
Method: GET
Headers: Authorization: Bearer <jwt_access_token>


**Response:**

```json
{
  "id": 1,
  "hpc_summary": "30-year-old male presents with cough for 1 week...",
  "differentials": [
    {"diagnosis": "Acute Bronchitis", "confidence": "High"},
    {"diagnosis": "Pneumonia", "confidence": "Medium"}
  ],
  "triage_level": "Urgent"
}

