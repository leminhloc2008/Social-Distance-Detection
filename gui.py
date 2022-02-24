import requests
import bs4
import webbrowser
from social_distance_detector import *
from googletrans import Translator

from pathlib import Path

from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, StringVar, filedialog

ASSETS_PATH = "assets"

translator = Translator()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def get_html_data(url):
    data = requests.get(url)
    return data

def covid_data(t):
    # get covid data
    url = "https://worldometers.info/coronavirus/"
    html_data = get_html_data(url)
    bs = bs4.BeautifulSoup(html_data.text, 'html.parser')
    info_div = bs.find("div", class_="content-inner").findAll("div", id="maincounter-wrap")
    # get data
    for i in range(3):
        infected = info_div[0].find("span", class_=None).get_text()
        die = info_div[1].find("span", class_=None).get_text()
        recovered = info_div[2].find("span", class_=None).get_text()

    if t==1:
        return infected
    elif t==2:
        return die
    else:
        return recovered

def get_country():

    # get country name
    name = country_name.get()

    # exceptions
    if country_name.get().lower() == "america" or country_name.get().lower() == "usa" or country_name.get().lower() == "unitedstates":
        name = "us"
    if country_name.get().lower() == "vietnam" or country_name.get().lower() == "vie":
        name = "viet-nam"
    if country_name.get().lower() == "england" or country_name.get().lower() == "unitedkingdom":
        name = "uk"

    url = "https://www.worldometers.info/coronavirus/country/"+name+"/"

    html_data = get_html_data(url)
    bs = bs4.BeautifulSoup(html_data.text, 'html.parser')
    info_div = bs.find("div", class_="content-inner").findAll("div", id="maincounter-wrap")

    # get data form info div
    for i in range(3):
        infected = info_div[0].find("span", class_=None).get_text()
        die = info_div[1].find("span", class_=None).get_text()
        recovered = info_div[2].find("span", class_=None).get_text()

    # update number
    canvas.itemconfigure(soCaText, text="Nhiễm: " + infected)
    canvas.itemconfigure(dieText, text="Tử Vong: " + die)
    canvas.itemconfigure(recoveredText, text="Khỏi: " + recovered)

    # update title
    translated = translator.translate(name, dest="vi")
    if translated.text == "chúng ta":
        translated.text = "Hoa Kỳ"
    if translated.text == "viet-nam":
        translated.text = "Việt Nam"
    if translated.text == "uk":
        translated.text = "Anh Quốc"
    if translated.text == "Châu Úc":
        translated.text = "Úc"
    canvas.itemconfigure(headingText, text="Số ca nhiễm tại " + translated.text)

def displayVideo():
    start_video(pathToVideo.get())

def StartWebcam():
    webcam_detect()

def browseFiles():
    filename = filedialog.askopenfilename(title="Select a File",
                                          filetypes=(("mp4 files","*.mp4*"),("avi files","*.avi*"),("all files","*.*")))
    pathToVideo.set(filename)

def openLink(event):
    webbrowser.open_new("https://github.com/leminhloc2008/Phan-Tich-Gian-Cach-Xa-Hoi")

def getStreamUrl():
    streamCam(streamingUrl.get())

def getPassUserCam():
    passCam(username.get(), password.get())

def startIpCamera():
    if not entry_3.get():
        getPassUserCam()

    else:
        getStreamUrl()

