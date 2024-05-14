import tkinter as tk
from functools import partial
import threading
import socket
from tkinter import messagebox
from PIL import Image, ImageTk  # Sử dụng PIL để xử lý hình ảnh
import pygame

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caro by Python")
        self.Buts = {}
        self.memory = []
        self.Threading_socket = Threading_socket(self)
        self.config(background="#BDB76B")
        print(self.Threading_socket.name)
        # Khởi tạo pygame để phát âm thanh
        pygame.mixer.init()
        pygame.mixer.music.load("assets/music_game.mp3")  # Load file nhạc
        pygame.mixer.music.play(-1)  # Phát nhạc lặp lại vô hạn
        self.effect_volume = 1.0  # Âm lượng hiệu ứng âm thanh
        self.music_volume = 1.0  # Âm lượng nhạc nền

        # Tải hình ảnh biểu tượng bánh răng
        self.settings_icon = ImageTk.PhotoImage(Image.open("assets/setting.png").resize((20, 20)))

        # Tải hình ảnh biểu tượng gửi tin nhắn
        self.send_icon = ImageTk.PhotoImage(Image.open("assets/send_icon.png").resize((15, 15)))

    def showFrame(self):
        frame1 = tk.Frame(self, background="#BDB76B")
        frame1.grid(row=0, column=0, sticky='nsew')

        frame2 = tk.Frame(self, background="#BDB76B")
        frame2.grid(row=1, column=0, sticky='nsew')

        frame3 = tk.Frame(self, background="#BDB76B")
        frame3.grid(row=1, column=1, sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Nút Setting với hình ảnh biểu tượng bánh răng
        setting_button = tk.Button(frame1, image=self.settings_icon, width=24, height=24, command=self.openSettings)
        setting_button.grid(row=0, column=0, padx=10)
        setting_button.config(background="#006400")  # Đặt màu nền cho nút "Setting"

        Undo = tk.Button(frame1, text="Undo", width=10,  # nút quay lại
                         command=partial(self.Undo, synchronized=True), font=("Cutie Pie", 11, "bold"), foreground="white")
        Undo.grid(row=0, column=1, padx=10)
        Undo.config(background="#006400")  # Đặt màu nền cho nút "Undo"

        lbl_ip = tk.Label(frame1, text="IP", pady=4, font=("Cutie Pie", 11, "bold"), foreground="#006400")  # Nhãn "IP"
        lbl_ip.grid(row=0, column=2)
        lbl_ip.config(background="#BDB76B")  # Đặt màu nền cho nhãn "IP"

        inputIp = tk.Entry(frame1, width=20, highlightbackground="#006400", highlightthickness=2)  # Khung nhập địa chỉ ip với viền màu xanh
        inputIp.grid(row=0, column=3, padx=5)

        connectBT = tk.Button(frame1, text="Connect", width=10,
                              command=lambda: self.Threading_socket.clientAction(inputIp.get()), font=("Cutie Pie", 11, "bold"), foreground="white")
        connectBT.grid(row=0, column=4, padx=3)
        connectBT.config(background="#006400")  # Đặt màu nền cho nút "Connect"

        makeHostBT = tk.Button(frame1, text="MakeHost", width=10,  # nút tạo host
                               command=lambda: self.Threading_socket.serverAction(), font=("Cutie Pie", 11, "bold"), foreground="white")
        makeHostBT.grid(row=0, column=5, padx=30)
        makeHostBT.config(background="#006400")  # Đặt màu nền cho nút "MakeHost"

        for x in range(Ox):   # tạo ma trận button Ox * Oy
            for y in range(Oy):
                self.Buts[x, y] = tk.Button(frame2, font=('arial', 15, 'bold'), height=1, width=2,
                                            borderwidth=2, command=partial(self.handleButton, x=x, y=y))
                self.Buts[x, y].grid(row=x, column=y)
                self.Buts[x, y].config(background="#fffacd")  # Đặt màu nền cho nút bằng mã màu RGB

        # Tải logo game
        self.logo = ImageTk.PhotoImage(Image.open("assets/caro_logo2.png").resize((450, 450)))  # Đảm bảo đã có file logo.png
        logo_label = tk.Label(frame3, image=self.logo, background="#BDB76B")
        logo_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Thêm khung chat
        self.chat_display = tk.Text(frame3, height=15, width=50, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_display.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        self.chat_entry = tk.Entry(frame3, width=50)  # Đặt độ rộng là 50
        self.chat_entry.grid(row=2, column=0, padx=0, pady=0)

        send_button = tk.Button(frame3, image=self.send_icon, width=24, height=24, command=self.sendMessage)
        send_button.grid(row=2, column=1, padx=0, pady=0)  # Đặt padx và pady thành 5 hoặc một giá trị nhỏ hơn
        send_button.config(background="#006400")  # Đặt màu nền cho nút "send"

    def sendMessage(self):
        message = self.chat_entry.get()
        if message:
            self.displayMessage("You: " + message)
            self.Threading_socket.sendData("message|{}".format(message))
            self.chat_entry.delete(0, tk.END)

    def displayMessage(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def handleButton(self, x, y):
        # Phát âm thanh khi click vào nút
        effect_sound = pygame.mixer.Sound("assets/effect_click.wav")
        effect_sound.set_volume(self.effect_volume)
        effect_sound.play()
        if self.Buts[x, y]['text'] == "": #Kiểm tra ô có ký tự rỗng hay không
            if self.memory.count([x, y]) == 0:
                self.memory.append([x, y])
            if len(self.memory) % 2 == 1:
                self.Buts[x, y]['text'] = 'O'
                self.Buts[x, y]['foreground'] = 'blue'  # Đặt màu xanh cho chữ 'O'
                self.Threading_socket.sendData("{}|{}|{}|".format("hit", x, y))
                if(self.checkWin(x, y, "O")):
                    self.notification("Winner", "O")
                    self.newGame()
            else:
                print(self.Threading_socket.name)
                self.Buts[x, y]['text'] = 'X'
                self.Buts[x, y]['foreground'] = 'red'  # Đặt màu đỏ cho chữ 'X'
                self.Threading_socket.sendData("{}|{}|{}|".format("hit", x, y))
                if(self.checkWin(x, y, "X")):
                    self.notification("Winner", "X")
                    self.newGame()

    def openSettings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.config(background="#BDB76B")

        music_frame = tk.Frame(settings_window, background="#BDB76B")
        music_frame.pack(pady=10)

        tk.Label(music_frame, text="Music Volume", background="#BDB76B", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        music_volume_slider = tk.Scale(music_frame, from_=0, to=1, resolution=0.1, orient="horizontal", command=self.setMusicVolume,
                                        troughcolor="#0000FF", sliderrelief='flat')
        music_volume_slider.set(self.music_volume)
        music_volume_slider.pack(side=tk.LEFT, padx=5)

        effect_frame = tk.Frame(settings_window, background="#BDB76B")
        effect_frame.pack(pady=10)

        tk.Label(effect_frame, text="Effect Volume", background="#BDB76B", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        effect_volume_slider = tk.Scale(effect_frame, from_=0, to=1, resolution=0.1, orient="horizontal", command=self.setEffectVolume,
                                        troughcolor="#0000FF", sliderrelief='flat')  # Màu xanh dương
        effect_volume_slider.set(self.effect_volume)
        effect_volume_slider.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(settings_window, text="Close", command=settings_window.destroy, font=("Cutie Pie", 11, "bold"), foreground="white")
        close_button.pack(pady=10)
        close_button.config(background="#ff0000")  # Đặt màu nền cho nút "close"



    def setMusicVolume(self, volume):
        self.music_volume = float(volume)
        pygame.mixer.music.set_volume(self.music_volume)

    def setEffectVolume(self, volume):
        self.effect_volume = float(volume)

    def notification(self, title, msg):
        messagebox.showinfo(str(title), str(msg))

    def checkWin(self, x, y, XO):
        count = 0
        i, j = x, y
        while(j < Ox and self.Buts[i, j]["text"] == XO):
            count += 1
            j += 1
        j = y
        while(j >= 0 and self.Buts[i, j]["text"] == XO):
            count += 1
            j -= 1
        if count >= 6:
            return True
        # check cột
        count = 0
        i, j = x, y
        while(i < Oy and self.Buts[i, j]["text"] == XO):
            count += 1
            i += 1
        i = x
        while(i >= 0 and self.Buts[i, j]["text"] == XO):
            count += 1
            i -= 1
        if count >= 6:
            return True
        # check cheo phai
        count = 0
        i, j = x, y
        while(i >= 0 and j < Ox and self.Buts[i, j]["text"] == XO):
            count += 1
            i -= 1
            j += 1
        i, j = x, y
        while(i <= Oy and j >= 0 and self.Buts[i, j]["text"] == XO):
            count += 1
            i += 1
            j -= 1
        if count >= 6:
            return True
        # check cheo trai
        count = 0
        i, j = x, y
        while(i < Oy and j < Ox and self.Buts[i, j]["text"] == XO):
            count += 1
            i += 1
            j += 1
        i, j = x, y
        while(i >= 0 and j >= 0 and self.Buts[i, j]["text"] == XO):
            count += 1
            i -= 1
            j -= 1
        if count >= 6:
            return True
        return False

    def Undo(self, synchronized):
        if(len(self.memory) > 0):
            x = self.memory[len(self.memory) - 1][0]
            y = self.memory[len(self.memory) - 1][1]
            # print(x,y)
            self.Buts[x, y]['text'] = ""
            self.memory.pop()
            if synchronized == True:
                self.Threading_socket.sendData("{}|".format("Undo"))
            print(self.memory)
        else:
            print("No character")

    def newGame(self):
        for x in range(Ox):
            for y in range(Oy):
                self.Buts[x, y]["text"] = ""

class Threading_socket():
    def __init__(self, gui):
        super().__init__()
        self.dataReceive = ""
        self.conn = None
        self.gui = gui
        self.name = ""

    def clientAction(self, inputIP):
        self.name = "client"
        print("client connect ...............")
        HOST = inputIP  # Cấu hình địa chỉ server
        PORT = 8000              # Cấu hình Port sử dụng
        self.conn = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # Cấu hình socket
        self.conn.connect((HOST, PORT))  # tiến hành kết nối đến server
        self.gui.notification("Đã kết nối tới", str(HOST))
        t1 = threading.Thread(target=self.client)  # tạo luồng chạy client
        t1.start()

    def client(self):
        while True:
            self.dataReceive = self.conn.recv(
                1024).decode()  # Đọc dữ liệu server trả về
            if(self.dataReceive != ""):
                friend = self.dataReceive.split("|")[0]
                action = self.dataReceive.split("|")[1]
                if(action == "hit" and friend == "server"):
                    #     print(self.dataReceive)
                    x = int(self.dataReceive.split("|")[2])
                    y = int(self.dataReceive.split("|")[3])
                    self.gui.handleButton(x, y)
                if(action == "Undo" and friend == "server"):
                    self.gui.Undo(False)
                if(action == "message" and friend == "server"):
                    message = self.dataReceive.split("|")[2]
                    self.gui.displayMessage("Friend: " + message)
            self.dataReceive = ""

    def serverAction(self):
        self.name = "server"
        HOST = socket.gethostbyname(socket.gethostname())  # Lấy địa chỉ
        print("Make host.........." + HOST)
        self.gui.notification("Gui IP chp ban", str(HOST))
        PORT = 8000  # Thiết lập port lắng nghe
        # cấu hình kết nối
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))  # lắng nghe
        s.listen(1)  # thiết lập tối ta 1 kết nối đồng thời
        self.conn, addr = s.accept()  # chấp nhận kết nối và trả về thông số
        t2 = threading.Thread(target=self.server, args=(addr, s))
        t2.start()

    def server(self, addr, s):
        try:
            # in ra thông địa chỉ của client
            print('Connected by', addr)
            while True:
                # Đọc nội dung client gửi đến
                self.dataReceive = self.conn.recv(1024).decode()
                if(self.dataReceive != ""):
                    friend = self.dataReceive.split("|")[0]
                    action = self.dataReceive.split("|")[1]
                    print(action)
                    if(action == "hit" and friend == "client"):
                        x = int(self.dataReceive.split("|")[2])
                        y = int(self.dataReceive.split("|")[3])
                        self.gui.handleButton(x, y)
                    if(action == "Undo" and friend == "client"):
                        self.gui.Undo(False)
                    if(action == "message" and friend == "client"):
                        message = self.dataReceive.split("|")[2]
                        self.gui.displayMessage("Friend: " + message)
                self.dataReceive = ""
        finally:
            s.close()  # đóng socket

    def sendData(self, data):
        # Gửi dữ liệu lên server`
        self.conn.sendall(str("{}|".format(self.name) + data).encode())

if __name__ == "__main__":
    Ox = 20  # Số lượng ô theo trục X
    Oy = 20 # Số lượng ô theo trục Y
    window = Window()
    window.showFrame()
    window.mainloop()
