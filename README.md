# google_home_speech

Let Google Home speak voice message.

## install

```
git clone https://github.com/shinjimatsumoto/google_home_speech
cd google_home_speech
pip3 install -r requirements.txt
```

## configuration (optional)

edit config.py

###### debug

Enable debug print.
default: True

###### listen_port

TCP port number to listen.
default: 8000

###### friendly_name

The friendly name of your Google Home to speak. If this variable is empty string, first found CastV2 enabled device will be chosen. If you have multiple CastV2 enabled devices, you may have to set the friendly_name.
defalut: ''

###### local_ip

local ip address of the computer which google_home_speech.py runs on. If this valiable is empty string, auto detection of local ip will be performed.

###### interface_name

Interface name for local ip detection. If this variable is empty string, first found network interface will be chosen. If your computer is multi-homed host, you may have to set the friendly_name.

## usage

Run google_home_speech.py

```
python3 google_home_speech.py
```

If google_home_speech.py succeeeds to discover your Google Home, it speaks a welcome message. Then google_home_speach.py waits http requests. You can send requests by curl command.

```
curl -X POST -d '{"text":"test"}' http://localhost:8000/
```

Your Google Home speaks "test".


## example

```
$ python3 google_home_speech.py 
initializing...
local_ip = 192.168.20.9
Start discovery google home...
[Chromecast('192.168.20.75', port=8009, device=DeviceStatus(friendly_name='オフィス', model_name='Google Home Mini', manufacturer='Google Inc.', uuid=UUID('cbd7504f-770a-4b6f-9217-0f5f7190e37e'), cast_type='cast'))]
google home found friendly_name = オフィス
HTTP Server is ready

examples:
curl -X POST -d '{"text":"test"}' http://localhost:8000/
curl -X POST -d '{"text":"Hello, this is test.","language":"en"}' http://localhost:8000/
curl -X POST -d '{"text":"你好","language":"zh-cn"}' http://localhost:8000/

get speech data for グーグルホームスピーチが起動しました。(ja)
send speech data to google home
media_url = http://192.168.20.9:8000/v.mp3
GET requested for  /v.mp3
192.168.20.75 - - [04/May/2018 12:34:08] "GET /v.mp3 HTTP/1.1" 200 -
```




