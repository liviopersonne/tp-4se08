code := blink.py
pyboard := ./utils/pyboard.py
device := /dev/ttyACM0

all:
	echo hello

init-venv:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

clean:
	rm -rf venv

upload:
	$(pyboard) --device $(device) src/$(code)

upload-main:
	$(pyboard) --device $(device) -f cp ./src/$(code) :main.py

remove-main:
	$(pyboard) --device $(device) -f rm :main.py