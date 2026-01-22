# UCI Study Spot Finder

## Populating Databse
1. sqlite3 data/database/app.db < data/database/schema.sql
2. python json_to_db.py

## Verify that Database is Populated
1. Open the database: ```sqlite3 data/database/app.db```
2. Type SQL commands to get some info.
3. Exit database: ```.quit```