##import套件
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import plotly.graph_objects as go
import os

##檢查資料夾是否存在，並創建資料夾
if not os.path.exists("images"):
    os.mkdir("images")
    
##阻擋瀏覽器跳出通知框
options = Options()
options.add_argument("--disable-notifications")

##執行webdriver
chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
chrome.maximize_window()#最大化瀏覽器
chrome.get("https://www.facebook.com/")#跳轉到facebook頁面
email = chrome.find_element_by_id("email")#取得帳號框元素ID
password = chrome.find_element_by_id("pass")#取得密碼框元素ID
email.send_keys(' ')#此處請填自己的帳號
password.send_keys(' ')#此處請填自己的密碼
password.submit()#用submit方法送出
time.sleep(3)#等待3秒

##等待抓到<meta name="theme-color">執行下一步，最多等待10秒
theam = WebDriverWait(chrome, 10).until(
    EC.presence_of_element_located((By.NAME, "theme-color"))
)

##瀏覽器抓取facebook名稱
chrome.find_element_by_link_text(" ").click()#此處請輸入自己facebook名稱
time.sleep(2)
friends=str(chrome.current_url)+"&sk=friends"
chrome.get(friends)#測試
time.sleep(2)

##滾動捲軸來動態載入更多的好友
SCROLL_PAUSE_TIME =2
last_height = chrome.execute_script("return document.body.scrollHeight")#取得卷軸高度

while True:
    chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")# 滾動到底
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = chrome.execute_script("return document.body.scrollHeight") #計算新的高度
    ##比較新舊高度差別
    if new_height == last_height:
        break
    last_height = new_height

##使用BeautifulSoup解析當前網頁原始碼
soup = BeautifulSoup(chrome.page_source, 'html.parser') 

##設定陣列與變數用來後續存資料
arrA = [] #放名字
arrB = [] #共同好友數
arrC = [] #放取出順序
x=1

##取得所有好友的div區塊原始碼
titles = soup.find_all('div', {
    'class': 'bp9cbjyn ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi n1f8r23x rq0escxv j83agx80 bi6gxh9e discj3wi hv4rvrfc ihqw7lf3 dati1w0a gfomwglr'})
##迴圈分別取出姓名及共同好友數
for title in titles:
    post = title.find('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em mdeji52x a5q79mjw g1cxx5fr lrazzd5p oo9gr5id'})
    num=title.find('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 m9osqain b1v8xokw'})

    ##判斷是某有取得資料並將資料解析存到變數
    if post:
        #print(post.getText())
        fname=post.getText() #提取原始碼中的Text文字
        if num:
            A=re.findall(r"\d+\.?\d*",num.getText())#找尋文字中所有匹配的文字
            A="".join(A)#陣列轉成字串
            int(A)#字串轉成整數
            #print(A)
        else:
            #print(0)
            A=0 #無資料設為0
        ##將資料依序存入字串    
        arrA.append(fname)
        arrB.append(int(A))
        arrC.append(str(x))
        x=x+1
##print(arrA)
##print(arrB)
##print(arrC)

##繪圖
size=arrB.copy()#複製共同好友數陣列作為圖形大小依據
##將資料導入並設定圖形及大小
fig = go.Figure(data=[go.Scatter(
    x=arrC, y=arrB.copy(),#x軸y軸依據
    text=arrA,#好友名字
    mode='markers',
    marker=dict(
        size=size,
        sizemode='area',
        sizeref=2.*max(size)/(80.**2),
        sizemin=4
        
    )
)])
##設定x軸y軸名稱及標題、字體大小顏色
fig.update_layout(
    title="臉書共同好友數視覺圖",
    xaxis_title="臉書好友順序",
    yaxis_title="共同好友數量",
    font=dict(
        size=16,
        color="#7f7f7f"
    )
)
##顯示圖表
fig.show()

##儲存圖表到剛剛的資料夾
fig.write_image("images/fig1.png")