# from __future__ import division
# import os
# import re
# import json
# import string
# import platform
# import webbrowser
#
# import tkinter as tk
# import tkinter.filedialog
#
# from PIL import ImageTk, Image, ExifTags
# from pyparsing import basestring
#
# OS_TYPE = platform.system()
#
#
# # TODO: [x] switch from label to canvas
# #       [x] make canvas scrollable
# #       [x] make a separate function for panel setup
# #       [x] hide scrollbar when canvas fits page
# #       [x] disable zoom in/zoom out buttons when cannot zoom (in/out) more
# #       [x] switch from thumbnail to resize on zoom > 100%
# #       [x] zoom on mouse wheel
# #       [x] add scrolling on scrollbar
# #       [ ] disable scrolling on empty canvas
#
#
# def donothing():
#     # a dummy callback placeholder
#     filewin = tk.Toplevel()
#     button = tk.Button(filewin, text="Do nothing button")
#     button.pack()
#
#
# def convert_to_degrees(value):
#     dd, mm, ss = map(lambda x: x[0] / float(x[1]), value)
#     return dd + (mm / 60.0) + (ss / 3600.0)
#
#
# def get_lat_lon(info):
#     try:
#         gps_info = info["GPSInfo"]
#         gps_latitude_ref = gps_info[1]
#         gps_latitude = gps_info[2]
#         gps_longitude_ref = gps_info[3]
#         gps_longitude = gps_info[4]
#
#         lat = convert_to_degrees(gps_latitude)
#         if gps_latitude_ref != "N":
#             lat = -lat
#
#         lon = convert_to_degrees(gps_longitude)
#         if gps_longitude_ref != "E":
#             lon = -lon
#
#         return lat, lon
#
#     except KeyError:
#         return None, None
#
#
# def get_exif_info(img):
#     if hasattr(img, '_getexif') and img._getexif() is not None:
#         raw_exif = {
#             ExifTags.TAGS[k]: v
#             for k, v in img._getexif().items()
#             if k in ExifTags.TAGS
#         }
#     else:
#         raw_exif = {}
#
#     return normalize(raw_exif)
#
#
# def has_lat_lon(img):
#     exif = get_exif_info(img)
#     lat, lon = get_lat_lon(exif)
#     return lat != None and lon != None
#
#
# def normalize(data):
#     if isinstance(data, dict):
#         norm = {key: normalize(val) for key, val in data.items()}
#         return {key: val for key, val in norm.items() if val is not None}
#     elif isinstance(data, list):
#         norm = [normalize(item) for item in data]
#         return [item for item in norm if item is not None]
#     else:
#         if isinstance(data, basestring):
#             try:
#                 data = str(data.replace('\x00', ''))
#             except UnicodeEncodeError:
#                 return None
#             if all(c in string.printable for c in data):
#                 return data
#             else:
#                 return None
#         return data
#
#
# def preformat(data, level=0, indent=2, sortkeys=True):
#     if isinstance(data, dict):
#         keys = data.keys()
#         if sortkeys:
#             keys.sort()
#         return "\n".join("{0}{1}:{2}{3}".format(" " * (indent * level), key,
#                                                 '\n' if isinstance(data[key], dict) else ' ',
#                                                 preformat(data[key], level + 1, indent, sortkeys)) for key in keys)
#     elif isinstance(data, list):
#         return "[" + ", ".join(preformat(item, level + 1, indent, sortkeys) for item in data) + "]"
#     else:
#         return str(data)
#
#
# class AutoScrollbar(tk.Scrollbar):
#     # a scrollbar that hides itself if it's not needed.  only
#     # works if you use the grid geometry manager.
#     def set(self, lo, hi):
#         threshold = 0.04
#         if float(lo) <= threshold and float(hi) >= 1 - threshold:
#             # grid_remove is currently missing from Tkinter!
#             self.grid_remove()  # tk.call("grid", "remove", self)
#         else:
#             self.grid()
#         tk.Scrollbar.set(self, lo, hi)
#
#     def pack(self, **kw):
#         raise (tk.TclError, "cannot use pack with this widget")
#
#     def place(self, **kw):
#         raise (tk.TclError, "cannot use place with this widget")
#
#
# class App(object):
#
#     def __init__(self):
#
#         self.bg_color = "#F2F4F3"
#         self.fg_color = "#A9BCD0"
#
#         # start GUI initialization part
#         self.window = tk.Tk()
#         # a placeholder image shown on startup
#         self.current_img = Image.new("RGB", (600, 400), "black")
#         self.zoom_level = 1.0
#
#         # a size of the panel scrollregion (4-tuple)
#         self.viewbox = tk.Variable()
#         self.viewbox.trace("w", self.update_scrollregion)
#         self.viewbox.trace("w", self.update_zoom_buttons)
#
#         # a path to the currently loaded image
#         self.current_image = tk.StringVar()
#         self.current_image.trace("w", self.update_title)
#         self.current_image.trace("w", self.update_toolbal)
#         self.current_image.trace("w", self.enable_canvas_zoom)
#
#         # status bar message
#         self.status = tk.StringVar()
#         self.status.set("Ready.")
#
#         self.setup_menu_bar()
#         self.setup_main_window()
#
#     def setup_main_window(self):
#
#         self.window.title('App Title')  # TODO: CHANGE ME
#         self.window.geometry('800x500')
#         self.window.config(background=self.bg_color)
#         # fonts for all widgets
#         self.window.option_add("*Font", "Sans 10")
#         # on resize event
#         self.window.bind("<Configure>", self.display_image)
#         # status bar label (bottom stick)
#         tk.Label(self.window, anchor=tk.W, textvariable=self.status,
#                  bg=self.bg_color).pack(fill=tk.X, side=tk.BOTTOM)
#         # buttons panel
#         self.setup_toolbar()
#         # canvas with the image displayed
#         self.setup_panel()
#
#         self.viewbox.set(self.canvas_viewbox)
#         self.disable_toolbar()
#
#     def setup_menu_bar(self):
#
#         menubar = tk.Menu(self.window, bg=self.bg_color,
#                           activebackground=self.fg_color, relief=tk.FLAT)
#         #    -------- File Menu --------
#         filemenu = tk.Menu(menubar, tearoff=0, bg=self.bg_color,
#                            activebackground=self.fg_color, relief=tk.FLAT)
#         filemenu.add_command(label="Open", command=self.select_file)
#         filemenu.add_command(label="Save", command=donothing)
#         filemenu.add_command(label="Export EXIF Info", command=self.export_exif)
#         filemenu.add_command(label="Close", command=donothing)
#         filemenu.add_separator()
#         filemenu.add_command(label="Exit", command=self.window.quit)
#         menubar.add_cascade(label="File", menu=filemenu)
#         #    -------- View Menu --------
#         viewmenu = tk.Menu(menubar, tearoff=0, bg=self.bg_color,
#                            activebackground=self.fg_color, relief=tk.FLAT)
#         viewmenu.add_command(label="Show Map", command=self.open_browser)
#         viewmenu.add_command(label="Zoom In", command=self.zoom_in)
#         viewmenu.add_command(label="Zoom Out", command=self.zoom_out)
#         viewmenu.add_command(label="Reset Zoom", command=self.reset_zoom)
#         menubar.add_cascade(label="View", menu=viewmenu)
#         #    -------- Help Menu --------
#         helpmenu = tk.Menu(menubar, tearoff=0, bg=self.bg_color,
#                            activebackground=self.fg_color, relief=tk.FLAT)
#         helpmenu.add_command(label="About", command=donothing)
#         helpmenu.add_command(label="Help", command=donothing)
#         menubar.add_cascade(label="Help", menu=helpmenu)
#
#         self.window.config(menu=menubar)
#
#     def setup_toolbar(self):
#
#         self.toolbar_frame = tk.Frame(self.window, bg=self.bg_color)
#         self.toolbar_frame.pack(side=tk.BOTTOM, fill=None, expand=False)
#
#         upper_frame = tk.Frame(self.toolbar_frame, bg=self.bg_color)
#         upper_frame.pack(side=tk.TOP, pady=(20, 5))
#
#         lower_frame = tk.Frame(self.toolbar_frame, bg=self.bg_color)
#         lower_frame.pack(side=tk.BOTTOM, pady=(5, 20))
#
#         commands = [self.load_prev_image,
#                     self.zoom_out,
#                     self.reset_zoom,
#                     self.zoom_in,
#                     self.load_next_image,
#                     self.open_browser]
#         names = ['Previous Image', 'Zoom Out', 'Reset Zoom', 'Zoom In', 'Next Image', 'Show Map']
#
#         for name, command in zip(names, commands):
#             frame = upper_frame if name != 'Show Map' else lower_frame
#             btn = tk.Button(frame, text=name, bg=self.bg_color, width=12,
#                             activebackground=self.fg_color, command=command)
#             if name != 'Show Map':
#                 btn.pack(side=tk.LEFT, padx=5)
#             else:
#                 btn.pack(side=tk.BOTTOM)
#             # add button to self namespace
#             btn_name = name.lower().replace(' ', '_') + '_btn'
#             setattr(self, btn_name, btn)
#
#     def configure_toolbal(self, state):
#         for frame in self.toolbar_frame.winfo_children():
#             for child in frame.winfo_children():
#                 child.configure(state=state)
#
#     def disable_toolbar(self):
#         self.configure_toolbal('disable')
#
#     def enable_toolbar(self):
#         self.configure_toolbal('normal')
#
#     def disable_canvas_zoom(self, *args):
#         for action in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
#             self.canvas.unbind(action)
#
#     def enable_canvas_zoom(self, *args):
#         for action in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
#             self.canvas.bind(action, self.on_mouse_zoom)
#
#     def setup_panel(self):
#
#         frame = tk.Frame(self.window, bg=self.bg_color)
#         frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
#
#         self.canvas = tk.Canvas(frame, bg=self.bg_color)
#
#         hbar = AutoScrollbar(frame, orient=tk.HORIZONTAL)
#         hbar.grid(row=1, column=0, sticky=tk.E + tk.W)
#         hbar.config(command=self.canvas.xview)
#
#         vbar = AutoScrollbar(frame, orient=tk.VERTICAL)
#         vbar.grid(row=0, column=1, sticky=tk.N + tk.S)
#         vbar.config(command=self.canvas.yview)
#
#         self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
#         self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
#
#         frame.grid_rowconfigure(0, weight=1)
#         frame.grid_columnconfigure(0, weight=1)
#
#         #              with Windows OS        with Linux OS
#         for action in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
#             hbar.bind(action, self.on_mouse_xscroll)
#             vbar.bind(action, self.on_mouse_yscroll)
#
#     @property
#     def canvas_shape(self):
#         return self.canvas.winfo_width(), self.canvas.winfo_height()
#
#     @property
#     def image_shape(self):
#         return self.current_img.size
#
#     @property
#     def viewbox_shape(self):
#         vb = self.viewbox.get()
#         return vb[2], vb[3]
#
#     def _shape_to_viewbox(self, shape):
#         return (0, 0, shape[0], shape[1])
#
#     @property
#     def image_viewbox(self):
#         return self._shape_to_viewbox(self.image_shape)
#
#     @property
#     def canvas_viewbox(self):
#         return self._shape_to_viewbox(self.canvas_shape)
#
#     def _shape_to_aspect(self, shape):
#         return shape[0] / shape[1]
#
#     @property
#     def image_aspect(self):
#         return self._shape_to_aspect(self.image_shape)
#
#     @property
#     def canvas_aspect(self):
#         return self._shape_to_aspect(self.canvas_shape)
#
#     @property
#     def viewbox_aspect(self):
#         return self._shape_to_aspect(self.viewbox_shape)
#
#     def _shape_to_center(self, shape):
#         return shape[0] / 2, shape[1] / 2
#
#     @property
#     def image_center(self):
#         return self._shape_to_center(self.image_shape)
#
#     @property
#     def canvas_center(self):
#         return self._shape_to_center(self.canvas_shape)
#
#     @property
#     def viewbox_center(self):
#         return self._shape_to_center(self.viewbox_shape)
#
#     @property
#     def max_viewbox_shape(self):
#         max_zoom = 2  # 200%
#         return max_zoom * self.image_shape[0], max_zoom * self.image_shape[1]
#
#     @property
#     def min_viewbox_shape(self):
#         min_zoom = 0.5  # 50%
#         return int(min_zoom * self.canvas_shape[0]), int(min_zoom * self.canvas_shape[1])
#
#     def update_title(self, *args):
#         self.window.title(os.path.basename(self.current_image.get()))
#
#     def update_toolbal(self, *args):
#         self.enable_toolbar()
#         if not has_lat_lon(self.current_img):
#             self.show_map_btn.configure(state='disable')
#
#     def update_scrollregion(self, *args):
#         self.canvas.config(scrollregion=self.viewbox.get())
#
#     def update_zoom_buttons(self, *args):
#         if self.viewbox_shape == self.min_viewbox_shape:
#             self.zoom_out_btn.configure(state='disable')
#         else:
#             self.zoom_out_btn.configure(state='normal')
#         if self.viewbox_shape == self.max_viewbox_shape:
#             self.zoom_in_btn.configure(state='disable')
#         else:
#             self.zoom_in_btn.configure(state='normal')
#
#     def select_file(self):
#         options = {
#             'filetypes': [("JPEG Image", "*.jpeg *.JPEG *.jpg *.JPG"), ("All Files", "*.*")],
#             'title': "Choose an image"
#         }
#
#         filename = tk.filedialog.askopenfilename(**options)
#         if not filename:  # early exit on Cancel
#             return
#
#         try:
#             self.load_image(filename)
#             self.status.set('Ready.')
#         except IOError:
#             self.status.set('Not an image file.')
#
#     def load_image(self, filename):
#         self.current_img = Image.open(filename)
#         self.current_image.set(filename)
#         self.reset_zoom()
#
#     def display_image(self, event=None):
#
#         if not self.current_image.get():
#             return
#
#         if self.viewbox_shape[0] < self.image_shape[0]:
#             copy = self.current_img.copy()  # thumbnail method works in-place, so make a copy first
#             copy.thumbnail(self.viewbox_shape, Image.NEAREST)  # Image.ANTIALIAS
#         else:
#             copy = self.current_img.resize(self.viewbox_shape)
#
#         image = ImageTk.PhotoImage(copy)
#         # allows to center the image on zoom < 100%
#         cx = max(self.viewbox_center[0], self.canvas_center[0])
#         cy = max(self.viewbox_center[1], self.canvas_center[1])
#         self.canvas.create_image(cx, cy, image=image, anchor=tk.CENTER)
#         self.canvas.image = image
#
#     def valid_image(self, filename):
#         supported_formats = ['.jpg', '.jpeg', '.png']
#         fname, ext = os.path.splitext(filename)
#         return ext.lower() in supported_formats
#
#     def _get_image_at_offset(self, current_image, offset):
#         dirname, filename = os.path.split(current_image)
#         image_files = sorted(filter(self.valid_image, os.listdir(dirname)))
#         file_index = (image_files.index(filename) + offset) % len(image_files)
#         return os.path.join(dirname, image_files[file_index])
#
#     def get_next_image(self, current_image):
#         return self._get_image_at_offset(current_image, 1)
#
#     def get_prev_image(self, current_image):
#         return self._get_image_at_offset(current_image, -1)
#
#     def load_next_image(self):
#         current = self.current_image.get()
#         self.load_image(self.get_next_image(current))
#
#     def load_prev_image(self):
#         current = self.current_image.get()
#         self.load_image(self.get_prev_image(current))
#
#     def reset_zoom(self):
#         # two calls are needed because canvas
#         # size is recalculated on the reset from
#         # zoomed-in image because scrollbars become
#         # hidden and canvas size increases a little
#         self.viewbox.set(self.canvas_viewbox)
#         self.canvas.update_idletasks()
#         self.viewbox.set(self.canvas_viewbox)
#         self.display_image()
#
#     def zoom_image(self, zoom_center=None, zoom_factor=1):
#         if zoom_center is None:
#             zoom_center = self.canvas_center
#         vb = self.viewbox.get()
#         right = min(vb[2] * zoom_factor, self.image_aspect * vb[3] * zoom_factor, self.max_viewbox_shape[0])
#         bottom = min(vb[3] * zoom_factor, vb[2] * zoom_factor / self.image_aspect, self.max_viewbox_shape[1])
#         right, bottom = max(right, self.min_viewbox_shape[0]), max(bottom, self.min_viewbox_shape[1])
#         self.viewbox.set((vb[0], vb[1], int(right), int(bottom)))
#         self.display_image()
#
#     def zoom_in(self, zoom_center=None, zoom_factor=1.25):
#         return self.zoom_image(zoom_center, zoom_factor)
#
#     def zoom_out(self, zoom_center=None, zoom_factor=0.75):
#         return self.zoom_image(zoom_center, zoom_factor)
#
#     def _scroll_direction(self, event):
#         # http://code.activestate.com/recipes/578894-mousewheel-binding-to-scrolling-area-tkinter-multi/
#         if OS_TYPE == 'Linux':
#             scroll_dir = 1 if event.num == 4 else -1
#         elif OS_TYPE == 'Windows':
#             scroll_dir = 1 if event.delta > 0 else -1
#         else:
#             scroll_dir = 1 if event.delta > 0 else -1
#         return scroll_dir
#
#     def on_mouse_zoom(self, event):
#         if self._scroll_direction(event) > 0:
#             self.zoom_in((event.x, event.y), zoom_factor=1.1)
#         else:
#             self.zoom_out((event.x, event.y), zoom_factor=0.9)
#
#     def on_mouse_xscroll(self, event):
#         self.canvas.xview_scroll(self._scroll_direction(event), "units")
#
#     def on_mouse_yscroll(self, event):
#         self.canvas.yview_scroll(self._scroll_direction(event), "units")
#
#     def open_browser(self):
#         exif = get_exif_info(self.current_img)
#         lat, lon = get_lat_lon(exif)
#         if lat != None and lon != None:
#             url = "http://google.com/maps/?q={0:.7f},{1:.7f}".format(lat, lon)
#             webbrowser.open(url)
#             self.status.set('Opening a web browser page ...')
#             self.window.after(3000, lambda: self.status.set('Ready'))
#         else:
#             self.status.set('No GPS Info found.')
#
#     def export_exif(self):
#         dirname, filename = os.path.split(self.current_image.get())
#
#         options = {'defaultextension': '.txt',
#                    'filetypes': [('all files', '.*'), ('text files', '.txt')],
#                    'initialdir': dirname,
#                    'initialfile': filename.rsplit('.', 1)[0] + "_exif.txt",
#                    'title': 'Export Exif Info',
#                    }
#
#         output_filename = tk.filedialog.asksaveasfilename(**options)
#         if not output_filename:
#             return
#
#         exif = get_exif_info(self.current_img)
#         if exif:
#             with open(output_filename, 'w') as fp:
#                 fp.write(preformat(exif))
#             self.status.set('Exported EXIF Info.')
#         else:
#             self.status.set('No EXIF tags found.')
#
#     def run(self):
#         self.window.mainloop()
#
#
# if __name__ == '__main__':
#     app = App()
#     app.run()
#
# class Army:
#     def train_swordsman(self, name):
#         raise NotImplementedError()
#
#     def train_lancer(self, name):
#         raise NotImplementedError()
#
#     def train_archer(self, name):
#         raise NotImplementedError()
#
#
# class Sword:
#     def __init__(self, name):
#         self._name = name
#
#     def introduce(self):
#         return self._name
#
#
# class Lancer:
#     def __init__(self, name):
#         self._name = name
#
#     def introduce(self):
#         return self._name
#
#
# class Archer:
#     def __init__(self, name):
#         self._name = name
#
#     def introduce(self):
#         return self._name
#
#
# class AsianArmy(Army):
#     def train_swordsman(self, name):
#         return Sword(f'''Samurai {name}, Asian swordsman''')
#
#     def train_lancer(self, name):
#         s = Lancer('lancer')
#         return Lancer(f'''Ronin {name}, Asian lancer''')
#
#     def train_archer(self, name):
#         return Archer(f'''Shinobi {name}, Asian archer''')
#
#
# class EuropeanArmy(Army):
#     def train_swordsman(self, name):
#         return Sword(f'''Knight {name}, European swordsman''')
#
#     def train_lancer(self, name):
#         return Lancer(f'''Raubritter {name}, European lancer''')
#
#     def train_archer(self, name):
#         return Archer(f'''Ranger {name}, European archer''')
#
#
# if __name__ == '__main__':
#     # These "asserts" using only for self-checking and not necessary for auto-testing
#
#     my_army = EuropeanArmy()
#     enemy_army = AsianArmy()
#
#     soldier_1 = my_army.train_swordsman("Jaks")
#     soldier_2 = my_army.train_lancer("Harold")
#     soldier_3 = my_army.train_archer("Robin")
#
#     soldier_4 = enemy_army.train_swordsman("Kishimoto")
#     soldier_5 = enemy_army.train_lancer("Ayabusa")
#     soldier_6 = enemy_army.train_archer("Kirigae")
#
#     print(soldier_1.introduce())
#     assert soldier_1.introduce() == "Knight Jaks, European swordsman"
#     assert soldier_2.introduce() == "Raubritter Harold, European lancer"
#     assert soldier_3.introduce() == "Ranger Robin, European archer"
#
#     assert soldier_4.introduce() == "Samurai Kishimoto, Asian swordsman"
#     assert soldier_5.introduce() == "Ronin Ayabusa, Asian lancer"
#     assert soldier_6.introduce() == "Shinobi Kirigae, Asian archer"
#
#     print("Coding complete? Let's try tests!")

