# sage-api
Sage ERP 500 - API that generates list of active users

## prerequisites
- Python 3.6 +
- pip
- venv
- git

## Create app folder/directory
```
mkdir sage-api
cd sage-api
```

## Clone the repository
```git clone https://github.com/jensonpaul/sage-api.git . ```

## Create virtual environment
```python3 -m venv venv```

## Create .env file, based on sample.env
```
copy sample.env .env
edit as needed
```

## Activate virtual environment
```
if using windows:
.\venv\scripts\activate.bat

if using linux:
source venv/bin/activate
```

## Install dependencies
```pip install -r requirements.txt```

## Run the app
```
python main.py
```

API call should be available at:
```
http://hostname:port/SageErpUsers
```

