import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5 import QtCore, Qt
import requests
import pathlib
from scipy.stats import binom

shiny_chance = 1 / 4096
shiny_chance_text = "1/4096"
pokedex = {}

app = QApplication([])

window = QWidget()

count_increment_label = QLabel()

shiny_chance_label = QLabel()

binomial_distribution_label = QLabel()

image_label = QLabel()

with open("./resources/pokedex/pokedex.txt", "r") as f:
    for line in f:
        (val, key) = line.strip().split(" ", 1)
        pokedex[str(key.lower())] = val


def get_pokemon_image(pokemon):
    if pokemon != "unknown":
        path = pathlib.Path("./resources/shiny_pokemon_images/" + pokemon + ".png")
        gen = "SM/"
        if not path.exists():
            pokemon_id = str(pokedex[pokemon])
            if "a" in pokemon_id:
                gen = "SM/"
            if "g" in pokemon_id:
                gen = "SWSH/"
            if "a" not in pokemon_id and "g" not in pokemon_id:
                if int(pokemon_id) < 810:
                    gen = "SM/"
                else:
                    gen = "SWSH/"

            url = "https://www.serebii.net/Shiny/" + gen + pokemon_id + ".png"
            shiny_file = requests.get(url)
            shiny_name = pokemon + ".png"
            open("./resources/shiny_pokemon_images/" + shiny_name, "wb").write(shiny_file.content)


encounters_box = QLineEdit()
pokemon_box = QLineEdit()
method_box = QComboBox()
shiny_charm_box = QComboBox()
lure_box = QComboBox()
game_version_box = QComboBox()

method_box.addItems(["Random Encounters", "Egg Hatching", "Dynamax Battles", "Lure", "Masuda Method", "PokeRadar Chaining",
                     "Consecutive Fishing", "Catch Combo"])

shiny_charm_box.addItems(["No", "Yes"])

lure_box.addItems(["No", "Yes"])

game_version_box.addItems(["SW/SH", "Let's Go", "S/M/US/UM", "X/Y", "B/W/B2/W2", "D/P/Plat", "R/S/E", "G/S",
                           "R/B"])

with open("preferences.txt", "r") as f:
    lines = f.readlines()
    if not lines:
        pokemon = "unknown"
    elif lines[1].strip() == "":
        pokemon = "unknown"
    else:
        encounters_box.setText(lines[0])
        pokemon = lines[1].strip().lower()
        pokemon_box.setText(lines[1].strip())
        method = lines[2].strip()
        method_box.setCurrentIndex(int(method))
        shiny_charm = lines[3].strip()
        shiny_charm_box.setCurrentIndex(int(shiny_charm))
        lure = lines[4].strip()
        lure_box.setCurrentIndex(int(lure))
        game_version = lines[5].strip()
        game_version_box.setCurrentIndex(int(game_version))
        shiny_chance_label.setText(lines[6].strip())
        binomial_distribution_label.setText(lines[7].strip())
    get_pokemon_image(pokemon)


def save_clicked():
    if str(pokemon_box.text()).lower() in pokedex:
        with open("preferences.txt", "w") as file:
            file.write(str(encounters_box.text()))
            file.write("\n")
            file.write(str(pokemon_box.text()).lower())
            file.write("\n")
            file.write(str(method_box.currentIndex()))
            file.write("\n")
            file.write(str(shiny_charm_box.currentIndex()))
            file.write("\n")
            file.write(str(lure_box.currentIndex()))
            file.write("\n")
            file.write(str(game_version_box.currentIndex()))
            file.write("\n")
            file.write(str(shiny_chance_label.text()))
            file.write("\n")
            file.write(str(binomial_distribution_label.text()))

        count_increment_label.setText(str(encounters_box.text()))
        pokemon = pokemon_box.text().lower()
        get_pokemon_image(pokemon)
        mon_pixmap = QPixmap("./resources/shiny_pokemon_images/" + pokemon + ".png")
        mon_pixmap = mon_pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        image_label.setPixmap(mon_pixmap)
        chance = shiny_chance()
        binomial_distribution(chance)
        window.setWindowTitle("Shiny Counter for: " + pokemon.capitalize())
    else:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("Cannot find pokemon:")
        error_dialog.setInformativeText('Ensure you have spelt the name correctly!\nRemember to specify regional forms '
                                        '\nex. Farfetch\'d-Galar or Rattata-Alola!')
        error_dialog.setWindowTitle("Cannot find pokemon!")
        error_dialog.exec_()


save_button = QPushButton()
save_button.setText("Save changes")
save_button.clicked.connect(save_clicked)

shine_pixmap = QPixmap("./resources/app_images/" + "shine.png")

