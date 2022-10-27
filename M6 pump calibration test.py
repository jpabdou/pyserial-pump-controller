import serial
import time
import datetime

# Configure serial connections for each pump
ser1 = serial.Serial(
    port='COM5',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    xonxoff=False,
    timeout=1,
    bytesize=serial.EIGHTBITS
)

ser2 = serial.Serial(
    port='COM4',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    xonxoff=False,
    timeout=1,
    bytesize=serial.EIGHTBITS
)

ser3 = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    xonxoff=False,
    timeout=1,
    bytesize=serial.EIGHTBITS
)

# Check that the serial connection is open
print(ser1.isOpen())
print("check #1")

print(ser2.isOpen())
print("check #2")

print(ser3.isOpen())
print("check #3")

startTime = time.ctime(time.time())
timelog = []

def logger(string): #appending strings to an array to write to a txt file at the end of the experiment
    timelog.append(string)
    return(timelog)

# Sends instructions to pump in the form of a string encoded in ASCII format

def direct1(string):
    string = string + "\r"
    ser1.write(string.encode('ascii'))

def direct2(string):
    string = string + "\r"
    ser2.write(string.encode('ascii'))


def direct3(string):
    string = string + "\r"
    ser3.write(string.encode('ascii'))

#conversion to the stepper level used in the pumps
def rate_calc(rate):
    const = 2432/60 # SL value for pump 1 for 1 ul/min; const * flow rate in ul/min = stepper level
    return str(round(float(rate) * float(const)))

def rate_log_direct1(rate): # logging the volume of the rate ran before and after sending the current rate on the pump using the PR V command and directing the pump rate
    a_rate = "SL="+rate_calc(rate)
    direct1("PR V")
    followup= str(ser1.read_until())
    logger(followup)
    logger(f"pump 1: {str(rate)} ul/min and set to {a_rate}")
    direct1(a_rate)
    direct1("PR V")
    followup2= str(ser1.read_until()) #read 2 lines as I still have timing issues for reading the PR V output line
    followup3= str(ser1.read_until())
    logger(followup2)
    logger(followup3)
    logger("")

def rate_log_direct2(rate): 
    b_rate = "SL="+rate_calc(rate)
    direct2("PR V")
    followup= str(ser2.read_until())
    logger(followup)
    logger(f"pump 2: {str(rate)} ul/min and set to {b_rate}")
    direct2(b_rate)
    direct2("PR V")
    followup2= str(ser2.read_until())
    followup3= str(ser2.read_until())
    logger(followup2)
    logger(followup3)
    logger("")
    logger("")

def rate_log_direct3(rate): 
    c_rate = "SL="+rate_calc(rate)
    direct3("PR V")
    followup= str(ser2.read_until())
    logger(followup)
    logger(f"pump 3: {str(rate)} ul/min and set to {c_rate}")
    direct3(c_rate)
    direct3("PR V")
    followup2= str(ser3.read_until())
    followup3= str(ser3.read_until())
    logger(followup2)
    logger(followup3)
    logger("")
    logger("")

# Setting target flow rate in ul/min in independent mode for each syringe
def run_rate(rate_value1, rate_value2):
    rate_log_direct1(rate_value1)
    time.sleep(0.1) # 0.1 second delay out of concern of the steps interfering with each on execution
    rate_log_direct2(rate_value2)

def volume_test(start_rate1, final_rate1, start_rate2, final_rate2, steps): # calculations for flow rates in experiment sequence based on starting/ending flow rates and number of steps; xxx_rate1 refers to pump 1 flow rates while xxx_rate2 refers to pump 2 flow rates
    p1rampset = []
    p2rampset = []
    p1dropset = []
    p2dropset = []
    steps_total = steps
    diff1 = start_rate1-final_rate1
    diff2 = start_rate2-final_rate2
    while steps != 0:
        p1rampset.append(start_rate1)
        p1dropset.append(start_rate1)
        p2rampset.append(start_rate2)
        p2dropset.append(start_rate2)
        start_rate1 = start_rate1 - (diff1/(steps_total-1))
        start_rate2 = start_rate2 - (diff2/(steps_total-1))
        steps = steps -1
    p1dropset.pop()
    p1dropset.reverse()    
    p2dropset.pop()
    p2dropset.reverse()
    return(p1rampset, p2rampset, p1dropset, p2dropset)

