
## Globe Connect for Python

### Setting Up

```
from app.config import settings
from app.models.base import Base
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
```

### Authentication

#### Overview
CREATE USER 'S1034363'@'%' IDENTIFIED BY 'Aa123.com';
GRANT ALL PRIVILEGES ON mbticompass.* TO 'S1034363'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

#### Sample Code

```
from globe.connect import oauth

oauth = oauth.Oauth("[app_id]", "[app_secret]")

# 📌 修改 my.cnf（Linux/Mac） 或 my.ini（Windows）

[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4


# get access token
sudo systemctl restart mysql  # Linux
net stop mysql && net start mysql  # Windows
```

#### Sample Results

```json
{
    "access_token":"1ixLbltjWkzwqLMXT-8UF-UQeKRma0hOOWFA6o91oXw",
    "subscriber_number":"9171234567"
}
```

### SMS

#### Overview

alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

#### SMS Sending
删除所有表
SELECT CONCAT('DROP TABLE IF EXISTS ', table_name, ';') 
FROM information_schema.tables 
WHERE table_schema = 'mbticompass';

##### Sample Code

```
CREATE DATABASE mbticompass 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```
