.PHONY: install data run test clean
install:
	pip install -r requirements.txt
data:
	python download_data.py
run:
	streamlit run app.py
test:
	python -m unittest discover -s tests -v
clean:
	rm -rf data/*.csv data/*.geojson __pycache__ */__pycache__
