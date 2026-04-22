code := blink.py

televerser:
	./src/pyboard.py --device /dev/ttyACM0 src/$(code)

televerser-main:
	./src/pyboard.py --device /dev/ttyACM0 -f cp ./src/$(code) :main.py
