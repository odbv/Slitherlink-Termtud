import pygame as pg
import numpy as np

# I have literally zero idea what I'm doing
# én amikor C++ programozónak érzem magam python-ban
# mondtam már, hogy utálom a pythont?

# oké, tehát
# kinyit egy ablakot, es kivalaszt egy random easy slithersnake-t
# de aztan van egy opcio, hogy valasszon egy uj randomat
# vagy hogy az ember beadja a sajatjat

n:np.int16 # sorok szama, i-s iterator
m:np.int16 # oszlopok szama, j-s iterator

v = np.zeros((1, 1), dtype=np.int8) # ez lesz a vektor ahol eltaroljuk a dolgokat
# strukturailag eleg csunya lesz
# de a lenyeg az
# kb 3*szor annyi helyet foglal, mert az egesz tablazatot egy 2d's array-ben akarom eltarolni
# tehat az {1,1} , {1,3}, . . ., {3,1}, {3,3}, etc
# vannak maguk a cellák értékei
# és direkt a cella felett/alatt/melett pedig egy 0/1 ertek, hogy be van-e huzva

'''

szóval pl
ez a táblázat
  0 1 2
0 3 2 
1   2 1
2   3

igy nezne ki
  0  1  2    3  4    5  6 
0 •	--	•	--	•	--	•
1 |	 3	|	 2	|		|
2 •	--	•	--	•	--	•
3 |		|	 2	|	 1	|
4 •	--	•	--	•	--	•
5 |		|	 3	|		|
6 •	--	•	--	•	--	•

(azért van behúzva az összes vonal, hogy látszódjon, az array melyik eleme a táblázat melyik részéről táról információt)
(igen, konkrétan a fele teljesen fölösleges, mert a pontok mindig léteznek)

szép? (nem)
de én írom ezt a hülye programot, én mondom meg hogy csináljuk
meg amúgy az extra memória az nagyon nem befolyásol sokat
50x50-nél nagyobb slitherlink puzzle úgyse kerül, egy 101x101-es array pedig nagyon laza

(n, m) -> (2n+1, 2m+1)

'''

# n = 100
# v = np.zeros((n, n), dtype=np.int64)

def initwindow():
    # pygame, do your magic  
    pg.init()
    screen = pg.display.set_mode((1600,900))
    pg.display.set_caption("Slitherlink")
    pg.display.init()
    
    screen.fill((255, 255, 255))    
    
    running: bool = True
    while running:
      for event in pg.event.get():
        pg.display.flip()
        if event.type == pg.QUIT:  # This fires when the window close button is clicked
            running = False

def getrandomboard():
    del v;
    

def main():
    # kinyitunk egy windowt
    # es felrajzoljuk
    initwindow()
    
    pg.quit()

if __name__ == "__main__":
    main()