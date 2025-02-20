
# Training Management System

## Overview
A comprehensive training management system that helps organizations manage their training programs efficiently. The system handles training brochures, plans, needs assessment, and course management.

## Features

### 1. Training Brochure Management [AF01]
- Create and manage training brochures
- Automatic generation of brochure numbers (format: CPxxxx)
- Track course schedules and registration deadlines
- Manage both company-provided and factory training courses

### 2. Training Plan Management [AF02]
- Create and manage training plans
- Approval workflow for training plans
- Email notifications
- Print training plan documents

### 3. Training Need Assessment [AF03]
- Create and manage training needs
- Approval workflow
- Email notification system

### 4. Training Course Management [AF04]
- Course creation and management
- Approval workflow
- Print course documentation

## System Architecture

### Data Models

#### Training Brochure
- Unique identifier (code: CPxxxx format)
- Description
- Year
- Course registration deadline
- Creator information
- Company information
- Course details (start date, end date)

#### Course Types
1. Company Provided Training
   - Course details
   - Schedule information
   - Registration periods

2. Factory Training
   - Course information
   - Training schedule
   - Facility requirements

## User Roles and Access
- HR Department
- Managers
- Employees
- Training Coordinators

## Technical Requirements
- Odoo Framework
- Python
- PostgreSQL Database

## Status Management
Courses can have different statuses:
- Active
- In Progress
- Completed
- Cancelled

## Security Features
- Role-based access control
- Approval workflows
- Data validation

## Documentation
For detailed information about specific features:
- Training Plan Blueprint
- Training Need Assessment Documentation
- Course Management Guidelines

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[License Information]

## Support
For support queries, please contact [Contact Information]