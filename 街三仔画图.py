import tkinter as tk
from tkinter import *
import tkinter.simpledialog
import tkinter.colorchooser
import tkinter.filedialog
from PIL import Image, ImageTk, ImageGrab
from tkinter.colorchooser import askcolor
from win32 import win32api, win32gui, win32print
from win32.lib import win32con

from win32.win32api import GetSystemMetrics


class Draw_designs(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack()

        self.temp = []  # 保存图形的类型
        self.li = []    # 保存所画图形的坐标
        self.fill_color = None # 保存填充的颜色

        self.lastDraw = 0
        self.end = [0]
        self.size = "12"    # 字体大小

        self.yesno = 0
        self.function = 1   # 默认铅笔
        self.X = 0
        self.Y = 0

        self.foreColor = '#000000'
        self.backColor = '#FFFFFF'

        self.create_widget()
        self.setMenu()

    def create_widget(self):
        self.image = PhotoImage()
        self.canvas = Canvas(root, bg='white', width=x, height=y)   # 创建画布
        self.canvas.create_image(x, y, image=self.image)

        self.canvas.bind('<Button-1>', self.onLeftButtonDown)
        self.canvas.bind('<B1-Motion>', self.onLeftButtonMove)
        self.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)
        self.canvas.bind('<ButtonRelease-3>', self.onRightButtonUp)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

    def setMenu(self):
        '''主菜单及其关联的函数'''
        self.menu = tk.Menu(self, bg="red")
        root.config(menu=self.menu)
        self.menu.add_command(label='导入', command=self.Import)
        self.menu.add_command(label='保存', command=self.SavePicture)
        self.menu.add_command(label='清屏', command=self.Clear)
        self.menu.add_command(label='撤销', command=self.Back)

        '''子菜单及其关联的函数'''
        self.menuType = tk.Menu(self.menu, tearoff=0)   # tearoff=0 - 表示无法将下拉菜单从“工具栏”窗口分离
        self.menu.add_cascade(label='工具栏', menu=self.menuType)  # add_cascade建立菜单类别对象
        # 在"工具栏"内建立菜单列表
        self.menuType.add_command(label='铅笔', command=self.drawCurve)
        self.menuType.add_command(label='直线', command=self.drawLine)
        self.menuType.add_command(label='矩形', command=self.drawRectangle)
        self.menuType.add_command(label='圆形', command=self.drawCircle)
        self.menuType.add_command(label='文本', command=self.drawText)
        self.menuType.add_command(label='橡皮擦', command=self.onErase)
        self.menuType.add_command(label='颜色填充', command=self.fill)
        self.menuType.add_separator()       # 建立分隔线
        self.menuType.add_command(label='选择前景色', command=self.chooseForeColor)
        self.menuType.add_command(label='选择背景色', command=self.chooseBackColor)

    def Import(self):     # 导入文件
        filename = tk.filedialog.askopenfilename(title='导入图片', filetypes=[('image', '*.jpg *.png *.gif')])
        if filename:
            self.image = Image.open(filename)
            self.image = self.image.resize((800, 600), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(400, 300, image=self.image)

    def SavePicture(self):      # 保存画布
        ScreenShot()

    def Clear(self):    # 清屏
        for item in self.canvas.find_all():
            self.canvas.delete(item)
        # 清屏后对数据进行初始化
        self.end = [0]
        self.lastDraw = 0

    def Back(self):     # 撤回
        try:
            for i in range(self.end[-2], self.end[-1] + 1):
                self.canvas.delete(i)
            self.end.pop()
            self.li.pop()

        except:
            self.end = [0]

    def onLeftButtonDown(self, event):  # 点击鼠标左键后运行此函数
        self.yesno = 1
        self.X = event.x
        self.Y = event.y

        if self.function == 7:  # 颜色填充
            for i in range(len(self.li)):
                if (self.X >= self.li[i][0] and self.X <= self.li[i][2]) and (self.Y >= self.li[i][1] and self.Y <= self.li[i][3]):
                    if self.temp[i] == 'rect':
                        rect = self.canvas.create_rectangle(self.li[i][0], self.li[i][1], self.li[i][2], self.li[i][3])
                        self.canvas.itemconfig(rect, fill=self.fill_color)
                        self.end.append(rect)   # 加入撤销列表

                    elif self.temp[i] == 'oval':
                        oval = self.canvas.create_oval(self.li[i][0], self.li[i][1], self.li[i][2], self.li[i][3])
                        self.canvas.itemconfig(oval, fill=self.fill_color)
                        self.end.append(oval)  # 加入撤销列表

                    break

        if self.function == 4:
            self.canvas.create_text(event.x, event.y, font=("等线", int(self.size)), text=self.text, fill=self.foreColor)
            self.function = 1

    def onLeftButtonMove(self, event):  # 按下鼠标左键并移动后运行此函数
        if self.yesno == 0:
            return

        if self.function == 1:    # 铅笔
            self.lastDraw = self.canvas.create_line(self.X, self.Y, event.x, event.y, fill=self.foreColor)
            self.X = event.x
            self.Y = event.y

        elif self.function == 2:  # 画直线
            try:
                self.canvas.delete(self.lastDraw)
            except Exception:
                pass
            self.lastDraw = self.canvas.create_line(self.X, self.Y, event.x, event.y, fill=self.foreColor)

        elif self.function == 3:  # 画矩形
            try:
                self.canvas.delete(self.lastDraw)
            except Exception:
                pass
            self.lastDraw = self.canvas.create_rectangle(self.X, self.Y, event.x, event.y, outline=self.foreColor)

        elif self.function == 5:  # 橡皮擦
            self.lastDraw = self.canvas.create_rectangle(event.x - 10, event.y - 10, event.x + 10, event.y + 10, outline=self.backColor)

        elif self.function == 6:  # 画圆
            try:
                self.canvas.delete(self.lastDraw)
            except Exception:
                pass
            self.lastDraw = self.canvas.create_oval(self.X, self.Y, event.x, event.y, fill=self.backColor, outline=self.foreColor)

    def onLeftButtonUp(self, event):    # 左键鼠标释放后运行此函数
        if self.function == 2:
            self.lastDraw = self.canvas.create_line(self.X, self.Y, event.x, event.y, fill=self.foreColor)

        elif self.function == 3:    # 正方形
            self.lastDraw = self.canvas.create_rectangle(self.X, self.Y, event.x, event.y, outline=self.foreColor)
            self.li.append((self.X, self.Y, event.x, event.y))  # 保存图型的坐标
            self.temp.append('rect')

        elif self.function == 6:    # 圆形
            self.lastDraw = self.canvas.create_oval(self.X, self.Y, event.x, event.y, outline=self.foreColor)
            self.li.append((self.X, self.Y, event.x, event.y))  # 保存图型的坐标
            self.temp.append('oval')

        self.yesno = 0
        if self.function != 7:
            self.end.append(self.lastDraw)

    def onRightButtonUp(self, event):   # 在画布中鼠标右键按下并松开时，弹出菜单
        self.menu.post(event.x_root, event.y_root)

    def drawCurve(self):    # 铅笔
        self.function = 1

    def drawLine(self):     # 直线
        self.function = 2

    def drawRectangle(self):    # 矩形
        self.function = 3

    def drawCircle(self):   # 画圆
        self.function = 6

    def drawText(self):     # 文字
        self.text = tk.simpledialog.askstring(title='输入文本', prompt='')
        if self.text is not None:
            self.size = tk.simpledialog.askinteger('输入字号', prompt='', initialvalue=20)
            if self.size is None:
                self.size = "20"
        self.function = 4

    def onErase(self):  # 橡皮擦
        self.function = 5

    def fill(self):
        c = askcolor(color=self.foreColor, title="选择画笔颜色")
        self.fill_color = c[1]
        self.function = 7

    def chooseForeColor(self):  # 设置前景色
        self.foreColor = tk.colorchooser.askcolor()[1]

    def chooseBackColor(self):  # 设置背景色
        self.backColor = tk.colorchooser.askcolor()[1]

"""
------------- 截图 -----------------
"""
def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h


def get_screen_size():
    """获取缩放后的分辨率"""
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h


real_resolution = get_real_resolution()
screen_size = get_screen_size()

# Windows 设置的屏幕缩放率
# ImageGrab 的参数是基于显示分辨率的坐标，而 tkinter 获取到的是基于缩放后的分辨率的坐标
screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)


