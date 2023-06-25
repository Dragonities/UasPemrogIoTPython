import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from matplotlib.widgets import Button
from collections import deque
from datetime import datetime
import time



topicpub_temp = "4171/dht11/temp"
topicpub_hum = "4171/dht11/hum"
topicpub_ldr = "4171/ldr"
topicpub_random = "4171/random"
topicpub_relay = "4171/relay"

broker = "192.168.41.71"
client = mqtt.Client("Client0101")

temperature_data = deque(maxlen=5)
humidity_data = deque(maxlen=5)
ldr_data = deque(maxlen=5)
current_times = deque(maxlen=5)
random_data = deque(maxlen=5)

bar_data = [100]

fig, (axLDR, ax, axBar) = plt.subplots(3, 1, figsize=(13, 12))
plt.subplots_adjust(top=0.85,
bottom=0.155,
left=0.125,
right=0.9,
hspace=0.515,
wspace=0.2)

def update_LDR():
    axLDR.clear()
    axLDR.plot(current_times, ldr_data, label='Nilai LDR')
    axLDR.set_xlabel('Time')
    axLDR.set_ylabel('Value')
    axLDR.set_title('LDR Sensor Data')
    axLDR.legend()  

    # Menambahkan teks jika nilai LDR di bawah 40
    if ldr_data[-1] < 50:
        axLDR.text(0.15, 0.15, 'Lampu Menyala', ha='right', va='top', transform=axLDR.transAxes,
                   fontsize=12, color='red')
        
    plt.draw()

def update_temp_hum():
    if len(temperature_data) == len(humidity_data):
        ax.clear()
        ax.plot(current_times, temperature_data, label='Temperature')
        ax.plot(current_times, humidity_data, label='Humidity')
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature / Humidity')
        ax.set_title('DHT Sensor Data', pad=-30)
        ax.legend()
        plt.draw()

    else:
        ax.clear()
        ax.text(0.5, 0.5, 'Tunggu sebentar', ha='center', va='center')
        ax.set_axis_off()
        plt.draw()

def update_bar():
    axBar.clear()
    axBar.bar(["Random"], bar_data)
    axBar.set_ylabel("Jumlah")
    axBar.set_title("Jumlah Pengunjung", pad=10)
    axBar.set_ylim(0, 100)
    axBar.text(0, 14, str(bar_data[0]), ha="center", va="center")
    plt.draw()

def time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_times.append(current_time)

def on_message(client, userdata, message):
    data = float(message.payload.decode("utf-8"))

    if message.topic == topicpub_temp:
        time()
        temperature_data.append(data)
        print(temperature_data)
        update_temp_hum()

    elif message.topic == topicpub_hum:
        humidity_data.append(data)
        print(humidity_data)
        update_temp_hum()

    elif message.topic == topicpub_ldr:
        ldr_data.append(data)
        print(ldr_data)
        update_LDR()

    elif message.topic == topicpub_random:
        random_data.append(int(data))
        bar_data[0] = int(data)
        print(random_data)
        update_bar()

def publish_message(message):
    client.publish(topicpub_relay, message)

button_on_ax = plt.axes([0.51, 0.05, 0.1, 0.05])
button_on = Button(button_on_ax, 'Keluar')
button_on.on_clicked(lambda event: publish_message("nyala"))

button_off_ax = plt.axes([0.4, 0.05, 0.1, 0.05])
button_off = Button(button_off_ax, 'Masuk')
button_off.on_clicked(lambda event: publish_message("mati"))

client.connect(broker)
client.subscribe(topicpub_temp)
client.subscribe(topicpub_hum)
client.subscribe(topicpub_ldr)
client.subscribe(topicpub_random)

client.on_message = on_message
client.loop_start()

fig.suptitle('Dashboard Monitoring Tempat Parkir', fontsize=16, y=0.95, ha='center')
fig.subplots_adjust(top=0.85)  # Menyesuaikan jarak judul dari atas

plt.show()
