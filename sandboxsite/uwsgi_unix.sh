uwsgi -s /tmp/uwsgi.sock --file sandboxsite/wsgi.py --gevent 2000 --listen 1000 --master --pidfile /tmp/uwsgi-master.pid --workers 5

#uwsgi --chdir=. \
 #     --module=sandboxsite.wsgi:application \
 #     --env DJANGO_SETTINGS_MODULE=sandboxsite.settings \
 #     --master --pidfile=/tmp/project-master.pid \
 #     --gevent 2000 \
 #     --socket=/tmp/uwsgi.sock \
 #     --processes=5 \
 #     --max-requests=5000 \
 #     --vacuum
