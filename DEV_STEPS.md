# UCI Study Spot Finder

## Database
### Populating Databse
1. ```sqlite3 data/database/app.db < data/database/schema.sql```
2. ```python utils/json_to_db.py```

### Verify that Database is Populated
1. Open the database: ```sqlite3 data/database/app.db```
2. Type SQL commands to get some info.
3. Exit database: ```.quit```


## Index
### Building Index
1. Run ```python utils/build_filters_index.py```