class Box:

    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

    def isNone(self):
        return self.start_x is None or self.end_x is None

    def setStart(self, x, y):
        self.start_x = x
        self.start_y = y

    def setEnd(self, x, y):
        self.end_x = x
        self.end_y = y

    def box(self):
        lt_x = min(self.start_x, self.end_x)
        lt_y = min(self.start_y, self.end_y)
        rb_x = max(self.start_x, self.end_x)
        rb_y = max(self.start_y, self.end_y)
        return lt_x, lt_y, rb_x, rb_y

    def center(self):
        center_x = (self.start_x + self.end_x) / 2
        center_y = (self.start_y + self.end_y) / 2
        return center_x, center_y


class SelectionArea:

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.area_box = Box()

    def empty(self):
        return self.area_box.isNone()

    def setStartPoint(self, x, y):
        self.canvas.delete('area', 'lt_txt', 'rb_txt')
        self.area_box.setStart(x, y)
        # 开始坐标文字
        self.canvas.create_text(
            x, y - 10, text=f'({x}, {y})', fill='red', tag='lt_txt')

    def updateEndPoint(self, x, y):
        self.area_box.setEnd(x, y)
        self.canvas.delete('area', 'rb_txt')
        box_area = self.area_box.box()
        # 选择区域
        self.canvas.create_rectangle(
            *box_area, fill='black', outline='red', width=2, tags="area")
        self.canvas.create_text(
            x, y + 10, text=f'({x}, {y})', fill='red', tag='rb_txt')


