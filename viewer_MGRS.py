#################
#   前提条件として以下のフォルダ構成であること
#   Direcroty
#    |-- viewer.py
#    |-- Data(directory)     camout.txt,plyファイル
#    |-- img(directory)      jpg
#
#from PyInstaller.utils.hooks import collect_dynamic_libs
# PyInstaller doesn't automatically include DLLs that pyproj depends on.
# We use a hook to tell PyInstaller about these DLLs.

#from pyproj import _network, network

import open3d as o3d
import numpy as np
import tkinter as tk
import glob
import math
import os
import utm2eqa
import calc_lat_lon

from PIL import Image, ImageTk,ImageOps

#import utm
from mgrs import MGRS

import configparser

print(o3d.__version__)

#ConfigParserオブジェクトを生成
config = configparser.ConfigParser()

#設定ファイル読み込み
config.read('set_exif.ini','utf-8')

class App:

    #画像の一覧表示
    def __init__(self, master, point, allpoints):

        #選択ポイント表示画面
        self.master = master
        
        #選択ポイント表示画面設定
        master.title("Select Point Images")
        self.num_cols = num_cols   #一覧表示のカラム数
        self.image_size = (280, 140) # 一覧表示する画像のサイズ
        self.image_size_org = (1600, 800) # 拡大表示する画像のサイズ


        #選択ポイント表示
    #    coordinate_label = tk.Label(master, text=f"Select Point: {point}")
    #    coordinate_label.pack()
    #    print("point=",point[0],point[1],point[2])
        #MGRS→緯度経度へ変換
#        mgrs_coord = "53SPU" + str(math.floor(float(point[0]))) + str(math.floor(float(point[1])))
#        mgrs_coord = "54SUE" + str(math.floor(float(point[0]))) + str(math.floor(float(point[1])))
        mgrs_coord = str(config['setting']['utm_zone']) + str(math.floor(float(point[0]))) + str(math.floor(float(point[1])))
        print("mgrs_coord:",mgrs_coord)

        lat,lon = utm2eqa.calculate_MGRS_suffix1(mgrs_coord)
#        lat,lon = self.calculate_MGRS_suffix1(mgrs_coord)
        print("latlon=",lat,lon)
        #緯度経度→平面直角座標
        #phi0_deg = 36.
        #lambda0_deg = 136

        #9系
#        phi0_deg = 36.
#        lambda0_deg = 139.5
        phi0_deg = float(config['setting']['phi0_deg'])
        lambda0_deg = float(config['setting']['lambda0_deg'])
        
        calc_x,calc_y = calc_lat_lon.calc_xy(lat,lon,phi0_deg,lambda0_deg)
