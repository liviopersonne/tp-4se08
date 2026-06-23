pyboard := ./utils/pyboard.py
device := /dev/ttyACM0

sample := cardiac.txt
code := main.py

all:
	echo hello

init-venv:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

clean:
	$(pyboard) --device $(device) -f rm :main.py
	$(pyboard) --device $(device) -f rm :cardiac.txt
	rm -rf venv

upload-sample:
	$(pyboard) --device $(device) -f cp data/$(sample) :cardiac.txt

upload:
	$(pyboard) --device $(device) src/$(code)

upload-main:
	$(pyboard) --device $(device) -f cp ./src/$(code) :main.py
