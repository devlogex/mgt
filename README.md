# TodoApp - Task Management Application

A modern Django application for tracking and managing your daily tasks.

## Features

- Create, update, and delete tasks
- Set task priorities (low, medium, high)
- Track task status (pending, in progress, completed)
- Categorize tasks with custom tags
- Set due dates for tasks
- Dashboard with task statistics
- Responsive and modern UI

## Screenshots

(Screenshots will be added once the application is deployed)

## Technologies Used

- Django 5.1.7
- Bootstrap 5
- SQLite
- Font Awesome
- Crispy Forms

## Setup Instructions

1. Clone the repository:

   ```
   git clone <repo-url>
   cd mgt
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Run migrations:

   ```
   python manage.py migrate
   ```

5. Create a superuser (for admin access):

   ```
   python manage.py createsuperuser
   ```

6. Run the development server:

   ```
   python manage.py runserver
   ```

7. Access the application:
   - Todo App: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage

1. Add new tasks by clicking the "New Task" button
2. Update task details by clicking the edit (pencil) icon
3. Change task status using the status buttons
4. Delete tasks by clicking the delete (trash) icon
5. View task statistics at the top of the dashboard

## License

This project is licensed under the MIT License.

## Author

Your Name
