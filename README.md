# esp32_server


This is a Micropython implemenation of  Microdot web server on Esp32. 

The server hosts a website that a user connects to and then can send messages over long distance ~1-2km(LORA), without the aid of cell service or wifi.

The beauty of this is that it does not require a seperate keyboard. 

The user connects to the esp32 via wifi, then routes to the localhost serving the microdot website. The user then can select their recepient, and send that user a message. 

Can be used with all devices(android/ios/pc)

