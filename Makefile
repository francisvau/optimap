migrate:
	minikube kubectl -- exec -it deploy/optimap-backend -- alembic upgrade head

downgrade:
	minikube kubectl -- exec -it deploy/optimap-backend -- alembic downgrade -1

revision:
	minikube kubectl -- exec -it deploy/optimap-backend -- alembic revision --autogenerate -m "$(msg)"

reset-database:
	minikube kubectl -- exec -it deploy/optimap-postgres -- psql -U admin -d postgres -c "DROP DATABASE IF EXISTS optimap WITH (FORCE);"
	minikube kubectl -- exec -it deploy/optimap-postgres -- psql -U admin -d postgres -c "CREATE DATABASE optimap WITH OWNER admin;"
	minikube kubectl -- exec -it deploy/optimap-backend -- alembic upgrade head

wipe-database:
	minikube kubectl -- exec -it deploy/optimap-postgres -- psql -U admin -d postgres -c "DROP DATABASE IF EXISTS optimap WITH (FORCE);"
	minikube kubectl -- exec -it deploy/optimap-postgres -- psql -U admin -d postgres -c "CREATE DATABASE optimap WITH OWNER admin;"

shell-backend:
	minikube kubectl -- exec -it deploy/optimap-backend -- /bin/sh

shell-frontend:
	minikube kubectl -- exec -it deploy/optimap-frontend -- /bin/sh

shell-engine:
	minikube kubectl -- exec -it deploy/optimap-engine -- /bin/sh
