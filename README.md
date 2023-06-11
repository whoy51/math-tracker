# Using
You must creat a config.py file in the root directory. Create a SECRET_KEY variable like this:
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