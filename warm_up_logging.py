#!/usr/bin/python2

import time
from datetime import datetime, timedelta
import Gpib

def setup_dmm(addr):
    inst = Gpib.Gpib(0, addr)
    inst.clear()
    inst.write("PRESET NORM")
    inst.write("OFORMAT ASCII")
    inst.write("DCV 10")
    inst.write("TARM HOLD")
    inst.write("TRIG AUTO")
    inst.write("NPLC 200")
    inst.write("NRDGS 1,AUTO")
    inst.write("MEM OFF")
    inst.write("END ALWAYS")
    inst.write("NDIG 9")
    inst.write("DISP OFF,\"                 \"")
    return inst

def run_acal(inst):
    inst.write("ACAL 1")

def record_cal_values(inst, file_handle):
    test_time = time.strftime("%d/%m/%Y-%H:%M:%S")

    inst.write("TEMP?")
    temp = inst.read().strip()

    # Read ACAL DCV 10V Gain value
    inst.write("CAL? 72")
    cal_dcv_gain = inst.read().strip()

    # Read 40K reference actual value
    inst.write("CAL? 1,1")
    cal_40k_actual = inst.read().strip()

    # Read 7V reference actual value
    inst.write("CAL? 2,1")
    cal_7v_actual = inst.read().strip()

    print '{} > Temp: {} Gain: {} 40k: {} 7v: {}'.format(test_time, temp, cal_dcv_gain, cal_40k_actual, cal_7v_actual)

    values = map(str, [test_time, temp, cal_dcv_gain, cal_40k_actual, cal_7v_actual])
    file_handle.write(";".join(values) + '\n')

def main():
    dmm1 = setup_dmm(22)
    dmm2 = setup_dmm(23)

    file_handle1 = open("cal_testing_22.csv", mode='a', buffering=1)
    file_handle2 = open("cal_testing_23.csv", mode='a', buffering=1)

    start_time = datetime.now()
    measure_interval = timedelta(hours=12)
    target_time = start_time.replace(microsecond=0, second=0, minute=0, hour=18)

    for x in range(1, 10):
        print "Next Measurement at {}".format(target_time)
        time.sleep((target_time-datetime.now()).seconds)
        target_time += measure_interval

        run_acal(dmm1)
        run_acal(dmm2)
        # Wait for 5 minutes
        time.sleep(60*5)
        
        print "Testing DMM 22"
        record_cal_values(dmm1, file_handle1)
        print "Testing DMM 23"
        record_cal_values(dmm2, file_handle2)

    file_handle1.close()
    file_handle2.close()

    print "Done with measurements"

if __name__ == "__main__":
    main()