class ScreenShot():

    def __init__(self, scaling_factor=2):
        self.win = tk.Tk()
        # self.win.tk.call('tk', 'scaling', scaling_factor)
        self.width = self.win.winfo_screenwidth()
        self.height = self.win.winfo_screenheight()

        # 无边框，没有最小化最大化关闭这几个按钮，也无法拖动这个窗体，程序的窗体在Windows系统任务栏上也消失
        self.win.overrideredirect(True)
        self.win.attributes('-alpha', 0.25)

        self.is_selecting = False

        # 绑定按 Enter 确认, Esc 退出
        self.win.bind('<KeyPress-Escape>', self.exit)
        self.win.bind('<KeyPress-Return>', self.confirmScreenShot)
        self.win.bind('<Button-1>', self.selectStart)
        self.win.bind('<ButtonRelease-1>', self.selectDone)
        self.win.bind('<Motion>', self.changeSelectionArea)

        self.canvas = tk.Canvas(self.win, width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.area = SelectionArea(self.canvas)
        self.win.mainloop()

    def exit(self, event):
        self.win.destroy()

    def clear(self):
        self.canvas.delete('area', 'lt_txt', 'rb_txt')
        self.win.attributes('-alpha', 0)

    def captureImage(self):
        if self.area.empty():
            return None
        else:
            filename = tk.filedialog.asksaveasfilename(filetypes=[('.jpg', 'JPG')],
                                                       initialdir='C:\\Users\\lin042\\Desktop\\')
            box_area = [x * screen_scale_rate for x in self.area.area_box.box()]
            self.clear()
            img = ImageGrab.grab(box_area).save(filename)
            return img

    def confirmScreenShot(self, event):
        img = self.captureImage()
        if img is not None:
            img.show()
        self.win.destroy()

    def selectStart(self, event):
        self.is_selecting = True
        self.area.setStartPoint(event.x, event.y)
        # print('Select', event)

    def changeSelectionArea(self, event):
        if self.is_selecting:
            self.area.updateEndPoint(event.x, event.y)
            # print(event)

    def selectDone(self, event):
        self.is_selecting = False

if __name__ == '__main__':
    x = 1200    # 宽
    y = 600     # 高
    root = tk.Tk()
    root.title('街三仔画图')   # 软件名
    root.geometry('1200x600')    # 设置软件大小 - 宽x高
    Draw_designs(root)
    root.mainloop()
