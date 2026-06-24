pyboard := ./utils/pyboard.py
device := /dev/ttyACM0

sample_data := cardiac.txt
sample_code := sample.py
analysis_code := analysis.py
screen_code := ST7735.py
code := main.py

all: upload-code

init-venv:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

clean:
	-$(pyboard) --device $(device) -f rm :main.py
	-$(pyboard) --device $(device) -f rm :$(sample_code)
	-$(pyboard) --device $(device) -f rm :$(analysis_code)
	-$(pyboard) --device $(device) -f rm :$(screen_code)
	-$(pyboard) --device $(device) -f rm :$(sample_data)
	-rm -rf venv

upload-sample:
	$(pyboard) --device $(device) -f cp data/$(sample_data) :$(sample_data)

upload-code:
	$(pyboard) --device $(device) -f cp ./src/$(sample_code) :$(sample_code)
	$(pyboard) --device $(device) -f cp ./src/$(analysis_code) :$(analysis_code)
	$(pyboard) --device $(device) -f cp ./src/$(screen_code) :$(screen_code)
	$(pyboard) --device $(device) -f cp ./src/$(code) :main.py

run: upload-code
	$(pyboard) --device $(device) src/$(code)

test:
	python src/test.py