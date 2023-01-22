from microdot import Microdot, Response, redirect
from microdot_utemplate import render_template
import utime
from ucollections import OrderedDict
import network
import time

app = Microdot()
Response.default_content_type='text/html'


month_dict={
            1:"JAN",
            2:"FEB",
            3:"MAR",
            4:"APR",
            5:"MAY",
            5:"JUN",
            7:"JUL",
            8:"AUG",
            9:"SEP",
            10:"OCT",
            11:"NOV",
            12:"DEC",
            }


chat_hist =[]
try:
    #open("/log/messages.csv", "r")
    with open("/log/messages.csv", "r") as file:
        for i in file.readlines():
            line_list = (i.split(","))
            chat_hist.append([x.strip() for x in line_list])
        file.close()
        print(chat_hist)
except:
    print('file doesnt exist yet or some other error')

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



def csv_write(sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this):
    with open('/log/messages.csv', "a") as file:
        file.write(str(sent_time_unix) +","+ other_device_addr +","+ this_device_addr +"," + message_oth +"," + message_this+"\n")
        file.close()
        
def on_recv(payload):
#     print("From:", payload.header_from)
#     print("Received:", payload.message)
#     print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    message_intermediate = payload.message
    other_device_addr = str(payload.header_from)
    this_device_addr = str(payload.header_to)
    print(message_intermediate, other_device_addr, this_device_addr)
    sent_time_unix = str(message_intermediate.decode().split("%$%$")[0])
    message_oth = str(message_intermediate.decode().split("%$%$")[1])
    message_this = ""
    chat_hist.append([sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this])
    csv_write(sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this)
    
@app.route("/")
def show_users(req):
    this_device_addr=str(CLIENT_ADDRESS)
    convo_list = []
    for i in chat_hist:
        print(i)
        if i[1] not in convo_list and i[1] != this_device_addr:
            convo_list.append(i[1])
    print(convo_list)
    return render_template('convos.html', convo_list= convo_list, this_device_addr=this_device_addr)

@app.route("/new_convo",  methods=['GET', 'POST'])
def new_convo(req):
    convo = ""
    if req.method == 'POST':
        convo = str(req.form.get('new_address'))
        return redirect("/"+convo)
    return render_template('new_convo.html')

# @app.route("/settings",  methods=['GET', 'POST'])
# def settings(req):
#     if req.method == 'POST':
#         essid = str(req.form.get('new_address'))
#         password = str(req.form.get('new_address'))
#         auth_type = str(req.form.get('new_address'))
#     return render_template('settings.html')
    
    
   
@app.route("/<string:convo>",  methods=['GET', 'POST'])
def message_input(req, convo):
    convo=convo
    global chat_hist
    local_list= []
    this_device_addr=str(CLIENT_ADDRESS)   
    for i in chat_hist:
        if i[1] == convo:
            local_list.append(i)
#     for i in local_list:
#         try:
#             tag = time.gmtime(int(i[0]) -946684800)
#             tag = str("%02d" %(tag[2],))+month_dict[tag[1]]+str(tag[0])+" "+str(tag[3])+":"+str(tag[4])
#             i.append(tag)
#         except
    
    if req.method == 'POST':
        sent_time_unix = str(req.form.get('unixTime'))
        message_this = str(req.form.get('textbox'))
        print(message_this)
        message_oth = ""
        other_device_addr = convo
        data = sent_time_unix+"%$%$"+message_this
        if [sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this] not in local_list:
            lora.send_to_wait(data, int(convo))
            local_list.append([sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this])
            chat_hist.append([sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this])
            csv_write(sent_time_unix, other_device_addr, this_device_addr, message_oth, message_this)
        
    return render_template('message_input.html', local_list= local_list, convo=convo, this_device_addr=this_device_addr)

lora.on_recv = on_recv
lora.set_mode_rx()


address= network.WLAN(network.STA_IF).ifconfig()[0]

print('app_running....', 'network config:', address+":5000")

if __name__ == '__main__':
    app.run()
