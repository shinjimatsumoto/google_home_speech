#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
debug = config.debug

import sys

if debug: sys.stderr.write('initializing...\n')

import os
import json
import netifaces

from http.server import BaseHTTPRequestHandler, HTTPServer

import pychromecast
import gtts


media_contoller = None
speech_filename = 'v.mp3'

def get_local_ip():
        if config.local_ip:
                return config.local_ip
        for iface_name in netifaces.interfaces():
                if iface_name == 'lo': continue
                if not iface_name.startswith(config.interface_name): continue
                iface_data = netifaces.ifaddresses(iface_name)
                if netifaces.AF_INET not in iface_data: continue
                ipv4_addrs = iface_data[netifaces.AF_INET]
                if not ipv4_addrs: continue
                if 'addr' not in ipv4_addrs[0]: continue
                ipv4_addr = ipv4_addrs[0]['addr']
                if not ipv4_addr: continue
                if ipv4_addr.startswith('127.'): continue
                if debug: sys.stderr.write('local_ip = ' + ipv4_addr + '\n')
                return ipv4_addr
        if debug: sys.stderr.write('failed to get local_ip\n')
        return ''                


def discovery_google_home():
        if debug : sys.stderr.write('Start discovery google home...\n')
        chromecasts = pychromecast.get_chromecasts()
        if debug : sys.stderr.write(",".join([str(x) for x in chromecasts]) + '\n')
        for cc in chromecasts:
                if cc.device.friendly_name.startswith(config.friendly_name):
                        if debug : sys.stderr.write('google home found friendly_name = ' + cc.device.friendly_name + '\n')
                        cast = cc
                        mc = cast.media_controller
                        return mc
        if debug : sys.stderr.write('No google home found.\n')
        return None

def do_speech(text, language):
        global media_contoller
        if debug: sys.stderr.write('get speech data for ' + text + '(' + language + ')\n')
        tts = gtts.gTTS(text = text, lang = language)
        tts.save(speech_filename)
        if debug: sys.stderr.write('send speech data to google home\n')
        if media_contoller is None:
                media_contoller = discovery_google_home()
        if media_contoller is None:
                return
        media_url = 'http://' + local_ip + ':' + str(config.listen_port) + '/' + speech_filename
        if debug: sys.stderr.write('media_url = ' + media_url + '\n')
        media_contoller.play_media(media_url, 'audio/mpeg')


class JsonResponseHandler(BaseHTTPRequestHandler):
        def do_POST(self):
                language = config.language 
                if debug: sys.stderr.write(format(self.headers) + '\n')
                content_len = int(self.headers.get('content-length'))
                requestBody = self.rfile.read(content_len).decode('UTF-8')
                if debug: sys.stderr.write('requestBody=' + requestBody + '\n')
                try:
                        jsonData = json.loads(requestBody)
                        if debug: sys.stderr.write('**JSON**\n')
                        if debug: sys.stderr.write(json.dumps(jsonData, sort_keys=False, indent=4, separators={',', ':'}) + '\n')
                except:
                        if debug: sys.stderr.write('faild to decode json\n')
                        jsonData = None

                if jsonData is not None and 'language' in jsonData:
                        language = jsonData['language']
                if jsonData is not None and 'text' in jsonData:
                        text = jsonData['text']
                        do_speech(text, language)
                else:
                        if debug: sys.stderr.write('no text\n')
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(requestBody.encode('UTF-8'))

        def do_GET(self):
                path = self.path
                if debug: sys.stderr.write ('GET requested for ' + path  + '\n')
                filename = path[1:]

                if filename != speech_filename:
                        if debug: sys.stderr.write('deny GET request for ' + path + '\n')
                        self.send_response(404)
                        self.end_headers()
                        return

                try:
                        sndfile = open(filename, 'rb').read()
                except:
                        sndfile = None

                if sndfile is None:
                        self.send_response(404)
                        self.end_headers()
                        return
                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Content-length', os.stat(filename).st_size)
                self.end_headers()
                self.wfile.write(sndfile)

local_ip = get_local_ip()
media_contoller = discovery_google_home()
server = HTTPServer(('', config.listen_port), JsonResponseHandler)
if debug: 
        sys.stderr.write('HTTP Server is ready\n')
        sys.stderr.write('\n')
        sys.stderr.write('examples:\n')
        sys.stderr.write('curl -X POST -d \'{"text":"test"}\' http://localhost:' + str(config.listen_port)  + '/\n')
        sys.stderr.write('curl -X POST -d \'{"text":"Hello, this is test.","language":"en"}\' http://localhost:' + str(config.listen_port)  + '/\n')
        sys.stderr.write('curl -X POST -d \'{"text":"こんにちは","language":"ja"}\' http://localhost:' + str(config.listen_port)  + '/\n')
        sys.stderr.write('curl -X POST -d \'{"text":"你好","language":"zh-cn"}\' http://localhost:' + str(config.listen_port)  + '/\n')
        sys.stderr.write('\n')

if config.welcome_speech_text: do_speech(config.welcome_speech_text, config.language)
server.serve_forever()
