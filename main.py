import pygame as pg
import numpy as np
import array

# I have literally zero idea what I'm doing
# én amikor C++ programozónak érzem magam python-ban
# mondtam már, hogy utálom a pythont?

# oké, tehát
# kinyit egy ablakot, es kivalaszt egy random easy slithersnake-t
# de aztan van egy opcio, hogy valasszon egy uj randomat
# vagy hogy az ember beadja a sajatjat

ll = np.int64
# megszokás kérdése

v = np.zeros((1, 1), dtype=np.int8) # ez lesz a vektor ahol eltaroljuk a dolgokat
# strukturailag eleg csunya lesz
# de a lenyeg az
# kb 3*szor annyi helyet foglal, mert az egesz tablazatot egy 2d's array-ben akarom eltarolni
# tehat az {1,1} , {1,3}, . . ., {3,1}, {3,3}, etc
# vannak maguk a cellák értékei
# és direkt a cella felett/alatt/melett pedig egy 0/1 ertek, hogy be van-e huzva

# n = 100
# v = np.zeros((n, n), dtype=np.int64)

def main():
    # kinyitunk egy windowt
    # es felrajzoljuk
    print("hello") 

if __name__ == "__main__":
    main()