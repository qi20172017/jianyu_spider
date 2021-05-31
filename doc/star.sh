#!/usr/bin/env bash

source_root="/projects/tar_spider"
cd ${source_root}


# systemd config
cp ${source_root}/deploy/toutiao_web.worker.service /etc/systemd/system/toutiao_web.worker.service
sed -i "s#proj_root_path#${source_root}#g" /etc/systemd/system/toutiao_web.worker.service

cp ${source_root}/deploy/toutiao_web.celerybeat.service /etc/systemd/system/toutiao_web.celerybeat.service
sed -i "s#proj_root_path#${source_root}#g" /etc/systemd/system/toutiao_web.celerybeat.service


mkdir /etc/conf.d
virtualenv=`pipenv --venv`
celery_path=${virtualenv}"/bin/celery"

# celery worker config
cp ${source_root}/deploy/toutiao_web_worker /etc/conf.d/toutiao_web_worker
sed -i "s#path_to_celery#${celery_path}#g" /etc/conf.d/toutiao_web_worker

# celery beat config
cp ${source_root}/deploy/toutiao_web_celerybeat /etc/conf.d/toutiao_web_celerybeat
sed -i "s#proj_root_path#${source_root}#g" /etc/conf.d/toutiao_web_celerybeat
sed -i "s#path_to_celery#${celery_path}#g" /etc/conf.d/toutiao_web_celerybeat


# create celery user and group and set permission
useradd -s /sbin/nologin celery
sudo mkdir /var/run/celery
sudo mkdir /var/log/celery
chown -R celery:celery /var/run/celery
chown -R celery:celery /var/log/celery


# start systemd service
systemctl enable toutiao_web.worker.service
systemctl enable toutiao_web.celerybeat.service

systemctl daemon-reload
systemctl restart toutiao_web.worker.service
systemctl restart toutiao_web.celerybeat.service

echo "deploy complete"