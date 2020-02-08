#!/usr/bin/env python
from flask import Flask, render_template, Response, request

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

#import GPIO
import RPi.GPIO as GPIO

app = Flask(__name__)

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define actuators GPIOs
Q1 = 6
Q2 = 13
Q3 = 19
Q4 = 26

#define PWM pin
P = 18

#initialize GPIO status variables
StartSts = 0
StopSts = 0
RevSts = 0

# Define led pins as output
GPIO.setup(Q1, GPIO.OUT)   
GPIO.setup(Q2, GPIO.OUT)
GPIO.setup(Q3, GPIO.OUT)   
GPIO.setup(Q4, GPIO.OUT)

#Define PWM pin as output and as PWM pin
GPIO.setup(P, GPIO.OUT)
PuWiMo = GPIO.PWM(P,30000) #(channel, frequency)

#turn leds OFF 
GPIO.output(Q1, GPIO.LOW)
GPIO.output(Q2, GPIO.LOW)
GPIO.output(Q3, GPIO.LOW)
GPIO.output(Q4, GPIO.LOW)

PuWiMo.stop()

try: #try block to catch Interrupt	

	@app.route('/')
	def index():
	#    """Video streaming home page."""
	#    return render_template('index.html')

		# Read Sensors Status
		StartSts = not(GPIO.input(Q1)) and GPIO.input(Q2) and (GPIO.input(Q3)) and not(GPIO.input(Q4)) 
		StopSts = not(GPIO.input(Q1)) and not(GPIO.input(Q2)) and not(GPIO.input(Q3)) and not(GPIO.input(Q4))
		RevSts = GPIO.input(Q1) and not(GPIO.input(Q2)) and not(GPIO.input(Q3)) and not(GPIO.input(Q4))

		templateData = {
	              'Start'  : StartSts,
	              'Stop'  : StopSts,
	              'Rev'  :RevSts,
	        }
		return render_template('index.html', **templateData)


	def gen(camera):
	    """Video streaming generator function."""
	    while True:
	        frame = camera.get_frame()
	        yield (b'--frame\r\n'
	               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



	@app.route('/video_feed')
	def video_feed():
	    """Video streaming route. Put this in the src attribute of an img tag."""
	    return Response(gen(Camera()),
	                    mimetype='multipart/x-mixed-replace; boundary=frame')


	#GPIO
	@app.route("/<action>")
	def action(action):

	   	PuWiMo.start(0)

		if action == "Start":
			GPIO.output(Q1, GPIO.LOW)
			GPIO.output(Q2, GPIO.HIGH)
			GPIO.output(Q3, GPIO.HIGH)
			GPIO.output(Q4, GPIO.LOW)
			PuWiMo.ChangeDutyCycle(65) #Run PWM at 100% duty cycle
		if action == "Stop":
			GPIO.output(Q1, GPIO.LOW)
			GPIO.output(Q2, GPIO.LOW)
			GPIO.output(Q3, GPIO.LOW)
			GPIO.output(Q4, GPIO.LOW)
			PuWiMo.ChangeDutyCycle(0)
		if action == "Rev":
			GPIO.output(Q1, GPIO.HIGH)
			GPIO.output(Q2, GPIO.LOW)
			GPIO.output(Q3, GPIO.LOW)
			GPIO.output(Q4, GPIO.LOW)
			PuWiMo.ChangeDutyCycle(65)
	   
		StartSts = not(GPIO.input(Q1)) and GPIO.input(Q2) and (GPIO.input(Q3)) and not(GPIO.input(Q4)) 
		StopSts = not(GPIO.input(Q1)) and not(GPIO.input(Q2)) and not(GPIO.input(Q3)) and not(GPIO.input(Q4))
		RevSts = GPIO.input(Q1) and not(GPIO.input(Q2)) and not(GPIO.input(Q3)) and not(GPIO.input(Q4))

		templateData = {
	              'Start'  : StartSts,
	              'Stop'  : StopSts,
	              'Rev'  :RevSts,
	        }
		return render_template('index.html', **templateData)


	if __name__ == '__main__':
	    app.run(host='0.0.0.0', debug=True)


except:
	print "Interrupted."


finally:
	GPIO.cleanup()