if __name__ == '__main__':
    root = Tk()
    #root.wm_iconbitmap(False, "icons\covid.ico")
    root.title("Phần mềm phát hiện người vi phạm giãn cách xã hội")
    root.geometry("900x600")
    root.configure(bg = "#D3F5FA")

    canvas = Canvas(root,bg = "#D3F5FA",height = 600,width = 900,bd = 0,highlightthickness = 0, relief = "ridge")

    canvas.place(x = 0, y = 0)
    canvas.create_text(286.0,8.0,anchor="nw",text="          Hệ thống nhận diện \nngười vi phạm giãn cách xã hội",
                    fill="#934A2A",font=("Roboto Bold", 25 * -1))

    canvas.create_text(522.0, 94.0, anchor="nw", text="Thông tin về đại dịch Covid 19", fill="#E33939",
                       font=("Roboto Bold", 22 * -1))

    canvas.create_text( 31.0,89.0,anchor="nw",text="                 Nhận diện \nngười vi phạm giãn cách xã hội",
        fill="#E33939",font=("Roboto Bold", 22 * -1))


    headingText = canvas.create_text( 573.0, 207.0, anchor="nw", text="Số ca nhiễm toàn cầu", fill="#E33939",
                        font=("Roboto Bold", 21 * -1))

    # viet nam covid data
    urlVie="https://worldometers.info/coronavirus/country/viet-nam"
    htmlDataVie = get_html_data(urlVie)
    bsVie = bs4.BeautifulSoup(htmlDataVie.text, 'html.parser')
    infoVie = bsVie.find("div", class_="content-inner").findAll("div", id="maincounter-wrap")

    #lay du lieu
    for i in range(3):
        infectedVie = infoVie[0].find("span", class_ = None).get_text()
        dieVie = infoVie[1].find("span", class_=None).get_text()
        recoveredVie = infoVie[2].find("span", class_=None).get_text()

    soCaText = canvas.create_text(518.0,247.0, anchor="nw", text="Nhiễm: " + covid_data(1),fill="#E33939",
        font=("Roboto Bold", 19 * -1))

    dieText = canvas.create_text(516.0, 276.0, anchor="nw", text="Tử vong: " + covid_data(2), fill="#E33939",
                       font=("Roboto Bold", 19 * -1))

    recoveredText = canvas.create_text(  518.0, 305.0, anchor="nw", text="Khỏi: " + covid_data(3), fill="#E33939",
                         font=("Roboto Bold", 19 * -1))

    canvas.create_text( 570.0,337.0,anchor="nw",text="Số ca nhiễm tại Việt Nam",fill="#E33939",
                        font=("Roboto Bold", 21 * -1))

    canvas.create_text( 522.0,369.0,anchor="nw",text="Nhiễm: " + infectedVie,fill="#E33939",
                        font=("Roboto Bold", 19 * -1))

    canvas.create_text(519.0,397.0,anchor="nw",text="Tử vong: " + dieVie,fill="#E33939",
                       font=("Roboto Bold", 19 * -1))

    canvas.create_text( 522.0,425.0,anchor="nw",text="Khỏi: " + recoveredVie,fill="#E33939",
                        font=("Roboto Bold", 19 * -1))

    entry_image_1 = PhotoImage( file=relative_to_assets("entry_1.png"))
    entry_bg_1 = canvas.create_image( 679.5,181.0,image=entry_image_1)
    country_name = StringVar()
    entry_1 = Entry(bd=0, bg="#F3EBEB", textvariable=country_name, highlightthickness=0)
    entry_1.place(x=596.0, y=167.0, width=167.0, height=26.0)

    button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
    button_1 = Button(image=button_image_1,borderwidth=0,highlightthickness=0,
                      command=get_country,relief="flat")
    button_1.place(x=793.0,y=167.0,width=62.0,height=28.0)

    button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
    button_2 = Button(image=button_image_2,borderwidth=0,highlightthickness=0,
                      command=StartWebcam,relief="flat")
    button_2.place(x=140.0,y=526.0,width=135.0,height=52.0)

    canvas.create_text(626.0,134.0,anchor="nw",text="Nhập tên nước",fill="#000000",font=("Roboto", 17 * -1))

    pathToVideo = StringVar()
    entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
    entry_bg_2 = canvas.create_image(128.5,246.0,image=entry_image_2)
    entry_2 = Entry(bd=0,bg="#F3EBEB",textvariable=pathToVideo, highlightthickness=0)
    entry_2.place(x=45.0,y=232.0,width=167.0,height=26.0)

    streamingUrl = StringVar()
    entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
    entry_bg_3 = canvas.create_image(100.5,392.0,image=entry_image_3)
    entry_3 = Entry(bd=0,bg="#F3EBEB",textvariable=streamingUrl,highlightthickness=0)
    entry_3.place(x=17.0,y=378.0,width=167.0,height=26.0)

    username = StringVar()
    entry_image_4 = PhotoImage(file=relative_to_assets("entry_4.png"))
    entry_bg_4 = canvas.create_image(352.5, 392.0,image=entry_image_4)
    entry_4 = Entry(bd=0,bg="#F3EBEB", textvariable=username, highlightthickness=0)
    entry_4.place(x=269.0,y=378.0,width=167.0,height=26.0)

    password = StringVar()
    entry_image_5 = PhotoImage(file=relative_to_assets("entry_5.png"))
    entry_bg_5 = canvas.create_image(352.5,451.0,image=entry_image_5)
    entry_5 = Entry(bd=0,bg="#F3EBEB",textvariable=password,highlightthickness=0)
    entry_5.place(x=269.0,y=437.0,width=167.0,height=26.0)

    button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
    button_3 = Button(image=button_image_3,borderwidth=0,highlightthickness=0,
                      command=displayVideo,relief="flat")
    button_3.place(x=96.0,y=277.0,width=88.0,height=28.0)

    button_image_4 = PhotoImage(file=relative_to_assets("button_4.png"))
    button_4 = Button(image=button_image_4, borderwidth=0,  highlightthickness=0,
                      command=browseFiles, relief="flat")
    button_4.place(x=242.0,y=232.0,width=88.0,height=28.0)

    button_image_5 = PhotoImage(file=relative_to_assets("button_5.png"))
    button_5 = Button(image=button_image_5,borderwidth=0,highlightthickness=0,
                      command=startIpCamera,relief="flat")
    button_5.place(x=66.0,y=430.0,width=88.0,height=28.0)

    canvas.create_text(44.0,351.0,anchor="nw",text="Streaming URL",
        fill="#000000",font=("Roboto", 17 * -1))

    canvas.create_text(313.0,351.0,anchor="nw",text="Username",fill="#000000",font=("Roboto", 17 * -1))

    canvas.create_text(313.0,412.0,anchor="nw",text="Mật khẩu",fill="#000000",font=("Roboto", 17 * -1) )

    canvas.create_text(101.0,200.0,anchor="nw",text="Đường dẫn video",fill="#000000",font=("Roboto", 17 * -1))

    canvas.create_text(207.0,382.0,anchor="nw",text="hoặc",
        fill="#000000",font=("Roboto Italic", 17 * -1))

    canvas.create_text(151.0,316.0,anchor="nw",text="IP Camera",
        fill="#3F9F5A",font=("Roboto Bold", 23 * -1))

    canvas.create_text(161.0,488.0,anchor="nw",text="Webcam",fill="#3F9F5A",font=("Roboto Bold", 23 * -1)
    )

    canvas.create_text(573.0,463.0,anchor="nw",text="Số liệu được cập nhật liên tục",
                       fill="#000000",font=("Roboto Italic", 17 * -1))

    canvas.create_text(124.0,162.0, anchor="nw",text="Video",fill="#3F9F5A",font=("Roboto Bold", 23 * -1))

    image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(509.0,154.0,image=image_image_1)

    image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(239.0,37.0,image=image_image_2)

    image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
    image_3 = canvas.create_image(58.0,180.0,image=image_image_3)

    root.resizable(False, False)
    root.mainloop()
