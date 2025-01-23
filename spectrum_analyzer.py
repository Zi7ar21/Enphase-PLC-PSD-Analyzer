from time import sleep
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np
import requests
import threading
import queue
from datetime import datetime

envoy_ip = '192.168.1.6'
session_id = 'Dl0qAEiIPMNuZ2HOovpFBHaNTgiVHqah'

# local Envoy server-sent events Power Line Communication samples stream
stream_url = f"https://{envoy_ip}/stream/psd"

timestamp = datetime.now().isoformat()

# set up plot
plt.ion()
plt.style.use('dark_background')
fig, ax = plt.subplots()
line1, = ax.plot([], [], linewidth=0.5)
#ax.set_xlim(0, 0.0575) # initial time range
ax.set_xlim(0, 250.0) # initial frequency range
ax.set_ylim(0, 120) # initial voltage range
ax.set_title("Power Line Communication (PLC) Power Spectral Density (PSD)")
ax.set_label(timestamp)
#x.set_xlabel("Time (s)")
ax.set_xlabel("Frequency (kHz)")
#ax.set_ylabel("Voltage (uV?)")
ax.set_ylabel("Amplitude (dBuVrms?)")
plt.grid(color = 'tab:gray')
fig.canvas.draw()
axbackground = fig.canvas.copy_from_bbox(ax.bbox)

plt.show(block=False)

shouldClose = threading.Event()

shouldClose.clear()

def get_stream():
	"""Stream Power Line Communication samples from the Envoy"""
	response = requests.get(stream_url, cookies={'sessionId': session_id}, stream=True, verify=False)

	if response.status_code == 200:
		print("Streaming PLC sample data...")
		for line in response.iter_lines():
			if line:
				#timestamp = datetime.now().isoformat()
				#print(line.decode())
				yield line.decode()
	else:
		raise Exception(f"Error: {response.status_code} - {response.text}")

data_queue = queue.Queue()

def get_data():
	stream = get_stream()
	for line in stream:
		if line.startswith("data: 0"):
			print("got data")
			data = np.hsplit(np.fromstring(line[6:].strip().replace(' ', '').rsplit(';', 1)[0].replace(';', ','), dtype=float, sep=',').reshape(-1,2),2)
			data_queue.put([data[0].ravel(), data[1].ravel()])
		if shouldClose.is_set():
			exit()
			
thread = threading.Thread(target=get_data, daemon=True)
thread.start()

def main():
	"""Stream samples and plot them"""
	samps = [0.0]
	try:
		while True:
			if plt.get_fignums():
				while not data_queue.empty():
					data = data_queue.get()
					time, val = data
					timestamp = datetime.now().isoformat()
					samps = np.append(samps, val, axis=0)
					print(len(samps))
					if(len(samps) > 1000000):
						wavfile.write(f"./out-{timestamp}.wav", int(1/((time[101]-time[0])/100)), (0.001*samps).astype(np.float32))
						samps = [0.0]
					val = np.multiply(val, np.blackman(len(val))) # apply window function
					n = len(time)
					fft_result = np.fft.fft(val)
					fft_freqs = 0.001*np.fft.fftfreq(n, d=((time[101]-time[0])/100))
					fft_result = np.abs(fft_result)[:n // 2]
					fft_freqs = fft_freqs[:n // 2]
					fft_result = 10 * np.log10(fft_result)
					#line1.set_data(time, val)
					line1.set_data(fft_freqs, fft_result)
					#ax.set_xlim(time.min(), time.max())
					#ax.set_xlim(fft_freqs.min(), fft_freqs.max())
					#ax.set_ylim(val.min() - 0.1, val.max() + 0.1)
					#ax.set_ylim(fft_result.min() - 0.1, fft_result.max() + 0.1)
				#fig.canvas.draw()
				#fig.canvas.restore_region(axbackground)
				#ax.draw_artist(line1)
				#fig.canvas.blit(ax.bbox)
				fig.canvas.flush_events()
				sleep(0.01)
			else:
				plt.close()
				shouldClose.set()
				thread.join()
	except Exception as e:
		print(f"Error: {e}")

main()
