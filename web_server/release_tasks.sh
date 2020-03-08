python manage.py migrate
# OBTAINED FROM STACKOVERFLOW
# Original Question Author: planetp (https://stackoverflow.com/users/275088/planetp)
# Answer Author: Eugene Yarmash (https://stackoverflow.com/users/244297/eugene-yarmash)
# Question Page: https://stackoverflow.com/questions/39744593/how-to-create-a-django-superuser-if-it-doesnt-exist-non-interactively
cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()  # get the currently active user model,

User.objects.filter(username='admin').exists() or \
    User.objects.create_superuser('admin', 'admin@example.com', 'pass')
EOF
# END STACKOVERFLOW