import _thread
import time
from machine import Pin
from dfled import LED

# ------------------------------------------------------------------------------------ #

from dfnetwork import NET
wifi = NET('<redacted>','<redacted>')
wifi.connect()

# ------------------------------------------------------------------------------------ #

# Global Vars
racenum = 0
race_length = 32
run_state = 1
start_time = 0
switch_delay = 3000

sb_triggered = False
sb_triggered_at = 0
sb_sensor = Pin(23, Pin.IN, Pin.PULL_DOWN)

lane1_led = LED(16)
lane1_sensor = Pin(21, Pin.IN, Pin.PULL_UP)
lane1_triggered = False
lane1_triggered_at = 0
lane1_final_time = 0
lane1_time_sec = 0
lane1_time_disp = 0
lane1_fps = 0
lane1_mph = 0
lane1_smph = 0

lane2_led = LED(17)
lane2_sensor = Pin(22, Pin.IN, Pin.PULL_UP)
lane2_triggered = False
lane2_triggered_at = 0
lane2_final_time = 0
lane2_time_sec = 0
lane2_time_disp = 0
lane2_fps = 0
lane2_mph = 0
lane2_smph = 0

# ------------------------------------------------------------------------------------ #

def reset():
    print("Resetting system...")
    lane1_led.on()
    lane2_led.on()
    global run_state
    global start_time
    global sb_triggered
    global lane1_triggered
    global lane2_triggered
    global lane1_final_time
    global lane2_final_time
    global lane1_time_sec
    global lane2_time_sec
    global lane1_time_disp
    global lane2_time_disp
    global lane1_fps
    global lane2_fps
    global lane1_mph
    global lane2_mph
    global lane1_smph
    global lane2_smph

    lane1_final_time = 0
    lane2_final_time = 0
    lane1_time_sec = 0
    lane2_time_sec = 0
    lane1_time_disp = 0
    lane2_time_disp = 0
    lane1_fps = 0
    lane2_fps = 0
    lane1_mph = 0
    lane2_mph = 0
    lane1_smph = 0
    lane2_smph = 0

    lane1_triggered = False
    lane2_triggered = False
    run_state = 1
    start_time = 0
    sb_triggered = False
    time.sleep(2)
    lane1_led.off()
    lane2_led.off()

def results_table(lanecolor, lane, lane_time_disp, lane_fps, lane_mph, lane_smph):
    str = """\
        <td style='background-color: {};'>
          <table width=100%>
            <tr>
              <td colspan=2 style='font-size: 90px; font-weight: bold;'>
                Lane {}
              </td>
            </tr>
            <tr style='font-size: 70px; font-weight: bold;'>
              <td>
                {}
              </td>
              <td>
                Seconds
              </td>
            </tr>
            <tr style='font-size: 70px; font-weight: bold;'>
              <td>
                {}
              </td>
              <td>
                Feet Per Second
              </td>
            </tr>
            <tr style='font-size: 70px; font-weight: bold;'>
              <td>
                {}
              </td>
              <td>
                Miles Per Hour
              </td>
            </tr>
            <tr style='font-size: 70px; font-weight: bold;'>
              <td>
                {}
              </td>
              <td>
                MPH (Scaled)
              </td>
            </tr>
          </table>
        </td>
    """.format(lanecolor, lane, lane_time_disp, lane_fps, lane_mph, lane_smph)
    return str

def Webserv():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(0)
    lane1color="white"
    lane2color="white"
    while True:
        conn, addr = s.accept()