gear_icon = QPixmap("./resources/app_images/" + "settings.png")
gear_icon = gear_icon.scaled(96, 96, QtCore.Qt.KeepAspectRatio)


def encounters_changed():
    count_increment_label.setText(str(encounters_box.text()))


def normal_round(num, ndigits=0):
    """
    Rounds a float to the specified number of decimal places.
    num: the value to round
    ndigits: the number of digits to round to
    """
    if ndigits == 0:
        return int(num + 0.5)
    else:
        digit_value = 10 ** ndigits
        return int(num * digit_value + 0.5) / digit_value


def shiny_chance():
    if game_version_box.currentText() == "SW/SH":
        if method_box.currentText() == "Dynamax Battles":
            if shiny_charm_box.currentText() == "No":
                shiny_chance_label.setText("Shiny Chance: 1/300")
                return 1 / 300
            else:
                shiny_chance_label.setText("Shiny Chance: 1/100")
                return 1 / 100
        else:
            if shiny_charm_box.currentText() == "No":
                if int(count_increment_label.text()) < 50:
                    shiny_chance_label.setText("Chance: 1/4096")
                    return 1 / 4096
                elif 50 <= int(count_increment_label.text()) < 100:
                    shiny_chance_label.setText("Chance: 1/2048")
                    return 1 / 2048
                elif 100 <= int(count_increment_label.text()) < 200:
                    shiny_chance_label.setText("Chance: 1/1365")
                    return 1 / 1365.333
                elif 200 <= int(count_increment_label.text()) < 300:
                    shiny_chance_label.setText("Chance: 1/1024")
                    return 1 / 1024
                elif 300 <= int(count_increment_label.text()) < 500:
                    shiny_chance_label.setText("Chance: 1/819")
                    return 1 / 819.2
                else:
                    shiny_chance_label.setText("Chance: 1/683")
                    return 1 / 682.6667
            else:
                if int(count_increment_label.text()) < 50:
                    shiny_chance_label.setText("Chance: 1/1365")
                    return 1 / 1365.33
                elif 50 <= int(count_increment_label.text()) < 100:
                    shiny_chance_label.setText("Chance: 1/1024")
                    return 1 / 1024
                elif 100 <= int(count_increment_label.text()) < 200:
                    shiny_chance_label.setText("Chance: 1/819")
                    return 1 / 819.2
                elif 200 <= int(count_increment_label.text()) < 300:
                    shiny_chance_label.setText("Chance: 1/683")
                    return 1 / 682.6667
                elif 300 <= int(count_increment_label.text()) < 500:
                    shiny_chance_label.setText("Chance: 1/585")
                    return 1 / 585.1429
                else:
                    shiny_chance_label.setText("Chance: 1/512")
                    return 1 / 512
    elif game_version_box.currentText() == "Let's Go":
        if lure_box.currentText() == "Yes":
            if shiny_charm_box.currentText() == "No":
                shiny_chance_label.setText("Chance: 1/2048")
                return 1 / 2048
            else:
                shiny_chance_label.setText("Chance: 1/1024")
                return 1 / 1024
        elif method_box.currentText() == "Catch Combos":
            if lure_box.currentText() == "Yes":
                if shiny_charm_box.currentText() == "Yes":
                    if int(count_increment_label.text()) < 11:
                        shiny_chance_label.setText("Chance: 1/1024")
                        return 1 / 1024
                    elif 11 <= int(count_increment_label.text()) < 21:
                        shiny_chance_label.setText("Chance: 1/585")
                        return 1 / 585.1429
                    elif 21 <= int(count_increment_label.text()) < 31:
                        shiny_chance_label.setText("Chance: 1/372")
                        return 1 / 372.36
                    else:
                        shiny_chance_label.setText("Chance: 1/273")
                        return 1 / 273.07
                else:
                    if int(count_increment_label.text()) < 11:
                        shiny_chance_label.setText("Chance: 1/2048")
                        return 1 / 2048
                    elif 11 <= int(count_increment_label.text()) < 21:
                        shiny_chance_label.setText("Chance: 1/819")
                        return 1 / 819.2
                    elif 21 <= int(count_increment_label.text()) < 31:
                        shiny_chance_label.setText("Chance: 1/455")
                        return 1 / 455.1
                    else:
                        shiny_chance_label.setText("Chance: 1/315")
                        return 1 / 315.08
            else:
                if shiny_charm_box.currentText() == "Yes":
                    if int(count_increment_label.text()) < 11:
                        shiny_chance_label.setText("Chance: 1/1365")
                        return 1 / 1365.3
                    elif 11 <= int(count_increment_label.text()) < 21:
                        shiny_chance_label.setText("Chance: 1/683")
                        return 1 / 682.6
                    elif 21 <= int(count_increment_label.text()) < 31:
                        shiny_chance_label.setText("Chance: 1/409")
                        return 1 / 409.6
                    else:
                        shiny_chance_label.setText("Chance: 1/293")
                        return 1 / 292.57
                else:
                    if int(count_increment_label.text()) < 11:
                        shiny_chance_label.setText("Chance: 1/4096")
                        return 1 / 4096
                    elif 11 <= int(count_increment_label.text()) < 21:
                        shiny_chance_label.setText("Chance: 1/1024")
                        return 1 / 1024
                    elif 21 <= int(count_increment_label.text()) < 31:
                        shiny_chance_label.setText("Chance: 1/512")
                        return 1 / 512
                    else:
                        shiny_chance_label.setText("Chance: 1/341")
                        return 1 / 341.3
        else:
            if shiny_charm_box.currentText() == "No":
                shiny_chance_label.setText("Chance: 1/4096")
                return 1 / 4096
            else:
                shiny_chance_label.setText("Chance: 1/1365")
                return 1 / 1365


