from microdot import Microdot, Response
from microdot_utemplate import render_template
import utime
from ucollections import OrderedDict

app = Microdot()
Response.default_content_type='text/html'

emp_dict={}

#LORA SEction

from ulora import LoRa, ModemConfig, SPIConfig

# Lora Parameters
RFM95_RST = 14 #reset pin on board.
RFM95_SPIBUS = SPIConfig.esp32_2
RFM95_CS = 5
RFM95_INT = 2
RF95_FREQ = 915.0 #north america
RF95_POW = 20
CLIENT_ADDRESS = 40 #this address
SERVER_ADDRESS = 20 # to address

# initialise radio
lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)


def csv_write(time_unix, user, message):
    with open('/log/messsages.csv', "a") as file:
        file.write(str(time_unix) + "," + user +"," + message + "," +"\n")
        file.close()
        
#def csv_read_in(user):
#    with open('/log/' + user + ".csv", "r") as file:
#        file.readlines(str(time_unix) + "," + user +"," + message + "," +"\n")
#        file.close()

def on_recv(payload):
    print("From:", payload.header_from)
    print("Received:", payload.message)
    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    print(payload.message)
    message_str = payload.message.decode()
    sent_time_unix = str(message_str.split("%$%")[0])
    #user= payload.message.split("%$%")[1]
    message_itself = message_str.split("%$%")[2]
    emp_dict[sent_time_unix] = (str(payload.header_from), message_itself)


    
@app.route("/",  methods=['GET', 'POST'])
def message_input(req):
    global emp_dict
    if req.method == 'POST':
        sent_time_unix = str(req.form.get('unixTime'))
        #time_machine = utime.time()+946684800+(60*60*5)
        message = str(req.form.get('textbox'))
        user=str(CLIENT_ADDRESS)
        data = sent_time_unix+"%$%"+user+"%$%"+message
        lora.send_to_wait(data, SERVER_ADDRESS)
        emp_dict[sent_time_unix]=(user, message)
        emp_dict = OrderedDict(sorted(emp_dict.items()))
        csv_write(sent_time_unix, user, message)
        print(sent_time_unix)
    return render_template('message_input.html', emp_dict= emp_dict)

lora.on_recv = on_recv
lora.set_mode_rx()


address= network.WLAN(network.STA_IF).ifconfig()[0]

print('app_running....', 'network config:', address+":5000")

if __name__ == '__main__':
    app.run()