#        print("Got a connection from %s" % str(addr))
        request = conn.recv(1024)
        header = 'HTTP/1.1 200 OK\nConnection: close\nServer: FBMiniServ\nContent-Type: text/html\n\n'
        content = header

        with open('header.html', 'r') as html:
            content = content + html.read()

        if (lane1_final_time == (lane2_final_time-1) or
            lane1_final_time == (lane2_final_time+1)):
                lane1color="yellow"
                lane2color="yellow"
        elif (lane2_final_time == (lane1_final_time-1) or
              lane2_final_time == (lane1_final_time+1)):
                lane1color="yellow"
                lane2color="yellow"
        elif lane1_final_time == lane2_final_time:
            lane1color="yellow"
            lane2color="yellow"
        elif lane1_final_time < lane2_final_time:
            lane1color="green"
            lane2color="red"
        elif lane1_final_time > lane2_final_time:
            lane1color="red"
            lane2color="green"
        elif lane1_final_time == 0 and lane2_final_time ==0:
            lane1color="white"
            lane2color="white"

        lane1 = results_table(lane1color, '1', lane1_time_disp, lane1_fps, lane1_mph, lane1_smph)
        lane2 = results_table(lane2color, '2', lane2_time_disp, lane2_fps, lane2_mph, lane2_smph)


        content = content + lane1 + lane2

        with open('footer.html', 'r') as html:
            content = content + html.read()
        content = content + '\n'
        conn.sendall(content)
        conn.close()
#        print("Connection wth %s closed" % str(addr))
_thread.start_new_thread(Webserv, ())
print('Web server running')

while True:
    if run_state == 1:
        if sb_sensor.value() == 0 and sb_triggered == False and time.ticks_diff(time.ticks_ms(), sb_triggered_at) > switch_delay:
            sb_triggered = True
            sb_triggered_at = time.ticks_ms()
            start_time = time.ticks_ms()
            print('Start Time: {} - Going to run state 2'.format(start_time))
            run_state = 2

    elif run_state == 2:
        if sb_sensor.value() == 0 and time.ticks_diff(time.ticks_ms(), sb_triggered_at) > switch_delay:
            print('Resetting; incomplete race')
            sb_triggered_at = time.ticks_ms()
            sb_triggered = False
            reset()

        if lane1_sensor.value() == 0 and lane1_triggered == False:
            lane1_triggered = True
            lane1_triggered_at = time.ticks_ms()
            print('Lane 1 Triggered')

        if lane2_sensor.value() == 0 and lane2_triggered == False:
            lane2_triggered = True
            lane2_triggered_at = time.ticks_ms()
            print('Lane 2 Triggered')

        if lane1_triggered and lane2_triggered:
            print('Race finished')
            lane1_final_time = time.ticks_diff(lane1_triggered_at, start_time)
            lane2_final_time = time.ticks_diff(lane2_triggered_at, start_time)
            lane1_time_sec = lane1_final_time/1000
            lane2_time_sec = lane2_final_time/1000
            lane1_time_disp = '{:06.3f}'.format(lane1_time_sec)
            lane2_time_disp = '{:06.3f}'.format(lane2_time_sec)
            lane1_fps = '{:4.2f}'.format(race_length/lane1_time_sec)
            lane2_fps = '{:4.2f}'.format(race_length/lane2_time_sec)
            lane1_mph = '{:4.2f}'.format((race_length/lane1_time_sec) * 0.6818)
            lane2_mph = '{:4.2f}'.format((race_length/lane2_time_sec) * 0.6818)
            lane1_smph = '{:4.2f}'.format(((race_length/lane1_time_sec) * 0.6818) * 25)
            lane2_smph = '{:4.2f}'.format(((race_length/lane2_time_sec) * 0.6818) * 25)
            print('Lane 1: TimeMS: {}, TimeS: {}, FPS: {}, MPH: {}, SMPH: {}'.format(lane1_final_time, lane1_time_disp, lane1_fps, lane1_mph, lane1_smph))
            print('Lane 2: TimeMS: {}, TimeS: {}, FPS: {}, MPH: {}, SMPH: {}'.format(lane2_final_time, lane2_time_disp, lane2_fps, lane2_mph, lane2_smph))
            run_state = 3

          # Light up winning lane LED
            if lane1_final_time < lane2_final_time:
              lane1_led.on()
            if lane2_final_time < lane1_final_time:
              lane2_led.on()

          # Write race data to file
            with open('race_stats.txt', 'a+') as file:
              file.write('{},{},{}\n'.format(racenum, lane1_final_time, lane2_final_time))

          # Increment race number
            racenum = racenum + 1

    elif run_state == 3:
        if sb_sensor.value() == 0:
            reset()
