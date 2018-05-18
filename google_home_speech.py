#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
debug = config.debug

import sys

if debug : print('initializing...', flush=True, file=sys.stderr)

import os
import json
import netifaces

from http.server import BaseHTTPRequestHandler, HTTPServer

import pychromecast
import gtts


media_contoller = None
speech_filename = 'v.mp3'

def dbgprint(text):
        if debug:
                print(text, flush=True, file=sys.stderr)


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
                dbgprint('local_ip = ' + ipv4_addr)
                return ipv4_addr
        dbgprint('failed to get local_ip')
        return ''                


def discovery_google_home():
        dbgprint('Start discovery google home...')
        chromecasts = pychromecast.get_chromecasts()
        dbgprint(",".join([str(x) for x in chromecasts]))
        for cc in chromecasts:
                if cc.device.friendly_name.startswith(config.friendly_name):
                        dbgprint('google home found friendly_name = ' + cc.device.friendly_name)
                        cast = cc
                        mc = cast.media_controller
                        return mc
        dbgprint('No google home found.')
        return None

def do_speech(text, language):
        global media_contoller
        dbgprint('get speech data for ' + text + '(' + language + ')')
        tts = gtts.gTTS(text = text, lang = language)
        tts.save(speech_filename)
        dbgprint('send speech data to google home')
        if media_contoller is None:
                media_contoller = discovery_google_home()
        if media_contoller is None:
                return
        media_url = 'http://' + local_ip + ':' + str(config.listen_port) + '/' + speech_filename
        dbgprint('media_url = ' + media_url)
        media_contoller.play_media(media_url, 'audio/mpeg')


class JsonResponseHandler(BaseHTTPRequestHandler):
        def do_POST(self):
                language = config.language 
                dbgprint(format(self.headers))
                content_len = int(self.headers.get('content-length'))
                requestBody = self.rfile.read(content_len).decode('UTF-8')
                dbgprint('POST requestBody=' + requestBody)
                try:
                        jsonData = json.loads(requestBody)
                        dbgprint('**JSON**')
                        dbgprint(json.dumps(jsonData, sort_keys=False, indent=4, separators={',', ':'}))
                except:
                        dbgprint('faild to decode json')
                        jsonData = None

                if jsonData is not None and 'language' in jsonData:
                        language = jsonData['language']
                if jsonData is not None and 'text' in jsonData:
                        text = jsonData['text']
                        do_speech(text, language)
                else:
                        dbgprint('no text')
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(requestBody.encode('UTF-8'))

        def do_GET(self):
                path = self.path
                dbgprint('GET path = ' + path)
                filename = path[1:]

                if filename != speech_filename:
                        dbgprint('deny GET request for ' + path)
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
        dbgprint('HTTP Server is ready')
        dbgprint('')
        dbgprint('examples:')
        dbgprint('curl -X POST -d \'{"text":"test"}\' http://localhost:' + str(config.listen_port) + '/')
        dbgprint('curl -X POST -d \'{"text":"Hello, this is test.","language":"en"}\' http://localhost:' + str(config.listen_port)  + '/')
        dbgprint('curl -X POST -d \'{"text":"こんにちは","language":"ja"}\' http://localhost:' + str(config.listen_port)  + '/')
        dbgprint('curl -X POST -d \'{"text":"你好","language":"zh-cn"}\' http://localhost:' + str(config.listen_port)  + '/')
        dbgprint('')

if config.welcome_speech_text: do_speech(config.welcome_speech_text, config.language)
server.serve_forever()
