# coding=utf-8
#-------------------------------------------------------------------------------
# Name:        Image processing tool
# Purpose:     Process Images
# Author:      shenglongshuai
# Created:     07/28/2017
#-------------------------------------------------------------------------------
from __future__ import division
from tkinter import *

import tkinter.messagebox
from tkinter.simpledialog import askstring, askinteger
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import os
import glob
import random
from tkinter.scrolledtext import ScrolledText
import cv2
import numpy as np
import glob as gb
import tkinter.filedialog
from tkinter.simpledialog import askstring, askinteger
import matplotlib
import math
import time
from matplotlib import pyplot as plt

# colors for the bboxes
COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 180,180

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("隧道图像识别软件v1.0")

        # 设置窗口的大小宽x高+偏移量
        #self.parent.geometry('800x500+500+200')
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.txtName = ''
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.classcandidate_filename = 'Classes/class.txt'
        self.index = ''
        self.annotationPath = ''
        self.imageHeight = ''
        self.imageDepth = 3
        self.imageWidth = ''
        self.sizePath=''

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "图像集序号：")
        self.label.grid(row = 0, column = 1, sticky = W)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1)
        self.ldBtn = Button(self.frame, text = " 加 载 ", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 1,sticky = E)

        # main panel for labeling
        self.scrollpane = Frame(self.frame, bd=2, relief=SUNKEN)
        self.xscrollbar = Scrollbar(self.scrollpane, orient=HORIZONTAL)
        self.xscrollbar.grid(row=0, column=1, sticky=E + W)
        self.yscrollbar = Scrollbar(self.scrollpane)
        #self.yscrollbar.pack(side=LEFT)
        self.yscrollbar.grid(row=1, column=0, sticky=W + N + S)
        self.mainPanel = Canvas(self.scrollpane, bd=0, cursor='tcross', scrollregion=(0, 0, 3000, 1800)
                                , xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.mainPanel.grid(row=1, column=1, sticky=N + S + E +W)
        self.xscrollbar.config(command=self.mainPanel.xview)
        self.yscrollbar.config(command=self.mainPanel.yview)
        self.mainPanel.config(scrollregion=self.mainPanel.bbox(ALL))

        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.scrollpane.grid(row=1, column=1, rowspan=4, sticky=W + N)

        # menu for choose class
        self.menubar = Menu(root)
        filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件", menu=filemenu)
        openmenu = Menu(filemenu, tearoff=0)
        filemenu.add_cascade(label="打开", menu=openmenu)
        openmenu.add_command(label="图像目录", command=self.openImages)
        #openmenu.add_command(label="标签目录", command=self.openLabel)
        openmenu.add_command(label="图片文件夹", command=self.openFile)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.frame.quit)

        toolmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="工具", menu=toolmenu)
        self.edgemenu = Menu(toolmenu, tearoff=0)
        toolmenu.add_cascade(label="边缘检测",menu=self.edgemenu)
        self.edgemenu.add_command(label="canny",command=self.canny)

        #toolmenu.add_command(label="单张canny", command=self.cannybar)
        #self.cannymenu.add_command(label="批量canny", command=self.canny)
        self.edgemenu.add_command(label="sobel", command=self.sobel)
        self.edgemenu.add_command(label="laplacian", command=self.laplacian)
        toolmenu.add_separator()

        self.binarymenu = Menu(toolmenu, tearoff=0)
        toolmenu.add_cascade(label='二值化处理', menu=self.binarymenu)
        self.binarymenu.add_command(label="Gray Image", command=self.GrayImage)
        self.binarymenu.add_command(label="BINARY", command=self.BINARY)
        self.binarymenu.add_command(label="BINARY_INV", command=self.BINARY_INV)
        self.binarymenu.add_command(label="TRUNC", command=self.TRUNC)
        self.binarymenu.add_command(label="TOZERO", command=self.TOZERO)
        self.binarymenu.add_command(label="TOZERO_INV", command=self.TOZERO_INV)

        toolmenu.add_separator()

        self.angularmenu = Menu(toolmenu, tearoff=0)
        toolmenu.add_cascade(label="角点检测", menu=self.angularmenu)
        self.angularmenu.add_command(label="harris", command=self.harris)
        self.angularmenu.add_command(label="Shi-Tomasi", command=self.Shi_Tomasi)
        self.angularmenu.add_command(label="brisk", command=self.brisk)

        aboutmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="关于", menu=aboutmenu)
        aboutmenu.add_command(label="捐赠", command=self.Email)
        aboutmenu.add_command(label="联系作者", command=self.Email)
        root.config(menu=self.menubar)

        self.classname = StringVar()
        self.classcandidate = ttk.Combobox(self.frame, state='readonly', textvariable=self.classname)
        #self.classcandidate.grid(row=1, column=2)
        if os.path.exists(self.classcandidate_filename):
            with open(self.classcandidate_filename) as cf:
                for line in cf.readlines():
                    # print line
                    self.cla_can_temp.append(line.strip('\n'))
        # print self.cla_can_temp
        self.classcandidate['values'] = self.cla_can_temp
        self.classcandidate.current(0)
        self.currentLabelclass = self.classcandidate.get()  # init
        self.btnclass = Button(self.frame, text='确认', command=self.setClass)
        #self.btnclass.grid(row=2, column=2, sticky=W + E)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='标注结果：')
        #self.lb1.grid(row=3, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=12)
        #self.listbox.grid(row=4, column=2, sticky=N + S)
        self.btnDel = Button(self.frame, text='删除', command=self.delBBox)
        #self.btnDel.grid(row=5, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='清空', command=self.clearBBox)
        #self.btnClear.grid(row=6, column=2, sticky=W + E + N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 7, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< 上一张', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='下一张 >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 1, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "页码:     /    ")
        self.progLabel.pack( side = LEFT,padx = 1)
        self.tmpLabel = Label(self.ctrPanel, text = "跳转到图片 No.")
        self.tmpLabel.pack(side = LEFT,padx = 1)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = RIGHT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 1)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "样例：")
        self.tmpLabel2.pack(side =LEFT, pady = 0)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        # display dialog
        self.dialogPanel = Frame(self.frame, border=10)
        self.dialogPanel.grid(row=1, column=0, rowspan=5, sticky=S)
        self.dialogLabel = Label(self.dialogPanel, text="                     日志:")
        self.dialogLabel.pack(side=BOTTOM, pady=5)
        self.dialogLabel.grid(row=4, column=0, sticky=W + S)
        self.dialogText = ScrolledText(self.dialogPanel, width=30, height=20)
        self.dialogText.config(state=DISABLED)
        self.dialogText.grid(row=5, column=0, sticky=W + S)

        # for debugging
        # self.setImage()
        # self.loadDir()

    def canny(self):
        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        numMin = askinteger('请输入参数范围', "最小值")
        numMax = askinteger('请输入参数范围', "最大值")
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath, 0)
            img = cv2.GaussianBlur(img, (3, 3), 0)
            canny = cv2.Canny(img, numMax, numMin)  # 此处参数是范围，数值越大越不细致，具体数值根据图片情况更改

            win = cv2.namedWindow('Canny', flags=0)
            cv2.imshow('Canny', canny)
            # cv2.imwrite("C:/Users/sls/Desktop/2//" + eachDir, canny)  # 图片输出的目录，更改成自己需要的
            cv2.imwrite(savePath + '/' + eachDir, canny)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   Canny边缘检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def sobel(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        numMin = askinteger('请输入求导次数', "dx")
        numMax = askinteger('请输入求导次数', "dy")
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            x = cv2.Sobel(img, cv2.CV_16S, numMin, 0)
            y = cv2.Sobel(img, cv2.CV_16S, 0, numMax)

            absX = cv2.convertScaleAbs(x)  # 转回uint8
            absY = cv2.convertScaleAbs(y)

            dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
            win = cv2.namedWindow('Sobel', flags=0)
            cv2.imshow("Sobel", dst)

            # cv2.imwrite("C:/Users/sls/Desktop/1/" + eachDir, canny)  # 图片输出的目录，更改成自己需要的
            cv2.imwrite(savePath + '/' + eachDir, dst)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   Sobel边缘检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def laplacian(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath, 0)

            gray_lap = cv2.Laplacian(img, cv2.CV_16S, ksize=3)
            dst = cv2.convertScaleAbs(gray_lap)

            win = cv2.namedWindow('Laplacian', flags=0)
            cv2.imshow('Laplacian', dst)
            # cv2.imwrite("C:/Users/sls/Desktop/laplacian/" + eachDir, canny)  # 图片输出的目录，更改成自己需要的
            cv2.imwrite(savePath + '/' + eachDir, dst)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        self.dialogText.config(state=NORMAL)
        ss = '\n   Laplacian边缘检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def cannybar(self):

        def CannyThreshold(lowThreshold):
            default_dir = ""
            savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))
            detected_edges = cv2.GaussianBlur(gray, (3, 3), 0)
            detected_edges = cv2.Canny(detected_edges, lowThreshold, lowThreshold * ratio, apertureSize=kernel_size)
            dst = cv2.bitwise_and(img, img, mask=detected_edges)
            cv2.imshow('canny demo', dst)
            cv2.imwrite(savePath + '/' + eachDir, dst)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        lowThreshold = 0
        max_lowThreshold = 100
        ratio = 3
        kernel_size = 3

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            print (img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            cv2.namedWindow('canny demo')

            cv2.createTrackbar('Min threshold', 'canny demo', lowThreshold, max_lowThreshold, CannyThreshold)

            CannyThreshold(0)  # initialization



    def harris(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            gray = np.float32(gray)
            dst = cv2.cornerHarris(gray, 2, 3, 0.04)

            # result is dilated for marking the corners, not important
            dst = cv2.dilate(dst, None)

            # Threshold for an optimal value, it may vary depending on the image.
            img[dst > 0.01 * dst.max()] = [0, 0, 255]

            win = cv2.namedWindow('Harris', flags=0)
            cv2.imshow('Harris', img)

            cv2.imwrite(savePath + '/' + eachDir, img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   Harris角点检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def Shi_Tomasi (self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
            # 返回的结果是[[ 311., 250.]] 两层括号的数组。
            corners = np.int0(corners)
            for i in corners:
                x, y = i.ravel()
                cv2.circle(img, (x, y), 3, 255, -1)

            win = cv2.namedWindow('Shi_Tomasi', flags=0)
            cv2.imshow('Shi_Tomasi', img)
            cv2.imwrite(savePath + '/' + eachDir, img)
            cv2.waitKey(0)

        self.dialogText.config(state=NORMAL)
        ss = '\n   Shi_Tomasi角点检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def brisk(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            brisk = cv2.BRISK_create()
            (kpt, desc) = brisk.detectAndCompute(img, None)
            bk_img = img.copy()
            out_img = img.copy()
            out_img = cv2.drawKeypoints(bk_img, kpt, out_img)
            win = cv2.namedWindow('brisk', flags=0)
            cv2.imshow('brisk', out_img)
            cv2.imwrite(savePath + '/' + eachDir, out_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   Brisk角点检测的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))


    def GrayImage(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            win = cv2.namedWindow('Gray Image', flags=0)
            cv2.imshow('Gray Image', gray)
            cv2.imwrite(savePath + '/' + eachDir, gray)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   Gray二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def BINARY(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            #感兴趣区域
            roiimg=img[0:500,500:1500]

            GrayImage = cv2.cvtColor(roiimg, cv2.COLOR_BGR2GRAY)
            ret, thresh1 = cv2.threshold(GrayImage, 80, 255, cv2.THRESH_BINARY)

            #thresh1=img.copyTo(roiimg)

            win = cv2.namedWindow('BINARY', flags=0)
            cv2.imshow('BINARY', thresh1)
            cv2.imwrite(savePath + '/' + eachDir, thresh1)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   BINARY二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def BINARY_INV(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, thresh2 = cv2.threshold(GrayImage, 127, 255, cv2.THRESH_BINARY_INV)
            win = cv2.namedWindow('BINARY_INV', flags=0)
            cv2.imshow('BINARY_INV', thresh2)
            cv2.imwrite(savePath + '/' + eachDir, thresh2)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   BINARY_INV二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def TRUNC(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, thresh3 = cv2.threshold(GrayImage, 127, 255, cv2.THRESH_TRUNC)
            win = cv2.namedWindow('TRUNC', flags=0)
            cv2.imshow('TRUNC', thresh3)
            cv2.imwrite(savePath + '/' + eachDir, thresh3)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   TRUNC二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def TOZERO(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, thresh4 = cv2.threshold(GrayImage, 127, 255, cv2.THRESH_TOZERO)
            win = cv2.namedWindow('TOZERO', flags=0)
            cv2.imshow('TOZERO', thresh4)
            cv2.imwrite(savePath + '/' + eachDir, thresh4)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   TOZERO二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))

    def TOZERO_INV(self):

        default_dir = ""
        savePath = tkinter.filedialog.askdirectory(title=u"保存路径", initialdir=(os.path.expanduser(default_dir)))

        # path = 'C:/Users/sls/Desktop/1/'  # 图片读取的目录，更改成自己需要的
        path = self.filePath + '/'
        pathDir = os.listdir(path)
        for eachDir in pathDir:
            imgPath = path + eachDir
            print (imgPath)
            img = cv2.imread(imgPath)
            GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, thresh5 = cv2.threshold(GrayImage, 127, 255, cv2.THRESH_TOZERO_INV)
            win = cv2.namedWindow('TOZERO_INV', flags=0)
            cv2.imshow('TOZERO_INV', thresh5)
            cv2.imwrite(savePath + '/' + eachDir, thresh5)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.dialogText.config(state=NORMAL)
        ss = '\n   TOZERO_INV二值化处理的图片已保存\n'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '%s' % (ss))



    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        # print self.imageDir
        self.index = self.imageDir.split('\\')
        # print self.index
        #print self.category
        self.annotationPath = r'annotation/' + self.index[1].replace('\n', '') + '/'

        # print self.annotationPath
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.*'))
        #print self.imageList
        if len(self.imageList) == 0:
            print ('图片集输入错误')
            tkinter.messagebox.showerror("error", "请输入正确的图片集序号")
            self.dialogText.config(state=NORMAL)
            self.dialogText.insert(0.0, '图片集输入错误\n')
            self.dialogText.config(state=DISABLED)
            return
        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %self.category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        # self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        self.egDir = os.path.join(r'./Examples/demo')
        print (os.path.exists(self.egDir))
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.*'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print ('%d images loaded from %s' %(self.total, s))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.imageHeight = str(self.img.size[1])
        self.imageWidth = str(self.img.size[0])
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        #self.mainPanel.config(width=max(self.tkimg.width(), 400), height=max(self.tkimg.height(), 400), yscrollcommand=scr1.set)
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        #self.sizePath = r'Size/' + self.index[1] + '/'
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    # tmp = [int(t.strip()) for t in line.split()]
                    tmp = line.split()
                    #print tmp
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(int(tmp[0]), int(tmp[1]),
                                                            int(tmp[2]), int(tmp[3]),
                                                            width = 2,
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    # print tmpId
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%s : (%d, %d) -> (%d, %d)' %(tmp[4],int(tmp[0]), int(tmp[1]),int(tmp[2]), int(tmp[3])))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')

        # print self.sizePath+self.txtName+'.txt'
        #self.writeSize(self.sizePath)
        # self.writeSize(size)
        print ('Image No. %d saved' %(self.cur))
        self.dialogText.config(state=NORMAL)
        self.dialogText.insert(0.0, 'Image No. %d \n' %(self.cur))
        self.dialogText.config(state=DISABLED)
        # tkMessageBox.showinfo("", "保存成功")

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):

        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):

        if self.cur < self.total:
            self.cur += 1
            self.loadImage()
        else:
            tkMessageBox.showinfo("喵", "已到最后一张图片")

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:

            self.cur = idx
            self.loadImage()
        else:
            tkMessageBox.showwarning("warning", "请输入1到%d之间的数" % self.total, )
            self.dialogText.config(state=NORMAL)
            self.dialogText.insert(0.0, '请输入1到%d之间的数\n' % self.total)
            self.dialogText.config(state=DISABLED)

    def setClass(self):
        self.currentLabelclass = self.classcandidate.get()
        print ('set label class to :', self.currentLabelclass)

    def setImage(self, imagepath = r'test2.png'):
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = self.tkimg.width())
        self.mainPanel.config(height = self.tkimg.height())
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

    # def getAnnotation(self):
        # self.get

    def openImages(self):
        os.startfile(self.imageDir)

    def openLabel(self):
        os.startfile(self.outDir)

    def Email(self):
        tkinter.messagebox.showinfo("作者邮箱", "作者邮箱：\nshenglongshuai@outlook.com")

    def openFile(self):
        default_dir = ""
        fpath = tkinter.filedialog.askdirectory(title=u"选择文件", initialdir=(os.path.expanduser(default_dir)))
        self.filePath = fpath
        for filename in os.listdir(fpath):  # listdir的参数是文件夹的路径
            print (filename )


        self.dialogText.config(state=NORMAL)
        ss='\n   已从文件夹读取图片，请从工具里选择对图片进行的操作'
        self.dialogText.insert(0.0, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+'%s' %(ss))

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width = True, height = True)
    root.mainloop()
