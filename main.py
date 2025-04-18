import pygame as pg
import numpy as np
import os
import random

# I have literally zero idea what I'm doing
# én amikor C++ programozónak érzem magam python-ban
# mondtam már, hogy utálom a pythont?

# oké, tehát
# kinyit egy ablakot, es kivalaszt egy random easy slithersnake-t
# de aztan van egy opcio, hogy valasszon egy uj randomat
# vagy hogy az ember beadja a sajatjat

n = 1 # sorok szama, i-s iterator
m = 1# oszlopok szama, j-s iterator

sol = np.zeros((1, 1), dtype=np.int8)
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
  0   1 2   3 4   5 6 
0 •	 --	•	 --	•	 --	•
1 |	  3	|	  2	|		  |
2 •	 --	•	 --	•	 --	•
3 |		  |	  2	|	  1	|
4 •	 --	•	 --	•	 --	•
5 |		  |	  3	|		  |
6 •	 --	•	 --	•	 --	•

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
    
    screen.fill((255, 251, 187))    
    
    running: bool = True
    while running:
      for event in pg.event.get():
        pg.display.flip()
        if event.type == pg.QUIT:  # This fires when the window close button is clicked
            running = False

def initboards():
    # comment
    global text_files
    global folder_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, 'pregenboards')  # folder is in the same directory as main.py
    text_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
def printtotal(arr, n, m):
    print("\nfull=\n")
    for i in range(0, 2 * n + 1, 1):
        for j in range(0, 2 * m + 1, 1):
          curr = arr[i][j]
          if(i % 2 == 0 and j % 2 == 0):
            curr = '•'
          if(i % 2 == 0 and j % 2 == 1):
            #horizontal line
            if(curr == 1):
              curr = '⎯'
            else:
              curr = " "
          if(i % 2 == 1 and j % 2 == 0):
            if(curr == 1):
              curr = '|'
            else:
              curr = " "
          if(i % 2 == 1 and j % 2 == 1):
            if(curr == -1):
              curr = " "    
          print(curr, end=" ")
        print(" ")

def printnumbers(arr, n, m):
  print("\nnumbers=\n")
  for i in range(1, 2 * n + 1, 2):
      for j in range(1, 2 * m + 1, 2):
          curr = arr[i][j]
          if(curr == -1):
            curr = '.'
          print(curr, end=" ")
      print(" ")

def getrandomboard():
    global v
    global sol
    global n
    global m
  
    v = np.zeros((1, 1), dtype=np.int8) # reset-eljuk a vektort
    # kinyitunk egy random file-t a pregenboards-bol
    
    random_file = random.choice(text_files)
    with open(os.path.join(folder_path, random_file), 'r') as file:
      content = file.read()
    
    #print(f"File:{random_file}")
    #print(content)
    
    parts = iter(content.split())
    n = int(next(parts))
    m = int(next(parts))
    v = np.zeros((2 * n +1, 2 * m + 1), dtype=np.int8)
    sol = np.zeros((2 * n + 1, 2 *m + 1), dtype=np.int8)
    for i in range(1, 2 * n + 1, 2):
        for j in range(1, 2 * n + 1, 2):
            curr = next(parts)
            if(curr == '.'):
              v[i][j] = -1
            else:
              v[i][j] = curr
            sol[i][j] = v[i][j]
            
    for i in range(0, 2 * n + 1):
        jstart = 0
        if(i % 2 == 0):
          jstart = 1
        
        for j in range(jstart, 2 * m + 1, 2):
          sol[i][j] = next(parts)
          
    printnumbers(v, n, m)
    printtotal(sol, n, m)

def main():
    # kinyitunk egy windowt
    # es felrajzoljuk
    initboards()
    
    getrandomboard()
    
    #initwindow()
    
    pg.quit()

if __name__ == "__main__":
    main()