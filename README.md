#Employee Management System
##Overview
This Employee Management System is a comprehensive web application designed to facilitate various aspects of employee and task management within an organization. Developed using Python and Django, this system allows managers and HR personnel to efficiently manage tasks, track employee progress, and maintain up-to-date employee records.

##Features
##Managerial Features
**Task Assignment:** Managers can assign tasks to employees, setting clear expectations and responsibilities.
**Progress Tracking:** Enables managers to monitor the progress of tasks to ensure timely completion.
**Task Modification:** Allows for the deletion and reassignment of tasks as per changing requirements.
**Feedback Provision:** Managers can provide constructive feedback on completed tasks to foster employee growth.
**Historical Data Access:** Access to historical task performance data for comprehensive team performance assessment.
##HR Features
**Employee Onboarding:** HR personnel can add new employees to the system, ensuring the employee database remains current.
**Record Maintenance:** Detailed entry and updating of employee information for complete record-keeping.
**Inactive Status:** Capability to mark former employees as inactive to maintain database integrity.
##Whistleblower Features
**Report Submission:** Employees can anonymously submit whistleblower reports to highlight concerns.
**Feedback and Tracking:** HR managers can provide feedback on and track the progress of whistleblower reports, maintaining transparency and accountability.
##Employee Features
**Task Management:** Employees can view their assigned tasks, update task progress, and request clarifications to ensure effective task completion.
**Performance Feedback:** Access to feedback on completed tasks for personal development.
**Workload Prioritization:** Tools to prioritize tasks based on urgency and importance.
## Installation

1. **Clone the Repository**: First, clone the repository to your local machine using the following command:

    ```bash
    git clone [repository-url]
    ```

    Replace `[repository-url]` with the actual URL of your project's repository.

2. **Install Dependencies**: Once you have cloned the repository, navigate to the project directory and install the required dependencies using:

    ```bash
    pip install -r requirements.txt
    ```

    This command will automatically install all the Python packages listed in the `requirements.txt` file, ensuring your project has all the necessary libraries.

3. **Database Migrations**: To set up your database schema, run the following Django command:

    ```bash
    python manage.py migrate
    ```

    This will apply all the migrations to your database, creating the necessary tables for your application.

4. **Run the Development Server**: Finally, you can start the Django development server using:

    ```bash
    python manage.py runserver
    ```

    This command starts a local web server. You can access your application by navigating to `http://127.0.0.1:8000/` in your web browser.

Follow these steps to set up your environment and start using the Employee Management System.

#Usage
Navigate to http://127.0.0.1:8000/ in your web browser to access the Employee Management System. Use the login credentials provided to you by the system administrator to access the respective functionalities based on your role within the organization.

Contributing
We welcome contributions to the Employee Management System. Please read our contributing guidelines before submitting pull requests.

Acknowledgments
We would like to express our gratitude to all team members and contributors who have been part of this project.
