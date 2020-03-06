# cmput404-group-project
Group project for the 404, team EarlyBirds

Website URL: https://cmput404-group-project-mandala.herokuapp.com/

# Test Data
## Creating Test Data
The following command will create a copy of your database and dump it into a file for others to load

    python manage.py dumpdata --indent 2 --format yaml > test_data.yaml

## Loading Test Data
The following command will load the file created in the above command into your database

    python manage.py loaddata test_data.yaml