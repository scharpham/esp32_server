from microdot import Microdot, Response
from microdot_utemplate import render_template
import utime
from ucollections import OrderedDict
import network

app = Microdot()
Response.default_content_type='text/html'



emp_dict={}
with open("/log/messages.csv", "r") as file:
    for i in file.readlines():
        (sent_time_unix, user1, user2, message) = i.split(",")
        emp_dict[sent_time_unix] = (user1, user2, message)

#LORA Section

from ulora import LoRa, ModemConfig, SPIConfig

# Lora Parameters
RFM95_RST = 14 #reset pin on board.
RFM95_SPIBUS = SPIConfig.esp32_2
RFM95_CS = 5
RFM95_INT = 2 #from pin 14(dio0 on rfm95w to this on interupt on board, you must select/define which you want to use.
RF95_FREQ = 915.0 #north america freq
RF95_POW = 20
CLIENT_ADDRESS = 40 # this address
SERVER_ADDRESS = 20 # to address

# initialise radio
lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)



def csv_write(time_unix, user1, user2, message):
    with open('/log/messsages.csv', "a") as file:
        file.write(str(time_unix) +","+ user1 +","+ user2 +"," + message +"\n")
        file.close()
        
def on_recv(payload):
    print("From:", payload.header_from)
    print("Received:", payload.message)
    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    print(payload.message)
    from_user = str(payload.header_from)
    to_user = str(payload.header_to)
    message_str = payload.message.decode()
    sent_time_unix = str(message_str.split("%$%$")[0])
    message_itself = message_str.split("%$%$")[2]
    emp_dict[sent_time_unix] = (from_user, to_user, message_itself)
    csv_write(sent_time_unix, from_user, to_user, message_itself)
    
@app.route("/")
def show_users(req):
    convo_list = []
    for k, v in emp_dict.items():
        if v[1] not in convo_list:
            convo_list.append(v[1])
    print(convo_list)
    return render_template('conversations.html', convo_list= convo_list)    

# def csv_to_dict(convo):
#     with open("/log/messages.csv", "r") as file:
#         for i in file.readlines():
#             (sent_time_unix, user1, user2, message) = i.split(",")
#             if user1==convo:
#                 emp_dict[sent_time_unix] = (user1, user2, message)

    
   
@app.route("/<string:convo>",  methods=['GET', 'POST'])
def message_input(req, convo):
    for k, v in emp_dict.items():
        local_dict={}
        if v[1] == convo:
            local_dict[k] = (v[0], v[1], v[2], v[3])
    if req.method == 'POST':
        sent_time_unix = str(req.form.get('unixTime'))
        message = str(req.form.get('textbox'))
        from_user=str(CLIENT_ADDRESS)
        to_user = str(SERVER_ADDRESS)
        data = sent_time_unix+"%$%$"+message
        lora.send_to_wait(data, SERVER_ADDRESS)
        emp_dict[sent_time_unix]=(to_user, from_user, message)
        emp_dict = OrderedDict(sorted(emp_dict.items()))
        csv_write(sent_time_unix, to_user, from_user, message)
        print(sent_time_unix)
    return render_template('message_input.html', local_dict= local_dict, convo=convo)

lora.on_recv = on_recv
lora.set_mode_rx()


address= network.WLAN(network.STA_IF).ifconfig()[0]

print('app_running....', 'network config:', address+":5000")

if __name__ == '__main__':
    app.run()
