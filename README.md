# CS 4400 Project 5 - Team 2
Team Members: Aashritha Ravi, Denisha Parsons, and Saisnigdha Ganumpally

i. Instructions to setup your app
1. Clone the GitHub Repository
2. Make sure that Python 3.12 is installed
3. Install Django (pip install django)
4. Intialize a virtual enviroment in the project folder (python -m venv venv)
5. Install any dependencies
6. Create a local MySQL connection (input password)
7. Import the SQL file

ii. Instructions to run your app
1. Activate venv
2. Make sure the SQL connection exists
3. Run python manage.py runserver
4. Click the link


iii. Brief explanation of what technologies you used and how you accomplished your
application (don’t spend too much time on this)
We used Django to serve as the framework for this project. This helped create the templates for the html pages for the views and procedures. It allowed for easy url linking between the pages and the views were able to easily link to SQL. We used Django's built in database and its cursor connection in order to call the stored procedures. We pulled all the views and procedures by calling the MySQL file. The views used the input from the user and validated the information, and then called the MySQL stored procedure. So, we used Django for all the formatting and used MySQL for the database logic.


iv. Explanation of how work was distributed among the team members
Aashritha did all the setup and made the framework that Denisha and Snigdha followed. She did the setup and the first 5 procedures. Snigdha did the views and then the next two procedures and Denisha finsihed up the procedures. We all helped each other debug whenever we ran into issues. We distributed this by communicating with one another making sure that no one feels like they are doing too much work and instead created this pretty equal split of work.