def binomial_distribution(chance):
    n = int(count_increment_label.text())
    k = chance
    max_chance = 0.3682
    if n * k >= 1:
        binomial_distribution_mass = (max_chance - binom.pmf(1, n, k)) + max_chance
    else:
        binomial_distribution_mass = binom.pmf(1, n, k)
    binomial_distribution_label.setText("B(n, p): " + str(round(100 * binomial_distribution_mass, 2)) + "%")


def increase_clicked():
    count_increment_label.setText(str((int(count_increment_label.text()) + 1)))
    chance = shiny_chance()
    binomial_distribution(chance)


increase_button = QPushButton("+ 1")
increase_button.clicked.connect(increase_clicked)


def decrease_clicked():
    if (int(count_increment_label.text()) - 1) >= 0:
        count_increment_label.setText(str((int(count_increment_label.text()) - 1)))
        chance = shiny_chance()
        binomial_distribution(chance)


decrease_button = QPushButton("- 1")
decrease_button.clicked.connect(decrease_clicked)


def reset_clicked():
    count_increment_label.setText(str((int(0))))
    chance = shiny_chance()
    binomial_distribution(chance)


reset_button = QPushButton("Reset")
reset_button.clicked.connect(reset_clicked)

previous_catch_label = QLabel()


def caught_clicked():
    dummy_file = "catch_history.bak"
    if method_box.currentText() == "Egg Hatching":
        if count_increment_label.text() == "1":
            with open("catch_history.txt", "r+") as curr_file, open(dummy_file, 'w') as bak_file:
                bak_file.write(
                    "Hatched " + str(pokemon_box.text()).capitalize() + " in " + str(count_increment_label.text()) +
                    " try with " + str(shiny_chance_label.text()) + " in " + str(game_version_box.currentText()) +
                    " with the " + str(method_box.currentText()) + " method.\n")
                for prev_catches in curr_file:
                    bak_file.write(prev_catches)
        else:
            with open("catch_history.txt", "r+") as curr_file, open(dummy_file, 'w') as bak_file:
                bak_file.write(
                    "Hatched " + str(pokemon_box.text()).capitalize() + " in " + str(count_increment_label.text()) +
                    " tries with " + str(shiny_chance_label.text()) + " in " + str(game_version_box.currentText()) +
                    " with the " + str(method_box.currentText()) + " method.\n")
                for prev_catches in curr_file:
                    bak_file.write(prev_catches)
    else:
        if count_increment_label.text() == "1":
            with open("catch_history.txt", "r+") as curr_file, open(dummy_file, 'w') as bak_file:
                bak_file.write(
                    "Caught " + str(pokemon_box.text()).capitalize() + " in " + str(count_increment_label.text()) +
                    " try with " + str(shiny_chance_label.text()) + " in " + str(game_version_box.currentText()) +
                    " with the " + str(method_box.currentText()) + " method.\n")
                for prev_catches in curr_file:
                    bak_file.write(prev_catches)
        else:
            with open("catch_history.txt", "r+") as curr_file, open(dummy_file, 'w') as bak_file:
                bak_file.write(
                    "Caught " + str(pokemon_box.text()).capitalize() + " in " + str(count_increment_label.text()) +
                    " tries with " + str(shiny_chance_label.text()) + " in " + str(game_version_box.currentText()) +
                    " with the " + str(method_box.currentText()) + " method.\n")
                for prev_catches in curr_file:
                    bak_file.write(prev_catches)
    curr_file.close()
    bak_file.close()
    os.remove("catch_history.txt")
    os.rename(dummy_file, "catch_history.txt")
    count_increment_label.setText(str((int(0))))
    chance = shiny_chance()
    binomial_distribution(chance)
    catch_history_file = open('./catch_history.txt', 'r')
    number_of_lines = 20
    catch_history_text = ""
    for i in range(number_of_lines):
        catch_history_line = catch_history_file.readline()
        catch_history_text = catch_history_text + catch_history_line
    previous_catch_label.setText(catch_history_text)


