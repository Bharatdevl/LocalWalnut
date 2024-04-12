############## Deployment Section ##########################
# DO NOT MAKE ANY CHANGES HERE UNTIL YOU KNOW WHAT TO DO ###

#down
down:
	sudo docker compose --project-name walnuteq_staging -f docker-compose.test.yml down

# build
build:
	sudo docker compose --project-name walnuteq_staging -f docker-compose.test.yml up --build -d

# django migrate
migrate:
	sudo docker exec -it walnutv2-test-webapp python manage.py makemigrations
	sudo docker exec -it walnutv2-test-webapp python manage.py migrate

# collectstatic
collectstatic:
	sudo docker exec -it walnutv2-test-webapp python manage.py collectstatic --no-input

# create super user
createsuperuser:
	sudo docker exec -it walnutv2-test-webapp python manage.py createsuperuser

# create migration directories for the app (for every new app add the migration folder with __init__.py here)
create:
	@echo Creating migration folder
	@mkdir -p company/migrations && touch company/migrations/__init__.py
	@mkdir -p employee/migrations && touch employee/migrations/__init__.py
	@mkdir -p services/migrations && touch services/migrations/__init__.py
	@mkdir -p scheduler/migrations && touch scheduler/migrations/__init__.py
	@mkdir -p survey/migrations && touch survey/migrations/__init__.py
	@mkdir -p curriculum/migrations && touch curriculum/migrations/__init__.py
	@mkdir -p dashboard/migrations && touch dashboard/migrations/__init__.py

# deployment for the project
deploy: down create build migrate collectstatic
