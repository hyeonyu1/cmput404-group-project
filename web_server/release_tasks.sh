python manage.py migrate
# OBTAINED FROM STACKOVERFLOW
# Original Question Author: bogdan (https://stackoverflow.com/users/192632/bogdan)
# Answer Author: Tk421 (https://stackoverflow.com/users/998649/tk421)
# Question Page: https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'password')" | python manage.py shell
# END STACKOVERFLOW