#        calc_x,calc_y = calc_xy(lat,lon,phi0_deg,lambda0_deg)

        print("calc_x,calc_y=",calc_x,calc_y)

        #選択ポイント表示
        coordinate_label = tk.Label(master, text="select point:" + str(calc_x) + "," + str(calc_y) + "," + str(point[2]))
        coordinate_label.grid(row=0, column=0, sticky="nsew")
        coordinate_label.pack()
        #print("point=",calc_x,calc_y,point[2])


        #閉じるボタン
        self.close_button = tk.Button(master, text="Close", command=self.close_window)
        #self.close_button.place(x=800,y=600)
        self.close_button.pack(side = "bottom")
  

        # 画像を表示するためのキャンバスを作成
        self.canvas = tk.Canvas(master, width=1750, height=500)
        self.canvas.pack()        


        #2点間距離が短いものを抽出(引数:x,y,comout.txtのデータ,抽出件数)        
        near_Points = self.nearPoints(calc_x,calc_y,allpoints,10)

        #距離が近いもののファイル名、パスを配列へセット
        self.image_paths = []
        self.filename = []
        for i,point in enumerate(near_Points):
            x=point["x"]
            y=point["y"]
            id=point["id"]
            print("id,x,y=",id,x,y)
            self.image_paths.extend(glob.glob(my_dir + "\\img\\" + id + ".jpg"))
            self.filename.append( id + ".jpg")

        print(self.image_paths)



        self.images = []
        self.original_image_paths = []

        #一覧画像抽出
        self.load_images()

        # キャンバス上の画像にクリックイベントを追加
        self.canvas.bind("<Button-1>", self.show_image)
    
        #閉じるボタンを押されたら画面を閉じる
        master.protocol("WM_DELETE_WINDOW",self.close_window)
    
    def close_window(self):
        self.master.destroy()


    # 複数の座標のうち、距離が近い順にk個の座標を求める
    def nearPoints(self, x, y, points, k):
        if len(points) == 0:
            return []
        dist_points = []
        for point in points:
            distance = math.sqrt((point["x"] - x) ** 2 + (point["y"] - y) ** 2)
            dist_points.append((distance, point))
        #dist_points.sort()
        dist_points.sort(key=lambda x: x[0])
        return [point[1] for point in dist_points[:k]]


    #画像一覧読み込み
    def load_images(self):
        # 画像を読み込み、リストに追加
        for path in self.image_paths:
            #print("load_path=",path)
            img = Image.open(path)
            # 画像を縮小
            img = img.resize(self.image_size, resample=Image.LANCZOS)
            # 画像を回転
            #img = img.rotate(90)
            # 画像に余白を追加
            img = ImageOps.expand(img, border=20, fill='white')
            self.images.append(ImageTk.PhotoImage(img))
            self.original_image_paths.append(path)

        # 画像を表示
        for i, img in enumerate(self.images):
            x = 50 + (i % self.num_cols) * 321
            y = 50 + (i // self.num_cols) * 191
            #print("filename=",self.filename[i])
            self.create_image(x,y,img,self.filename[i])

    #一覧画像を表示
    def create_image(self, x, y, img, filename):
        #print("create_image")
        # 画像を表示
        self.canvas.create_image(x, y, image=img, anchor='nw')
        # ファイル名を表示
        self.canvas.create_text(x+self.image_size[0]//2, y+self.image_size[1]+30, text=filename)
    
    #クリックイベント（拡大画像を表示)
    def show_image(self, event):
        print("show_image")
        # クリックされた座標を取得
        x, y = event.x, event.y

        # クリックされた画像を特定
        for i, img in enumerate(self.images):
            img_width, img_height = img.width(), img.height()
            img_x, img_y = 50 + (i % self.num_cols) * 321, 50 + (i // self.num_cols) * 191
            if img_x <= x <= img_x + img_width and img_y <= y <= img_y + img_height:
                
                # クリックされた画像のインデックスを保存
                self.current_index = i
                
                # 元の画像を表示する新しいウィンドウを作成
                top = tk.Toplevel()
                top.title("Select Image")

                # 画像を表示するためのキャンバスを作成
                self.original_canvas = tk.Canvas(top, width=1600, height=900)
                self.original_canvas.pack()

                #ボタンを作成
                self.button_next = tk.Button(top,text="次の画像", command=self.next_images) 
                self.button_next.place(x=800,y=850)

                self.button_front = tk.Button(top,text="前の画像", command=self.front_images) 
                self.button_front.place(x=700,y=850)

                print(self.original_image_paths[i])
                #画像の取得
                original_img = Image.open(self.original_image_paths[i])
                #画像のサイズ変更
                original_img = original_img.resize(self.image_size_org, resample=Image.LANCZOS)

                # 画像を表示
                self.photo_image = ImageTk.PhotoImage(original_img)
                self.original_canvas.create_image(0, 0, image=self.photo_image, anchor='nw', tags=("image_tag",))

                break

    #前の画像ボタン押下処理
    def front_images(self):
        i = self.current_index - 1
        if i < 0:
            i = len(self.images) - 1
        self.current_index = i

        print("index", self.current_index)

        self.set_image(self.original_image_paths[i])

    #次の画像ボタン押下処理
    def next_images(self):
        i = self.current_index + 1
        if i > len(self.images) -1:
            i = 0
        self.current_index = i

        print("index", self.current_index)
        self.set_image(self.original_image_paths[i])

    #拡大画像を更新
    def set_image(self, img):
        #画像のサイズ変更
        new_img = Image.open(img)
        new_img = new_img.resize(self.image_size_org, resample=Image.LANCZOS)
        self.new_img_tk = ImageTk.PhotoImage(new_img)
        # キャンバス上の画像アイテムのタグを取得
        item_tag = self.original_canvas.find_withtag("image_tag")[0]
    
        print("item_tag=",item_tag)
        # 画像アイテムの画像を更新
        self.original_canvas.itemconfig(item_tag,image=self.new_img_tk)


#ポイント選択
def pick_points(pcd):
    print("Please pick points using [shift + left click]")

    picked_points = np.array([])
   
    vis = o3d.visualization.VisualizerWithEditing()
#    vis = o3d.visualization.Visualizer()
    
    vis.create_window(window_name='Viewer')

    vis.get_render_option().show_coordinate_frame = True
    vis.get_render_option().mesh_show_back_face = True
    vis.get_render_option().background_color = np.asarray([0, 0, 0])
    settings = vis.get_render_option().point_size  # 現在の点のサイズを取得
    vis.get_render_option().point_size = settings * 0.1  # 現在の点のサイズの半分に変更
    vis.get_render_option().light_on = False
    

    vis.add_geometry(pcd)

    print("pick_point run")
    
    vis.run()

    while True:
        vis.poll_events()
        vis.update_renderer()
        print("get_picked_points1")
        if vis.get_picked_points():

            picked_points = vis.get_picked_points()
            print("pick_point2", picked_points)

            


            #ポイント選択されていたら画像表示処理
            if len(picked_points) > 0:
                print("pick_point3 0over",len(picked_points))

                #座標リスト取得
                allpoints = readCoordinates(my_dir + "\\Data\\camout.txt")        

                point_id = picked_points[0]
                point = np.asarray(point_cloud.points[point_id])

                #ポイント表示画面作成
                create_info_window(point,allpoints)

                break

        else:
            break    

    print("pick_point destroy_window")
    vis.destroy_window()
    
    print("pick_point_return")

    if len(picked_points) == 0:
        return 1
    else:
        return 0 


#選択ポイント表示window作成
def create_info_window(point,allpoints):

    print("create_info_window(point)=",point)
    root = tk.Tk()
    root.title("Image Viewer")

    app = App(root,point,allpoints)
    root.mainloop()

# txtファイルから座標リストを作成する関数
def readCoordinates(filename):
    print("readCoordinates")
    coordinates = []
    cnt = 0
    with open(filename, 'r') as file:
        for line in file:
            if cnt >= 2:
                # 行をタブで分割する
                values = line.strip().split('\t')
                # 座標の値を浮動小数点数に変換してリストに追加する
                coordinates.append({"x": float(values[1]), "y": float(values[2]), "id": str(values[0])})
            cnt = cnt + 1 
    return coordinates


if __name__ == "__main__":

#    args = sys.argv
#    print(args)



    #一覧表示用
    num_cols = 5

    #このファイルのディレクトリ取得
    my_dir = os.getcwd()
    filename = glob.glob(my_dir+"\\Data\\*.ply") 

    print("filename=",filename)

    #表示する3D画像
#    point_cloud = o3d.io.read_point_cloud(my_dir + "\\Data\\sample.ply")
    point_cloud = o3d.io.read_point_cloud(filename[0])

    #ポイント選択
#    print("picked_points")
    while True:

        rtn = pick_points(point_cloud)
        if rtn == 1:
            break

    print("picked_points_end")



