pyboard := ./utils/pyboard.py
device := /dev/ttyACM0

sample_data := cardiac.txt
sample_code := sample.py
code := main.py

all: run

init-venv:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

clean:
	$(pyboard) --device $(device) -f rm :main.py
	$(pyboard) --device $(device) -f rm :cardiac.txt
	rm -rf venv

upload-sample:
	$(pyboard) --device $(device) -f cp src/$(sample_code) :sample.py
	$(pyboard) --device $(device) -f cp data/$(sample_data) :cardiac.txt

upload-main:
	$(pyboard) --device $(device) -f cp ./src/$(code) :main.py

run:
	$(pyboard) --device $(device) src/$(code)

test:
	python src/test.py