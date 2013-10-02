export PATH=$PATH:.

num_cpu=`cat /proc/cpuinfo |grep processor|wc -l`
num_workers=$[ ($num_cpu*2)  +  1 ]

# TCP
gunicorn \
      -b :8001 -w $num_workers -k gevent --worker-connections=2000 \
        --backlog=2000 -p gunicorn.pid --log-level=critical sandboxsite.wsgi:application

