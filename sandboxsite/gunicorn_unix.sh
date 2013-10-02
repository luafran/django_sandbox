export PATH=$PATH:.

num_cpu=`cat /proc/cpuinfo |grep processor|wc -l`
num_workers=$[ ($num_cpu*2)  +  1 ]

# UNIX
gunicorn \
      --bind unix:/tmp/gunicorn.sock -w $num_workers -k gevent --worker-connections=2000 \
        --backlog=1000 -p gunicorn.pid --log-level=critical sandboxsite.wsgi:application
