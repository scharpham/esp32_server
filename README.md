# esp32_server


This is a Micropython implemenation of  Microdot web server on Esp32 with rfm95w Lora Radio. 

The microcontroller hosts a small http web server that a user connects to with wifi. 

THere is a gui at the local address for sending messages. Range ~1-2km(LORA), without the aid of cell service or wifi.



The beauty of this is that it does not require a separate keyboard, or any app installation.

The user connects to the esp32 via wifi, then routes to the localhost serving the microdot website. The user then can select their intended recipient, and send that user a message. 

Can be used with all devices(android/ios/pc)

