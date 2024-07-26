start:
	python3 main.py

create_adc:
	gcloud auth application-default login

run:
	make create_adc
	make start
