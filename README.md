# Foresight Health Provider Matching & Appointment Request API

## Project Overview

This project analyzes Foresight Health, a healthcare website focused on mental health services, and implements a backend MVP for provider matching and appointment request management.

## Business Domain

Healthcare / Mental Health Services

## Website Analysis

Foresight Health helps patients find mental health providers and request care. The main users are patients, providers, and admin/support staff.

## Core Business Needs

- Provider discovery
- Provider matching based on patient needs
- Appointment request management
- Appointment status tracking
- Admin/provider review of incoming requests

## Selected Business Need

Provider matching and appointment request management.

## MVP Scope

Patients can:
- register and log in
- view providers
- submit provider match preferences
- receive matched providers
- create appointment requests
- view their own appointment requests
- cancel appointment requests

Admins/providers can:
- update appointment request status

## Main Resources

- User
- Provider
- ProviderMatchRequest
- AppointmentRequest

## Business Endpoints

- GET /providers
- GET /providers/{provider_id}
- POST /provider-matches
- POST /appointment-requests
- GET /appointment-requests/me
- PATCH /appointment-requests/{request_id}/status
- DELETE /appointment-requests/{request_id}

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT authentication
- Docker
- AWS EC2