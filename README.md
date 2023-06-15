# About

This project was created for the Jackson-Reed Math Center so that faculty can keep track of students who attend math center and assure that students are receiving supports, especially if they have a learning plan with the school like an IEP or 504 plan. 
Some teachers may mandate that their students attend math center for various reasons and this tracker assures the students are completing this task.

# Using
Edit the file 'sample_config.py' and rename it to 'config.py'. Edit the following lines:
```python
SECRET_KEY = 'your_secret_key_here'
```
## Running


```bash
# Install dependencies
pip install -r requirements.txt
# {username} and {password} are the credentials for the admin account.
python database_setup.py {username} {password}
# Start the server
python -m flask run
```

# Notes

- This project requires python3 to be installed.
- After adding a new teacher in the admin panel, the service must be rebooted
- While the login system should be secure, it is recommended to use a different password for your teacher account.
- The access code is designed so that students cannot fake attending Math Center. However, teachers must regenerate the code in the teacher panel after every session.