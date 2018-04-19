from m5stack import lcd, node_id
import network, ubinascii, machine
import ujson as json
import utime as time
import usocket as socket

wlan_sta = network.WLAN(network.STA_IF); 
wlan_ap = network.WLAN(network.AP_IF)

def do_connect(ntwrk_ssid, netwrk_pass):
	if not wlan_sta.isconnected():
		print('M5Stack Core try to connect WiFi: SSID:'+ntwrk_ssid+' PASSWD:'+netwrk_pass+' network...')
		lcd.println('M5Stack Core try to connect WiFi: \r\nWiFi SSID:'+ntwrk_ssid+' \t\nPASSWD:'+netwrk_pass)
		wlan_sta.active(True)
		wlan_sta.connect(ntwrk_ssid, netwrk_pass)
		lcd.print('Connecting.')
		a = 0
		while not wlan_sta.isconnected() | (a > 100) :
			time.sleep(0.2)
			a += 1
			print('.', end='')
			lcd.print('.', wrap=True)
		if wlan_sta.isconnected():
			print('\nConnected. Network config:', wlan_sta.ifconfig())
			lcd.println("Connected! \r\nNetwork config:\r\n"+wlan_sta.ifconfig()[0]+', '+wlan_sta.ifconfig()[3])
			return (True)
		else: 
			print('\nProblem. Not Connected to :'+ntwrk_ssid)
			lcd.println('Problem. Not Connected to :'+ntwrk_ssid)
			return (False)


def save_wifi(ssid, password):
	try:
		wifidata = {}
		wifidata['ssid'] = ssid
		wifidata['password'] = password
		with open("config.json", "r") as fo:
			cfg = fo.read()
		with open("config.json", "w") as fo:
			cfg = json.loads(cfg)
			cfg['wifi'] = wifidata
			fo.write(json.dumps(cfg))
	except:
		with open("config.json", "w") as fo:
			cfg = {}
			cfg['wifi'] = wifidata
			fo.write(json.dumps(cfg))


def _httpHanderRoot(httpClient, httpResponse) :
	response_header = """\
		<html><meta name="viewport" content="width=device-width,height=device-height,initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>p{margin:10px 0}h1,h2{text-align:center;margin:35px 0}h2{margin:20px 0!important}form{margin-top:30px}tr td{text-align:right}tr select,tr input{width:200px;height:30px;padding-left:10px;outline:0;border-radius:3px;border:1px solid lightgrey}input[type="submit"]{width:300px;height:38px;color:#fff;background-color:#2196f1;border:0;font-size:20px;border-radius:3px;margin-top:20px}#mask{position:absolute;top:0;left:0;right:0;bottom:0;width:100%;height:100%;background-color:rgba(255,255,255,0.9);display:none}.wrap{position:absolute;top:0;left:0;right:0;bottom:0;margin:120px auto;width:280px}h4{font-size:22px;text-align:center}.progress-bar-wrap{width:280px;height:20px;border-radius:6px;overflow:hidden}.progress-bar{width:0;height:100%;animation:go 2s 1 forwards}@keyframes go{0%{width:0;background-color:#c72e45}50%{width:85%;background-color:orange}100%{width:100%;background-color:#0e9577}}</style><h1><img src="data:image/png;base64,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" alt=""></h1><h2 style="color: #333"><p style="font-weight:100;font-size:32px;">WiFi Setup</p></h2><form action="configure" method="get"><table style="margin-left: auto; margin-right: auto;"><tbody><tr><td>SSID:</td><td style="text-align: center;"><select id="ssid" name="ssid" >
	"""

	response_variable = ""
	# for ssid, *_ in scanlist:
	for ssid, *_ in wlan_sta.scan():
		response_variable += '<option value="{0}">{0}</option>'.format(ssid.decode("utf-8"))

	response_footer = """\
	</select></td></tr><tr><td>Password:</td><td><input name="password" type="password"></td></tr></tbody></table><p style="text-align: center;"><input type="submit" value="Configure" onclick="showLoading()"></p></form><div id="mask"><div class="wrap"><h4 id="info_text">Connecting Wifi ...</h4><div class="progress-bar-wrap"><div class="progress-bar"></div></div></div></div><script>function showLoading(){document.getElementById("mask").style.display="block"};</script></html>
	"""

	content = response_header + response_variable + response_footer
	# print('content:')
	# print(content)
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	   = "text/html",
								  contentCharset = "UTF-8",
								  content 		   = content )


def _httpHanderConfig(httpClient, httpResponse) :
	formData  = httpClient.GetRequestQueryParams()
	ssid      = formData["ssid"]
	password  = formData["password"]
	print(formData)
	content = ''
	is_connected = False

	if do_connect(ssid, password):
		is_connected = True
		save_wifi(ssid, password)
		content = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><style>h1{text-align:center;margin-top:120px;font-size:1.4rem;color:#0064a0}p{text-align:center;font-size:1.1rem}div{width:200px;margin:0 auto;padding-left:60px}</style><title></title></head><body><h1>^_^ WiFi connection success</h1><div><span>Reset device now </span><span id="wating">...</span></div></body><script>var wating=document.getElementById("wating");setInterval(function(){if(wating.innerText==="..."){return wating.innerText="."}wating.innerText+="."},500);</script></html>"""
	else:
		content = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><style>h1{text-align:center;margin-top:120px;font-size:1.4rem;color:red}p{text-align:center;font-size:1.1rem}</style><title></title></head><body><h1>×_× WiFi connection failed</h1><p>Click <a href="/">here</a> return configure page.</p></body></html>"""

	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

	if is_connected:
		time.sleep(3)
		wlan_ap.active(False)
		machine.reset()


routeHandlers = [
	( "/",	        "GET",	_httpHanderRoot ),
	( "/wifi",	    "GET",	_httpHanderRoot ),
	( "/configure",	"GET",	_httpHanderConfig )
]


# def wlan_ap_cb(info):
# 	# [WiFi] event: 15 (Station connected to soft-AP)
# 	event = info[0]
# 	if event == 15:
# 		# lcd.clear(lcd.WHITE)
# 		lcd.image(0,0, '/flash/img/qrcode_192.jpg')
# 		lcd.qrcode('http://192.168.4.1', 126, 17, 175)


def webserver_start():
	# wlan_ap.eventCB(wlan_ap_cb)
	wlan_ap.active(True)
	# node_id = ubinascii.hexlify(machine.unique_id())
	ssid_name= "M5Stack-"+node_id[-4:]
	# lcd.font(lcd.FONT_Comic, transparent=True)
	# lcd.print(ssid_name, 135, 190, lcd.RED)
	wlan_ap.config(essid=ssid_name, authmode=network.AUTH_OPEN)
	addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
	print('WiFi AP WebServer Start!')
	print('Connect to Wifi ssid:'+ssid_name)
	print('And connect to esp via your web browser (like 192.168.4.1)')
	print('listening on', addr)
	lcd.println(b'Connect to Wifi ssid:'+ssid_name)
	lcd.println('via your web browser: 192.168.4.1')
	lcd.println('listening on'+str(addr))

	from microWebSrv import MicroWebSrv
	webserver = MicroWebSrv(routeHandlers=routeHandlers)
	webserver.Start(threaded=False)