# Mixing test based on starting flow rates in ul/min, step count for each change in flow rate, and step time in seconds
def mix_test(start_rate1, final_rate1, start_rate2, final_rate2, steps_total, step_time):
    logger("step " + str(0))
    logger(str(datetime.datetime.now()))
    logger(str(datetime.datetime.now()-startProgram))
    step = 0
    p1ramplist, p2ramplist, p1droplist, p2droplist = volume_test(start_rate1, final_rate1, start_rate2, final_rate2, steps_total)
    logger("ramp test") # ramp test with syringe P1 starting at 500 ul/min and changed stepwise to 0 ul/min over 11 steps for 3 minutes each while P2 syringe undergoes vice versa
    while step != steps_total:
        logger("step " + str(step))
        logger(str(datetime.datetime.now())) # log datetime
        logger(str(datetime.datetime.now()-startProgram)) # log time in terms of hours, minutes, and seconds since start
        start_step = datetime.datetime.now()
        p1rate = ((p1ramplist[step]))
        p2rate = ((p2ramplist[step]))
        run_rate(p1rate, p2rate)
        delay_time=(datetime.datetime.now()-start_step).seconds+((datetime.datetime.now()-start_step).microseconds/1000000)
        time.sleep((step_time)-(delay_time))
        logger("")
        step = step + 1 
    # logger("drop test") # drop test with syringe P1 starting at 50 ul/min (set from 0 ul/min at start) and changed stepwise to 500 ul/min over 10 steps for 3 minutes each while P2 syringe undergoes vice versa
    # step = 0
    # while step != steps_total-1:
    #     logger("step " + str(step))
    #     logger(str(datetime.datetime.now()))
    #     p1rate = ((p1droplist[step]))
    #     p2rate = ((p2droplist[step]))
    #     if p1rate == str(0) or p1rate == str(0.0): # Can't send IRUN command at 0 ul/min as its below the minimum flow rate
    #         solo_run = "SL="+rate_calc(p2rate)
    #         logger(solo_run)
    #         logger("pump 1: " + str(p1rate) + " and " +"pump 2:" + str(p2rate))
    #         direct2(solo_run)
    #         time.sleep(step_time)
    #         direct2("SL=0")
    #     elif p2rate == str(0) or p2rate == str(0.0):
    #         solo_run = "SL="+rate_calc(p1rate)
    #         logger(solo_run)
    #         logger("pump 1: " + str(p1rate) + " and " +"pump 2:" + str(p2rate))
    #         direct1(solo_run)
    #         time.sleep(step_time)
    #         direct1("SL=0")
    #     else:
    #         run_rate(p1rate, p2rate)
    #         time.sleep(step_time)
    #         direct1("SL=0")
    #         direct2("SL=0")
    #     step = step + 1 
direct1("EM=1") # setting pumps to half-duplex
direct2("EM=1")
direct3("EM=1")
run_rate(0,0) # set to zero flow rates in case pumps were left running
rate_log_direct3(0)
print("Start the PowerChrom in T-minus: 5...") # count down to start measurements
time.sleep(1)
print("4...")
time.sleep(1)
print("3...")
time.sleep(1)
print("2...")
time.sleep(1)
print("1...")
time.sleep(1)
print("Start!")
startProgram = (datetime.datetime.now())
rate_log_direct3(500)
logger(str(datetime.datetime.now()))
logger(str(datetime.datetime.now()-startProgram))
logger("")
logger("starting sequence") # starting sequence of running pump 1 at 500 ul/min and pump 2 at 0 ul/min, then pump 1 at 0 and pump 2 and 500, and lastly pump 1 at 500 and pump 2 at 0 at 1 minute for each step
mix_test(500, 0, 0, 500, 2, 60)
run_rate(500, 0)
time.sleep(60)

logger("experiment sequence")

mix_test(500,0,0,500,11, 60) # programmed experimental sequence
logger("ending sequence") # rerunning starting sequence to determine if measurements of the maximum and minimum measurements shifted at the end of the experiment
mix_test(500, 0, 0, 500, 2, 60)
run_rate(500, 0)
time.sleep(60)
logger("testing complete")
logger(str(datetime.datetime.now()))
logger(str(datetime.datetime.now()-startProgram))
run_rate(0, 0) # setting pumps to zero by the end of the experiment
rate_log_direct3(0)

# writes timelog to a text file in the a folder location with a name based on the start time; can be moved to the "logger" function, but I was concerned if file writing can affect the serial commands
with open(("INSERT FOLDER LOCATION HERE" + startTime.replace(":","-") + ".txt") ,  "w") as txt_file:
    for line in timelog:
        txt_file.write("".join(line) + "\n")
