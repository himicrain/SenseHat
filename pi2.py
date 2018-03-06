import time
import datetime as dt
import os
import string
import random
from sense_hat import SenseHat

def get_data_from_file(filename):

    file_r = open(filename,"r")
    maxt = maxh = maxp = -100
    mint = minh = minp = 100
    averaget = 0
    averageh = 0
    averagep = 0
    totalt = totalh = totalp = 0
    counter = 0
    line = file_r.readline()
    for line in file_r:
        datas = line.strip().split("\t")

        if datas[0] in [ "max","t","h","p"]:
            continue

        if maxt < round(float(datas[0]),1):
            maxt = round(float(datas[0]),1)
        if maxh < round(float((datas[1])),0):
            maxh = round(float((datas[1])),0)
        if maxp < round(float(datas[2]),1):
            maxp = round(float(datas[2]),1)

        if mint > round(float(datas[0]),1):
            mint = round(float(datas[0]),1)
        if minh > round(float((datas[1])),0):
            minh = round(float((datas[1])),0)
        if minp > round(float(datas[2]),1):
            minp = round(float(datas[2]),1)

        totalt = totalt + round(float(datas[0]),1)
        totalh = totalh + round(float((datas[1])),0)
        totalp = totalp + round(float(datas[2]),1)
        counter +=1

    averaget = round(totalt/counter,1)
    averageh = round(totalh/counter,1)
    averagep = round(totalp/counter,1)
    file_r.close()
    return maxt,maxh,maxp,mint,minh,minp,averaget,averageh,averagep


def write_data(path,old_day_str):
    maxt, maxh, maxp, mint, minh, minp, averaget, averageh, averagep = get_data_from_file(path + os.sep + old_day_str)
    file = open(path + os.sep + old_day_str, "a")
    file.write("\tmax\t" + "min\t" + "average" + os.linesep)
    file.flush()
    file.write("t\t" + str(maxt) + "\t" + str(mint) + "\t" + str(averaget) + os.linesep)
    file.write("h\t" + str(maxh) + "\t" + str(minh) + "\t" + str(averageh) + os.linesep)
    file.write("p\t" + str(maxp) + "\t" + str(minp) + "\t" + str(averagep) + os.linesep)


def get_data():
    sense = SenseHat()
    h=sense.get_humidity()
    t=sense.get_temperature()
    p=sense.get_pressure()
    msg="T=%s,H=%s,P=%s"%(t,p,h)

    #sense.show_message(msg,scroll_speed=0.1)

    print("T %s C"%t)
    print("h %s rh"%h)
    print("p %s p"%p)

    return [t,h,p]

def work(sq_time=1):

    #初始化当前存储数据的目录路径 getcwd（）是获取当前工作路径
    path = os.getcwd()+os.sep+"data"

    #如果当前路径下的这个文件夹不存在那么就创建
    if not os.path.isdir(path):
        os.mkdir("data")
        #工作路径修改成path
        os.chdir(path)
    #获取当前时间的时间戳
    current_time = time.time()
    #获取当前日期 比如 2017 03 05
    current_day = dt.date.today()
    #计算出当前日期的下一天，比如今天 2017 03 17 明天就是2017 03 18
    one_day_later = int(time.mktime((current_day + dt.timedelta(days=1)).timetuple()))
    #作为一个存储即将过去的一天，这样做是为了，当一天过去后，current_day修改成了新的一天，但是这时候需要计算刚过去一天的平均值等，那么就需要知道前一天是那一天，所以创建了这个
    old_day_str = current_day.strftime("%Y-%m-%d")

    while True:

        [t,h,p] = get_data()
        current_time = time.time()
        str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
        str_day = current_day.strftime("%Y-%m-%d")

        if not os.path.isfile(path + os.sep + str_day):
            os.mknod(path + os.sep + str_day )
            file = open(path + os.sep + str_day, "a")
            file.write("t\t" + "h\t" + "p"+"\ttime" + os.linesep)

        if current_time >= one_day_later :

            write_data(path,old_day_str)
            old_day_str = str_day
            current_day = dt.date.today()
            one_day_later = int(time.mktime((current_day + dt.timedelta(days=1)).timetuple()))
            str_day = current_day.strftime("%Y-%m-%d")
            print("next day")
            continue

        temp_time = time.strftime("%H:%M:%S", time.localtime(current_time))

        file = open(path+os.sep+str_day,"a")
        file.write(str(t)+"\t"+str(h)+"\t"+str(p)+"\t"+temp_time+os.linesep)
        file.flush()

        print(path+os.sep+str_day+"  "+str_time)
        time.sleep(sq_time*60)

if __name__ == '__main__':
    work(1) # 参数代表间隔多久测量一次（/min）






