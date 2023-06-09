# Using

db is sqlite3. Must be named database.db and be in the root directory of the project.

You must creat a config.py file in the root directory. Create a SECRET_KEY variable like this:
```python
SECRET_KEY = 'your_secret_key_here'
```
## Running

```bash
# install requirements
pip install -r requirements.
# create admin account in database
python database_setup.py {username} {password}
# run
python -m flask run
```