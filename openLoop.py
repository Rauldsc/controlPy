import time, math
import pandas as pd
import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

class openLoop(object):
	def __init__(self, input, output, highOrLow):
		self.input = input
		self.highOrLow = highOrLow # 1 HIGH activation, 0 LOW activation
		self.output = output
		GPIO.setup(output, GPIO.OUT)
		ADC.setup()

	def start(self, sampleTime, dutyCicle, timer):
		texp = 0
		sensor_measure = []
		timeline = []
		estimated_value =[]
		error = []
		if(self.highOrLow == 1):
			PWM.start(self.output, dutyCicle)
		else:
			PWM.start(self.output, 100 - dutyCicle)

		while True:
			sensor = ADC.read(self.input)
			data = {"Time" : timeline,"Sensor measure" : sensor_measure, "Estimates" : estimated_value, "Error" : error}
			sensor_measure.append(sensor)
			timeline.append(texp)
			time.sleep(sampleTime)
			texp = texp + sampleTime

			if texp >= timer:
				K = (sensor_measure[-1] - sensor_measure[0])/dutyCicle
				tau = timeline[np.abs(np.array(timeline) - sensor_measure[-1]*0.62).argmin()]
				for i in range(len(sensor_measure)):
					eval = K*dutyCicle*(1 - pow(math.e, timeline[i]/tau))
					estimated_value.append(eval)
					error.append(pow(sensor_measure[i] - eval , 2))
				df = pd.DataFrame(data)
				print(df)
				print("K = " + str(K))
				print("tau = " + str(tau))
				break

	def stop(self):
		if(self.highOrLow == 1):
			GPIO.output(self.output, GPIO.LOW)
		else:
			GPIO.output(self.output, GPIO.HIGH)