caught_button = QPushButton("Shiny!")
caught_button.clicked.connect(caught_clicked)


def counter_tab_UI():
    counter_tab = QWidget()
    counter_layout = QGridLayout()
    mon_pixmap = QPixmap("./resources/shiny_pokemon_images/" + pokemon + ".png")
    mon_pixmap = mon_pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
    image_label.setAlignment(QtCore.Qt.AlignCenter)
    image_label.setPixmap(mon_pixmap)
    counter_layout.addWidget(image_label, 0, 1)
    count_increment_label.setFont(QFont('Times', 16))
    count_increment_label.setAlignment(QtCore.Qt.AlignCenter)
    counter_layout.addWidget(count_increment_label, 1, 1)
    shiny_chance_label.setFont(QFont('Times', 12))
    shiny_chance_label.setAlignment(QtCore.Qt.AlignCenter)
    counter_layout.addWidget(shiny_chance_label, 3, 1)
    binomial_distribution_label.setFont(QFont('Times', 12))
    binomial_distribution_label.setAlignment(QtCore.Qt.AlignCenter)
    counter_layout.addWidget(binomial_distribution_label, 4, 1)
    counter_layout.addWidget(increase_button, 5, 0)
    counter_layout.addWidget(reset_button, 5, 1)
    counter_layout.addWidget(decrease_button, 5, 2)
    counter_layout.addWidget(caught_button, 6, 1)
    counter_tab.setLayout(counter_layout)
    return counter_tab


def catch_tab_UI():
    catch_tab = QWidget()
    catch_layout = QGridLayout()
    previous_catch_text_label = QLabel()
    previous_catch_text_label.setText("Previous 20 Shiny Encounters: ")
    previous_catch_text_label.setFont(QFont('Times', 16))
    catch_layout.addWidget(previous_catch_text_label, 0, 0)
    catch_history_file = open('./catch_history.txt', 'r')
    number_of_lines = 20
    catch_history_text = ""
    for i in range(number_of_lines):
        line = catch_history_file.readline()
        catch_history_text = catch_history_text + line
    previous_catch_label.setFont(QFont('Times', 10))
    previous_catch_label.setText(catch_history_text)
    catch_layout.addWidget(previous_catch_label, 1, 0)
    catch_tab.setLayout(catch_layout)
    return catch_tab


def settings_tab_UI():
    settings_tab = QWidget()
    settings_layout = QFormLayout()
    settings_layout.addRow("Method:", method_box)
    settings_layout.addRow("Pokemon Version:", game_version_box)
    settings_layout.addRow("Shiny Charm?", shiny_charm_box)
    settings_layout.addRow("Lure? (Lets Go Only)", lure_box)
    settings_layout.addRow("Encounters:", encounters_box)
    settings_layout.addRow("Pokemon:", pokemon_box)
    settings_layout.addRow(QLabel("Note: Please specify regional forms eg 'Darumaka-Galar'"))
    settings_layout.addRow(save_button)
    settings_tab.setLayout(settings_layout)
    return settings_tab


layout = QGridLayout()

tabs = QTabWidget()
tabs.addTab(counter_tab_UI(), "Counter")
tabs.addTab(catch_tab_UI(), "Catch History")
tabs.addTab(settings_tab_UI(), "Settings")
layout.addWidget(tabs)

window.setWindowTitle("Shiny Counter for: " + pokemon.capitalize())
window.setWindowIcon(QIcon(shine_pixmap))
window.setLayout(layout)

with open("preferences.txt", "r") as f:
    lines = f.readlines()
    if lines:

        if lines[0].strip() == "":
            count_increment_label.setText("0")
        else:
            count_increment_label.setText(str(lines[0].strip()))

window.show()


def exit_process():
    with open("preferences.txt", "w") as file:
        file.write(str(count_increment_label.text()))
        file.write("\n")
        if str(pokemon_box.text()).lower() in pokedex:
            file.write(str(pokemon_box.text()).lower())
            file.write("\n")
        else:
            file.write("snover")
            file.write("\n")
        file.write(str(method_box.currentIndex()))
        file.write("\n")
        file.write(str(shiny_charm_box.currentIndex()))
        file.write("\n")
        file.write(str(lure_box.currentIndex()))
        file.write("\n")
        file.write(str(game_version_box.currentIndex()))
        file.write("\n")
        file.write(str(shiny_chance_label.text()))
        file.write("\n")
        file.write(str(binomial_distribution_label.text()))


app.aboutToQuit.connect(exit_process)

app.exec_()
