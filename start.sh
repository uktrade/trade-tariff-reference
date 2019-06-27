#!/bin/bash -xe



sleep infinity

echo "docker exec -it dit_helpdesk_helpdesk_1 /bin/bash"
echo "python manage.py scrape_section_hierarchy_v2"
#python manage.py scrape_section_hierarchy_v2

# -----------------------------------------------------------------------------
# To destroy and rebuild:
# -----------------------------------------------------------------------------
# $ docker-compose stop
# $ docker-compose rm
# $ docker-compose build
# $ docker-compose up
# -----------------------------------------------------------------------------
