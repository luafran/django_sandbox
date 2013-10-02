uwsgi --http :8002 --file sandboxsite/wsgi.py --gevent 2000 --listen 10 --master --pidfile /tmp/uwsgi-master.pid --workers 5 -L
