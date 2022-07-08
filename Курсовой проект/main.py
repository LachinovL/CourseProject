from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3
import matplotlib.pyplot as plt
from kivymd.uix.list import OneLineListItem


class Diet(MDApp):
    title = 'Помощник диетолога'
    conn = sqlite3.connect('diet.db')
    sql = conn.cursor()
    def build(self):
        self.theme_cls.theme_style = "Dark"

    def clear(self):
        self.root.ids.user.text = ""
        self.root.ids.password.text = ""

    def registration(self):
        username = self.root.ids.user_reg.text
        password = self.root.ids.password_reg.text
        name = self.root.ids.name_reg.text
        self.sql.execute(f"SELECT login FROM user WHERE login = '{username}'")

        if name == '' or username == '' or password == '':
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Заполните все поля')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()
        elif self.sql.fetchone() is None:
            self.sql.execute(f"INSERT INTO user VALUES ('{username}', '{password}', '{name}', 'NULL', 'NULL', 'NULL')")
            self.conn.commit()
            print('You have registered')
            self.root.current = "weight"

        else:
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Такая учетная запись уже существует')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()

    def login(self):
        username = self.root.ids.user.text
        password = self.root.ids.password.text
        a = self.sql.execute(
            f"SELECT login, password FROM user WHERE login = '{username}' AND password = '{password}'")
        self.conn.commit()
        if username == '' or password == '':
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Заполните все поля')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()
        elif not self.sql.fetchone():
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Неверный логин/пароль')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()
        else:
            self.root.current = "main"

    def toFixed(numObj, digits=0):
        return f"{numObj:.{digits}f}"

    def acc_upd(self):
        weight = ''
        weight_start = ''
        weight_des = ''
        username = self.root.ids.user.text
        if username == '':
            username = self.root.ids.user_reg.text
        for i in self.sql.execute(f"SELECT weight, weight_start, weight_des FROM user WHERE login = '{username}'"):
            weight = str(i[0])
            weight_start = str(i[1])
            weight_des = str(i[2])

        self.conn.commit()
        self.root.ids.prog_bar.max = abs(int(weight_des)-int(weight_start))
        self.root.ids.prog_bar.value = abs(int(weight)-int(weight_start))
        progr = int(self.root.ids.prog_bar.value)/int(self.root.ids.prog_bar.max)*100
        progr = float('{:.1f}'.format(progr))
        if weight_des > weight_start and weight<weight_start:
            progr = 0.0
            self.root.ids.prog_bar.value = 0
        elif weight_des < weight_start and weight > weight_start:
            progr = 0.0
            self.root.ids.prog_bar.value = 0

        self.root.ids.prog_bar_txt.text = f"{progr}% Progress"
        self.root.ids.weight_upd.text = weight
        self.root.ids.weight_upd_start.text = "Начальный вес: " + weight_start
        self.root.ids.weight_upd_des.text = "Желанный вес: " + weight_des


    def weight_now_update(self):
        username = self.root.ids.user.text
        if username == '':
            username = self.root.ids.user_reg.text
        weight_now = self.root.ids.weight_now.text
        self.sql.execute(
            f"UPDATE user SET weight = '{weight_now}' WHERE login = '{username}'")
        self.conn.commit()
        self.sql.execute(
            f"INSERT INTO user_weight VALUES('{username}', '{weight_now}')")
        self.conn.commit()
        self.acc_upd()
        self.root.ids.weight_now.text = ''
        self.root.current = "main"


    def weight_reg(self):
        username = self.root.ids.user_reg.text
        weight_start = self.root.ids.weight_start.text
        weight = self.root.ids.weight_start.text
        weight_des = self.root.ids.weight_des.text

        if weight_start == '' or weight_des == '':
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Заполните все поля')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()
        else:
            self.sql.execute(
                f"UPDATE user SET weight_start = '{weight_start}', weight = '{weight}', weight_des='{weight_des}' WHERE login = '{username}'")
            self.conn.commit()
            self.sql.execute(
                f"INSERT INTO user_weight VALUES('{username}', '{weight_start}')")
            self.conn.commit()
            self.root.current = "main"

    def go_to_main(self, k, cal, prot, fat):
        self.root.ids.breakfast.add_widget(k)
        self.root.ids.food_menu.clear_widgets()
        self.root.ids.calories_num.text = str(float(self.root.ids.calories_num.text)+float(cal))
        self.root.ids.protein_num.text = str(float(self.root.ids.protein_num.text)+float(prot))
        self.root.ids.fats_num.text = str(float(self.root.ids.fats_num.text)+float(fat))
        self.root.current = 'main'

    def menu_insert(self):
        a = self.sql.execute(
            f"SELECT * FROM food")
        for i in a:
            cal = i[1]
            prot = i[2]
            fat = i[3]
            k = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            f = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            k.bind(on_press= lambda x, j=f, calories=cal, protein=prot, fats=fat: self.go_to_main(j, calories, protein, fats))
            self.root.ids.food_menu.add_widget(k)
        self.root.current = "food_menu"

    def go_to_main_dinner(self, k, cal, prot, fat):
        self.root.ids.dinner.add_widget(k)
        self.root.ids.food_menu_dinner.clear_widgets()
        self.root.ids.calories_num.text = str(float(self.root.ids.calories_num.text) + float(cal))
        self.root.ids.protein_num.text = str(float(self.root.ids.protein_num.text) + float(prot))
        self.root.ids.fats_num.text = str(float(self.root.ids.fats_num.text) + float(fat))
        self.root.current = 'main'

    def menu_insert_dinner(self):
        a = self.sql.execute(
            f"SELECT * FROM food")
        for i in a:
            cal = i[1]
            prot = i[2]
            fat = i[3]
            k = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            f = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            k.bind(on_press= lambda x, j=f, calories=cal, protein=prot, fats=fat: self.go_to_main_dinner(j, calories, protein, fats))
            self.root.ids.food_menu_dinner.add_widget(k)
        self.root.current = "food_menu_dinner"

    def go_to_main_even(self, k, cal, prot, fat):
        self.root.ids.even.add_widget(k)
        self.root.ids.food_menu_even.clear_widgets()
        self.root.ids.calories_num.text = str(float(self.root.ids.calories_num.text) + float(cal))
        self.root.ids.protein_num.text = str(float(self.root.ids.protein_num.text) + float(prot))
        self.root.ids.fats_num.text = str(float(self.root.ids.fats_num.text) + float(fat))
        self.root.current = 'main'

    def menu_insert_even(self):
        a = self.sql.execute(
            f"SELECT * FROM food")
        for i in a:
            cal = i[1]
            prot = i[2]
            fat = i[3]
            k = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            f = OneLineListItem(text=f"{i[0]}     калории: {i[1]}     белки: {i[2]}г.     жиры: {i[3]}г.")
            k.bind(on_press= lambda x, j=f, calories=cal, protein=prot, fats=fat: self.go_to_main_even(j, calories, protein, fats))
            self.root.ids.food_menu_even.add_widget(k)
        self.root.current = "food_menu_even"

    def food_insert(self):
        name_food = self.root.ids.name_food.text
        calories = self.root.ids.calories.text
        proteins = self.root.ids.proteins.text
        fats = self.root.ids.fats.text

        if name_food == '' or calories == '' or proteins == '' or fats == '':
            content = BoxLayout(orientation='vertical')
            lbl = Label(text='Заполните все поля')
            content.add_widget(lbl)
            popup = Popup(title='Ошибка',
                          content=content,
                          size_hint=(None, None), size=(300, 200))
            popup.open()
        else:
            self.sql.execute(
                f"INSERT INTO food VALUES ('{name_food}', '{calories}', '{proteins}', '{fats}', 'no')")
            self.conn.commit()
            self.root.ids.food_menu.clear_widgets()
            self.root.ids.food_menu_dinner.clear_widgets()
            self.root.current = "main"

    def matplot(self):
        x = []
        y=[]
        g = 0
        username = self.root.ids.user.text
        if username == '':
            username = self.root.ids.user_reg.text
        a = self.sql.execute(
            f"SELECT weight FROM user_weight WHERE login = '{username}'")
        for j in a:
            y.append(j[0])
            g+=1
            x.append(g)
        plt.plot(x,y)
        plt.ylabel('Y')
        plt.xlabel('X')
        self.root.ids.box.add_widget(plt.show())




class WindowManager(ScreenManager):
    pass

class MainWindow(Screen):
    pass

class Auth(Screen):
    pass

class Registr(Screen):
    pass

class Weight(Screen):
    pass

class Weight_upd(Screen):
    pass

class Food_Menu(Screen):
    pass

class Food_Menu_Dinner(Screen):
    pass

class Food_Menu_Even(Screen):
    pass

class Food_Insert(Screen):
    pass

Diet().run()