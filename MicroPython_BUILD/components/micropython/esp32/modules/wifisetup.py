import _thread, network, json, ubinascii, time, machine
from m5stack import lcd

wlan_sta = network.WLAN(network.STA_IF); wlan_sta.active(True)
lcd.setColor(0xCCCCCC, 0)


# # Define the WiFi events callback function
# def wifi_cb(info):
#     print("[WiFi] event: {} ({})".format(info[0], info[1]))
#     if (info[2]):
#         print("        info: {}".format(info[2]))


def do_connect(ntwrk_ssid, netwrk_pass):
	if not wlan_sta.isconnected():
		print('Connect WiFi: SSID:'+ntwrk_ssid+' PASSWD:'+netwrk_pass+' network...')
		lcd.println('Connect WiFi: \r\nWiFi SSID:'+ntwrk_ssid)
		# lcd.println('Connect WiFi: \r\nWiFi SSID:'+ntwrk_ssid+' \t\nPASSWD:'+netwrk_pass)
		# wlan_sta.eventCB(wifi_cb)
		wlan_sta.active(True)
		wlan_sta.connect(ntwrk_ssid, netwrk_pass)
		lcd.print('Connecting.')
		a=0
		while not wlan_sta.isconnected() | (a > 50) :
			time.sleep_ms(500)
			a+=1
			print('.', end='')
			lcd.print('.',wrap=1)
		if wlan_sta.isconnected():
			print('\nConnected. Network config:', wlan_sta.ifconfig())
			lcd.println("Connected! \r\nNetwork config:\r\n"+wlan_sta.ifconfig()[0]+', '+wlan_sta.ifconfig()[3])
			return (True)
		else : 
			print('\nProblem. Not Connected to :'+ntwrk_ssid)
			lcd.println('Problem. Not Connected to :'+ntwrk_ssid)
			return (False)


def auto_connect():
	try:
		if not wlan_sta.isconnected():
			with open("config.json") as f:
				jdata = json.loads(f.read())
				ssid = jdata['wifi']['ssid']
				passwd = jdata['wifi']['password']

			if do_connect(ssid, passwd):
				return (True)
			print('connect fail!')

			if not wlan_sta.isconnected():
				wlan_sta.disconnect()
				import wificonfig
				wificonfig.webserver_start()
		else:
			return (True)
		
	except OSError:
		# Web server for connection manager
		import wificonfig
		wificonfig.webserver_start()


def isconnected():
	return wlan_sta.isconnected()


# def start():
# 	if auto_connect() == True:
# 		rtc = machine.RTC()
# 		print("Synchronize time from NTP server ...")
# 		lcd.println("Synchronize time from NTP server ...")
# 		rtc.ntp_sync(server="cn.ntp.org.cn")
# 	while not wlan_sta.isconnected():
# 		time.sleep(1)
# 	lcd.setTextColor(0xffffff)	

# start()

auto_connect()

rtc = machine.RTC()
print("Synchronize time from NTP server ...")
lcd.println("Synchronize time from NTP server ...")
rtc.ntp_sync(server="cn.ntp.org.cn")