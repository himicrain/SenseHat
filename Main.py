from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as figureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
import sys
import time
import random
import threading
from pi2 import *

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.resize(500,350)
        self.setWindowTitle(self.tr("环境数据信息采集与分析系统"))
        self.timer_modify = QTimer(self)
        self.timer = QTimer(self)

        self.dirs_path = os.getcwd()+ os.sep + "data" + os.sep

        self.createActions()
        self.createMenus()
        #search界面需要的一些数据 (s代表的就是search)
        #湿度数据集合
        self.W_s = []
        #压强数据集合
        self.H_s = []
        #温度数据集合
        self.T_s = []
        #横坐标集合，初始化为24小时
        self.Y_s = []
        for i in range(1,25*60):
            self.Y_s.append(i)
        #search界面所需要的用于保存当前设置的年月分
        self.year_s = int(dt.date.today().strftime("%Y")) - 2017
        self.mouth_s = int(dt.date.today().strftime("%m")) - 1
        self.day_s = int(dt.date.today().strftime("%d")) - 1

        #测量界面所需要的一些数据集合，代表的意思和上面一样
        self.W = []
        self.H = []
        self.T = []
        self.Y = []

        #seq_time是指测量间隔时间，初始化为1min， 可以自己修改
        self.sq_time = 1

        #初始化上下限
        '''
            这里有几个关键的初始条件，下面这些变量就是上下限的初始值，可以自己修改
        '''

        self.max_h = 101
        self.min_h = 0
        self.max_t = 40
        self.min_t = 0
        self.max_w = 70
        self.min_w = 0

        #用于保存当前设置的上下限
        self.status = [[self.max_t,self.min_t],[self.max_w,self.min_w],[self.max_h,self.min_h]]

        #初始化
        self.SetUp()

        #开辟一个新的线程进行单独测量
        threading._start_new_thread(work,(self.sq_time,))

    #链接处理事件的函数和信号量
    def createActions(self):
        self.measureActions()
        self.queryActions()
        self.quitActions()
        self.openActions()
        self.helpActions()

    def measureActions(self):
        self.measureAction = QAction(self.tr("测量"), self)
        self.measureAction.setShortcut("Ctrl+M")
        self.measureAction.setStatusTip(self.tr("测量"))
        self.connect(self.measureAction, SIGNAL("triggered()"), self.measure)

    def queryActions(self):
        self.queryAction = QAction(self.tr("查询"), self)
        self.queryAction.setShortcut("Alt+S")
        self.queryAction.setStatusTip(self.tr("查询"))
        self.connect(self.queryAction, SIGNAL("triggered()"), self.search)

    def openActions(self):
        self.openAction = QAction(self.tr("打开"), self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip(self.tr("打开"))
        self.connect(self.openAction, SIGNAL("triggered()"), self.open)

    def quitActions(self):
        self.quitAction = QAction(self.tr("退出"), self)
        self.quitAction.setShortcut("Ctrl+G")
        self.quitAction.setStatusTip(self.tr("模块分级表"))
        self.connect(self.quitAction, SIGNAL("triggered()"),QtGui.qApp, SLOT('quit()'))

    def helpActions(self):
        self.helpAction = QAction(self.tr("帮助"), self)
        self.helpAction.setShortcut("Ctrl+G")
        self.helpAction.setStatusTip(self.tr("模块分级表"))
        self.connect(self.helpAction, SIGNAL("triggered()"),self.help)


    def createMenus(self):
        profileMenu = self.menuBar().addMenu(self.tr("菜单"))
        profileMenu.addAction(self.measureAction)
        profileMenu.addAction(self.queryAction)
        profileMenu.addAction(self.openAction)
        profileMenu.addAction(self.quitAction)

        help = self.menuBar().addMenu(self.tr("帮助"))
        help.addAction(self.helpAction)

    #打开文件夹
    def open(self):
        f = os.getcwd()
        self.dirs_path = QFileDialog.getExistingDirectory(self,'选取数据文件夹',f)+ os.sep
        if self.dirs_path == '/':
            self.dirs_path = f + os.sep + 'data' + os.sep
        print(self.dirs_path)

    #绘制measure假面的左上部分
    def createGridUpGroupBox(self):
        self.gridUpGroupBox = QGroupBox('')

        self.timeLabel = QLabel(self)
        self.dayLabel = QLabel(self)
        self.t_label = QLabel(self)
        self.w_label = QLabel(self)
        self.h_label = QLabel(self)

        d_str = time.strftime("%Y年%m月%d日", time.localtime())
        self.dayLabel.setFixedWidth(200)
        self.dayLabel.setFixedHeight(18)
        self.dayLabel.setText(self.tr('  当前日期： ' + d_str))

        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)

        self.timer_modify.timeout.connect(self.modify_all)
        self.timer_modify.start(self.sq_time*1000*60)


        t_str = time.strftime("%H:%M:%S", time.localtime())
        self.timeLabel.setFixedWidth(200)
        self.timeLabel.setFixedHeight(18)
        self.timeLabel.setText('  当前时间： ' + t_str)

        t, h, p = get_data()
        self.t_label.setFixedWidth(200)
        self.t_label.setFixedHeight(18)
        self.t_label.setText('  温度： '+str(round(float(t),1))+' °C')

        self.w_label.setFixedWidth(200)
        self.w_label.setFixedHeight(18)
        self.w_label.setText('  湿度： '+str(int(float(h))) + '  %RH')

        self.h_label.setFixedWidth(200)
        self.h_label.setFixedHeight(18)
        self.h_label.setText('  大气压力： '+str(round(float(p)/10,1)) + ' kPa')


        select_text = QLabel()
        select_text.setFixedHeight(20)
        select_text.setText('时间间隔: ')

        back_text = QLabel()
        back_text.setFixedHeight(20)
        back_text.setText(' mins')

        self.select = QComboBox()
        self.select.setFixedHeight(20)
        l = [1,2,3,4,5,6,7,8,9,10,15,20,25,30,40,50,60]
        for i in l:
            self.select.insertItem(i,self.tr(str(i)))

        self.select.setCurrentIndex(l.index(self.sq_time))
        self.select.currentIndexChanged.connect(self.modifyTime)

        inner_box = QHBoxLayout()
        inner_box.addWidget(select_text)
        inner_box.addWidget(self.select)
        inner_box.addWidget(back_text)
        inner_box.setAlignment(Qt.AlignLeft)
        inner_widget = QWidget()
        inner_widget.setLayout(inner_box)
        #inner_widget.setFixedHeight(20)

        grid1 = QGridLayout()
        grid1.addWidget(self.dayLabel, 0, 0)
        grid1.addWidget(self.timeLabel, 1, 0)
        grid1.addWidget(self.t_label, 2, 0)
        grid1.addWidget(self.w_label, 3, 0)
        grid1.addWidget(self.h_label, 4, 0)
        grid1.addWidget(inner_widget,5,0)

        self.gridUpGroupBox.setLayout(grid1)



    #用于动态修改当前时间
    def showTime(self):
        t_s = QTime.currentTime()
        text = t_s.toString('hh:mm:ss')

        if t_s.second() % 2 == 0:
            if t_s.second() / 60 == 0:
                text = text[:2] + ' ' + text[3:]
            else:
                text = text[:5] + ' ' + text[6:]
        try:
            self.timeLabel.setText('  当前时间： ' +text)
        except :
            pass
    #修改时间间隔
    def modifyTime(self):
        self.sq_time = int(self.select.currentText())
        self.timer_modify.start(self.sq_time*1000*60)

    #修改测量到的数据
    def modify_all(self):
        t,h,p = get_data()
        try:
            self.w_label.setText('  湿度： ' + str(round(float(h),1)) + ' %RH')
        except:
            pass
        self.W.append(h)

        try:
            self.h_label.setText('  大气压力： ' + str(int(float(p)/10)) + ' kPa')
        except:
            pass
        self.H.append(p/10)

        try:
            self.t_label.setText('  温度： ' + str(round(float(t),1)) + ' °C')
        except:
            pass
        self.T.append(t)

        t_s = time.strftime("%H:%M:%S", time.localtime(time.time()))

        t_i = int(t_s.split(":")[0])*60 + int(t_s.split(":")[1])

        self.Y.append(t_i/60)

        try:
            self.createRightUp()
        except:
            pass
    #用于保存当前measure 界面的上下限数据
    def storageStatus(self):
        for i in range(3):
            for j in range(2):
                self.status[i][j] = round(float(self.inner_table.item(i, j).text()), 1)

    #创建measure 的左下部分
    def createGridDownGroupBox(self):

        self.inner_table = QTableWidget(3,2)
        self.inner_table.clicked.connect(self.storageStatus)
        self.inner_table.setHorizontalHeaderLabels([ '上限', '下限'])
        self.inner_table.setVerticalHeaderLabels(["温度","湿度","大气压力"])

        for i in range(3):
            for j in range(2):
                self.inner_table.setItem(i,j,QTableWidgetItem(str(self.status[i][j])))

        self.inner_table.setFixedWidth(270)
        self.inner_table.setFixedHeight(123)
    #用于绘制measure 的温度曲线
    def T_draw(self):
        plt.cla()
        self.max_t = round(float(self.inner_table.item(0,0).text()),1)
        self.min_t = round(float(self.inner_table.item(0, 1).text()), 1)
        plt.xlim(0,24)
        plt.ylim(self.min_t,self.max_t)
        plt.plot(self.Y,self.T)
        plt.title('T')
    #用于绘制measure 的压强曲线
    def H_draw(self):
        plt.cla()
        self.max_h = round(float(self.inner_table.item(2,0).text()),1)
        self.min_h = round(float(self.inner_table.item(2, 1).text()), 1)
        plt.xlim(0,24)
        plt.ylim(self.min_h,self.max_h)
        plt.plot(self.Y,self.H)
        plt.title('P')
    #用于绘制measure 的湿度曲线
    def W_draw(self):
        plt.cla()
        self.max_w = int(float(self.inner_table.item(1,0).text()))
        self.min_w = int(float(self.inner_table.item(1, 1).text()))
        plt.xlim(0,24)
        plt.ylim(self.min_w,self.max_w)
        plt.plot(self.Y,self.W)
        plt.title('H')
    #用于绘制右上
    def createRightUp(self):

        plt.cla()

        if self.current_type == 0:
            self.T_draw()
        elif self.current_type == 1:
            self.H_draw()
        elif self.current_type == 2:
            self.W_draw()
        else:
            pass

        #x，y轴的标签
        plt.xlabel('time')
        plt.ylabel('data')
        self.canvas.draw()

    def action_T(self):
        self.current_type = 0
        self.createRightUp()
    def action_H(self):
        self.current_type = 1
        self.createRightUp()
    def action_W(self):
        self.current_type = 2
        self.createRightUp()

    #绘制右下 measure
    def createRightDown(self):
        RD_layout = QHBoxLayout()

        self.t_btn = QPushButton('温度')
        self.t_btn.clicked.connect(self.action_T)

        self.w_btn = QPushButton('湿度')
        self.w_btn.clicked.connect(self.action_W)

        self.h_btn = QPushButton('大气压力')
        self.h_btn.clicked.connect(self.action_H)

        RD_layout.addWidget(self.t_btn)
        RD_layout.addWidget(self.w_btn)
        RD_layout.addWidget(self.h_btn)


        self.t_btn.text()
        self.RD_widget = QWidget()
        self.RD_widget.setLayout(RD_layout)

    #绘制第一个初始化界面
    def SetUp(self):

        top = QVBoxLayout()
        top_label1 = QLabel("环  境  数  据  信  息")
        top_label2 = QLabel("采  集  与  分  析  系  统")

        top_label1.setFixedWidth(700)
        top_label1.setFixedHeight(50)
        top_label1.setAlignment(Qt.AlignCenter)
        top_label1.setFont(QFont("Serif",25,QFont.Bold))
        top_label1.setMargin(50)

        top_label2.setFixedWidth(700)
        top_label2.setFixedHeight(50)
        top_label2.setAlignment(Qt.AlignCenter)
        top_label2.setFont(QFont("Serif", 25, QFont.Bold))

        down_label1 = QLabel("制作人   : 王宣       ")
        down_label2 = QLabel("指导老师 : 秦晋       ")

        down_label1.setAlignment(Qt.AlignRight)
        down_label2.setAlignment(Qt.AlignRight)
        down_label1.setFont(QFont("Roman times", 15))
        down_label2.setFont(QFont("Roman times", 15))

        top.addSpacing(50)
        top.addWidget(top_label1)
        top.addWidget(top_label2)
        top.addStretch(1)
        top.addWidget(down_label1)
        top.addWidget(down_label2)
        top.addSpacing(80)


        top_widget = QWidget()
        top_widget.setLayout(top)

        self.setCentralWidget(top_widget)

        self.timer_s = QTimer(self)
        self.timer_s.timeout.connect(self.measure)
        self.timer_s.start(1000)

    #measure界面
    def measure(self):
        try:
            self.timer_s.stop()
        except:
            print('failed')
            pass

        self.current_type = -1 # 0 for T , 1 for H ,2 for W
        self.figure = plt.gcf()  # 返回当前的figure
        self.canvas = figureCanvas(self.figure)


        self.table = QTableWidget()
        self.createGridUpGroupBox()
        self.createGridDownGroupBox()
        self.createRightDown()
        self.createRightUp()


        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.gridUpGroupBox)
        vbox1.addWidget(self.inner_table)
        vbox1.setStretchFactor(self.gridUpGroupBox,3)
        vbox1.setStretchFactor(self.inner_table, 2)
        vw1 = QWidget()
        vw1.setLayout(vbox1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.canvas)
        vbox2.addWidget(self.RD_widget)
        vbox2.setStretchFactor(self.canvas,2)
        vbox2.setStretchFactor(self.RD_widget, 1)
        vw2 = QWidget()
        vw2.setLayout(vbox2)

        hbox = QHBoxLayout()
        hbox.addWidget(vw1)
        hbox.addWidget(vw2)

        mainWidget = QWidget()
        mainWidget.setLayout(hbox)

        self.setCentralWidget(mainWidget)


    #search界面 显示数据
    def show_data(self):

        self.year_s = self.year_select.currentIndex()
        self.mouth_s = self.mouth_select.currentIndex()
        self.day_s = self.day_select.currentIndex()

        self.date_str = self.year_select.currentText() + '-' + self.mouth_select.currentText() + '-' + self.day_select.currentText()

        maxt = maxh= maxp=mint= minh=minp=averaget=averageh=averagep = 0

        data = [[maxt, maxh, maxp], [mint, minh, minp], [averaget, averageh, averagep]]
        try :
            print(self.dirs_path+self.date_str)
            maxt, maxh, maxp, mint, minh, minp, averaget, averageh, averagep = get_data_from_file(self.dirs_path+self.date_str)
        except Exception as e :
            print(e)

        data = [[maxt, maxh, maxp/10], [mint, minh, minp/10], [averaget, averageh, averagep/10]]

        for i in range(1,4):
            for j in range(1,4):
                self.labels[4*i+j].setText(str(round(data[j-1][i-1],1)))
    #search界面的上部绘制
    def search_top(self):
        self.date_label = QLabel('日期 ：')
        self.year_label = QLabel('年')
        self.mouth_label = QLabel('月')
        self.day_label = QLabel('日')

        self.year_select = QComboBox()
        self.year_select.connect(self.year_select, SIGNAL("activated(int)"), self.show_data)

        self.mouth_select = QComboBox()
        self.mouth_select.connect(self.mouth_select, SIGNAL("activated(int)"), self.show_data)

        self.day_select = QComboBox()
        self.day_select.connect(self.day_select,SIGNAL("activated(int)"),self.show_data)


        for i in range(2017,2041):
            self.year_select.insertItem(i, self.tr(str(i)))
        for i in range(1,13):
            if i <10:
                self.mouth_select.insertItem(i, '0'+self.tr(str(i)))
            else:
                self.mouth_select.insertItem(i, self.tr(str(i)))
        for i in range(1,32):
            if i <10:
                self.day_select.insertItem(i, '0'+self.tr(str(i)))
            else:
                self.day_select.insertItem(i, self.tr(str(i)))

        self.year_select.setCurrentIndex(self.year_s)
        self.mouth_select.setCurrentIndex(self.mouth_s)
        self.day_select.setCurrentIndex(self.day_s)

        self.search_btn = QPushButton('查询')
        self.search_btn.clicked.connect(self.All_draw)

        self.t_btn = QPushButton("温度")
        self.t_btn.clicked.connect(self.T_s_draw)

        self.w_btn = QPushButton("湿度")
        self.w_btn.clicked.connect(self.W_s_draw)

        self.h_btn = QPushButton("大气压力")
        self.h_btn.clicked.connect(self.H_s_draw)

        top = QHBoxLayout()
        top.addWidget(self.date_label)
        top.addWidget(self.year_select)
        top.addWidget(self.year_label)
        top.addWidget(self.mouth_select)
        top.addWidget(self.mouth_label)
        top.addWidget(self.day_select)
        top.addWidget(self.day_label)

        top.addWidget(self.search_btn)
        top.addWidget(self.t_btn)
        top.addWidget(self.w_btn)
        top.addWidget(self.h_btn)

        self.top_widget = QWidget()
        self.top_widget.setLayout(top)


    #从数据文件获取数据
    def Datas(self):

        self.T_s = []
        self.H_s = []
        self.W_s = []
        self.Y_s = []
        if not os.path.isfile(self.dirs_path+self.date_str):
            return ;

        file = open(self.dirs_path+self.date_str,'r')
        line = file.readline()
        for line in file:
            datas = line.strip().split("\t")
            if datas[0] in ["max", "t", "h", "p"]:
                continue
            self.T_s.append(float(datas[0]))
            self.H_s.append(float(datas[2])/10) # 压强
            self.W_s.append(int(float(datas[1]))) # 湿度
            time_ = datas[3].split(":")
            mins = int(time_[0])*60 + int(time_[1])
            self.Y_s.append(mins/60)

        file.close()
    #绘制search的温度曲线
    def T_s_draw(self):

        self.Datas()

        plt.cla()
        self.max_t_s = max(self.T_s)
        self.min_t_s = min(self.T_s)
        plt.xlim(0, 24)
        plt.ylim(self.min_t_s-10, self.max_t_s+10)
        print(self.Y_s)
        plt.plot(self.Y_s[0:len(self.T_s)],self.T_s, color="red")

        plt.xlabel('time')
        plt.ylabel('data')
        self.canvas_s.draw()


    #绘制search 的压强曲线
    def H_s_draw(self):
        self.Datas()
        plt.cla()

        self.max_h_s = max(self.H_s)
        self.min_h_s = min(self.H_s)

        plt.xlim(0, 24)
        plt.ylim(self.min_h_s, self.max_h_s)
        plt.plot( self.Y_s[0:len(self.T_s)],self.H_s, color="blue")

        plt.xlabel('time')
        plt.ylabel('data')
        self.canvas_s.draw()

    #绘制湿度的曲线
    def W_s_draw(self):

        self.Datas()
        plt.cla()
        self.max_w_s = max(self.W_s)
        self.min_w_s = min(self.W_s)
        plt.xlim(0, 24)
        plt.ylim(self.min_w_s, self.max_w_s)
        plt.plot( self.Y_s[0:len(self.T_s)],self.W_s, color="black")
        plt.xlabel('time')
        plt.ylabel('data')
        self.canvas_s.draw()

    #绘制三个曲线
    def All_draw(self):

        self.Datas()
        plt.cla()
        ts = [max(self.W_s),max(self.T_s),max(self.H_s),min(self.W_s),min(self.T_s),min(self.H_s)]

        self.max_a = max(ts)
        self.min_a = min(ts)
        plt.xlim(0, 24)
        plt.ylim(self.min_a, self.max_a)
        plt.plot(self.Y_s[0:len(self.H_s)],self.H_s, color="blue", linewidth=1, linestyle="-", label="P")
        plt.plot(self.Y_s[0:len(self.T_s)],self.T_s, color="red", linewidth=1, linestyle="-", label="T")
        plt.plot(self.Y_s[0:len(self.W_s)],self.W_s, color="black", linewidth=1, linestyle="-", label="H")

        plt.xlabel('time')
        plt.ylabel('data')
        plt.legend(loc='upper right')
        self.canvas_s.draw()

    #绘制右下部分
    def DrawRightDown(self):

        self.Datas()

        plt.cla()
        if self.s_type == 0:
            self.T_s_draw()
        elif self.s_type == 1:
            self.H_s_draw()
        elif self.s_type == 2:
            self.W_s_draw()
        elif self.s_type == 3:
            self.seach_draw()
        else:
            pass

        plt.xlabel('time')
        plt.ylabel('data')
        self.canvas_s.draw()
    #绘制下部
    def search_down(self):
        self.grid_s = QGridLayout()
        self.grid_s.setSpacing(0)
        self.grid_s.setMargin(0)

        texts = [["","最大值","最小值","平均值"],["温度","","",""],["湿度","","",""],["大气压力","","",""]]

        for i in range(4):
            for j in range(4):
                temp = QLabel(texts[i][j])
                self.labels.append(temp)
                self.grid_s.addWidget(temp,i,j)

        self.grid_s_widget = QWidget()
        self.grid_s_widget.setFixedHeight(150)
        self.grid_s_widget.setFixedWidth(250)
        self.grid_s_widget.setStyleSheet("border:1px solid #cccccc;margin:0px")
        self.grid_s_widget.setLayout(self.grid_s)

        down  = QHBoxLayout()
        down.addWidget(self.grid_s_widget)
        down.addWidget(self.canvas_s)

        self.down_widget = QWidget()
        self.down_widget.setLayout(down)

        self.show_data()



    #search界面的主函数
    def search(self):

        self.labels = []

        self.s_type = -1 # 0 for T , 1 for H ,2 for W ,3 for search
        self.figure_s = plt.gcf()  # 返回当前的figure
        self.canvas_s = figureCanvas(self.figure_s)

        self.search_top()
        self.search_down()
        self.DrawRightDown()

        self.search_layout = QVBoxLayout()
        self.search_layout.addWidget(self.top_widget)
        self.search_layout.addWidget(self.down_widget)

        self.search_widget = QWidget()
        self.search_widget.setLayout(self.search_layout)

        self.setCentralWidget(self.search_widget)


    #帮助界面
    def help(self):
        helpLabel = QLabel(self)
        helpLabel.setFixedHeight(60)
        helpLabel.setFixedWidth(700)
        #self.helpLabel.setFont(QFont('帮助文档', 10, QFont.Bold))
        helpLabel.setText('帮助文档')
        helpLabel.setAlignment(Qt.AlignCenter)
        helpLabel.move(250,250)
        self.setCentralWidget(helpLabel)

app=QApplication(sys.argv)
main=MainWindow()
main.show()
app.exec_()