class Friend:
    def __init__(self, name):
        self.name = name
        self.invites = ''
        self.pname = ''

    def show_invite(self):
        if len(self.invites) != 0:
            return f"{self.pname}: {self.invites}"
        else:
            return 'No party...'


class Party:
    def __init__(self, party):
        self.list = set()
        self.party = party

    def add_friend(self, name):
        if not isinstance(name, Friend):
            raise TypeError
        self.list.add(name)

    def del_friend(self, name):
        self.list.remove(name)

    def send_invites(self, time):
        for f in self.list:
            f.invites = time
            f.pname = self.party


if __name__ == '__main__':
    # These "asserts" using only for self-checking and not necessary for auto-testing

    party = Party("Midnight Pub")
    nick = Friend("Nick")
    john = Friend("John")
    lucy = Friend("Lucy")
    chuck = Friend("Chuck")

    party.add_friend(nick)
    party.add_friend(john)
    party.add_friend(lucy)
    party.send_invites("Friday, 9:00 PM")
    party.del_friend(nick)
    party.send_invites("Saturday, 10:00 AM")
    party.add_friend(chuck)
    print(chuck.show_invite())
    assert john.show_invite() == "Midnight Pub: Saturday, 10:00 AM"
    assert lucy.show_invite() == "Midnight Pub: Saturday, 10:00 AM"
    assert nick.show_invite() == "Midnight Pub: Friday, 9:00 PM"
    assert chuck.show_invite() == "No party..."
    print("Coding complete? Let's try tests!")
