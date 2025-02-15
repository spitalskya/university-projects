export FLASK_APP=main
export FLASK_ENV=development

app: 
	python -m flask run --port=1739

flask_debug: 
	python -m flask run --debug --port=1739

clean_data:
	python -m data_handlers.data_cleaner

create_db:
	python -m data_handlers.database_creator

report:
	python -m processing.processing_for_report

exam:
	python -m processing.indicator_processor
