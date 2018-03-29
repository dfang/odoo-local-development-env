#!/bin/sh

# docker-compose down -v && docker-compose up -d && docker logs -f odoo
# docker stop odoo && docker start odoo && docker logs -f odoo

docker-compose down -v && docker-compose up --build  --force-recreate -d

sleep 5

docker exec -ti odoo python /tmp/bootstrap_odoo_db.py

docker-compose logs -f
