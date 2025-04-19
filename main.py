import pygame as pg
import pygame_gui as pgui
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
m = 1 # oszlopok szama, j-s iterator

solcalc : bool = False # has the solution been calculated already?
# ez akkor igaz, ha egy pregeneralt board-ot veszunk
# vagy ha helyben generalunk egyet

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

def initwindow():
    # pygame, do your magic  
    pg.init()
    height:int = 900
    width:int = 1600
    screen = pg.display.set_mode((width,height))
    pg.display.set_caption("Slitherlink")
    pg.display.init()
    
    backgroundcolor = (255, 251, 187)
    
    background = pg.Surface((width, height), pg.SRCALPHA)
    background.fill(backgroundcolor)
    
    clock = pg.time.Clock()
    
    clock.tick(60)
    
    manager = pgui.UIManager((width, height), theme_path=os.path.join(base_dir, "testtheme.json"))
    
    # minden elemrol kideritjuk, hogy micsoda
    # ha pont vagy szam, muszaj felrajzoljuk
    # ha viszont vonal, akkor csak egy lathatatlant rajzolunk be
    # vagyis egy olyant, ami a hatterszinnel egyenlo ;)
    
    y1:int = 0.10 * height; x1:int = 0.10 * width; # top left corner
    y2:int = 0.75 * height; x2:int = 0.75 * width; # bottom right corner
    
    ystep = (y2-y1)/n
    xstep = (x2-x1)/m
    
    # pythonban top left 0,0
    # y1, x1 olyan ~5-10%al legyenek beljebb
    # y2 csak olyan ~5-10%al, x2 pedig ~5-10% + meg a gomboknak a hely
    
    place = np.zeros((2 * n + 1, 2 * m + 1, 2), dtype=np.int32)
    # [i][j][0] = y cord, [i][j][1] = x cord
    
    # eloszor lerakjuk a pontokat
    
    cy:int = y1;
    cx:int = x1
    
    pointradius = 20;
    fontsize = 60;
    
    font = pg.font.Font(os.path.join(base_dir, "Lexend-Regular.ttf"), fontsize)
    
    # rendering points
    for i in range(0, 2 * n + 1, 2):
      for j in range(0, 2 * m + 1, 2):
        place[i][j][0] = cy;
        place[i][j][1] = cx;
        pg.draw.circle(background, (0, 0, 0), (cx, cy), pointradius)
        cx += xstep
      cy += ystep;
      cx = x1
    # rendering numbers
    for i in range(1, 2 * n + 1, 2):
      for j in range(1, 2 * m + 1, 2):
        cy = (place[i-1][j-1][0] + place[i+1][j-1][0])/2
        cx = (place[i-1][j-1][1] + place[i-1][j+1][1])/2
        curr = v[i][j]
        if(curr == -1):
          continue;
        text_surface = font.render(str(curr), True, (0,0,0))
        rect = text_surface.get_rect(center=(cx, cy))
        background.blit(text_surface, rect)
    test_button = pgui.elements.UIButton(relative_rect=pg.Rect((1300, 50), (200, 100)),text='test:Hello World',manager=manager)

    running: bool = True
    while running:
      time_delta = clock.tick(60)/1000.0
      for event in pg.event.get():
        if event.type == pg.QUIT:  # This fires when the window close button is clicked
            running = False
        if event.type == pgui.UI_BUTTON_PRESSED:
          if event.ui_element == test_button:
              print("Hello world")
        manager.process_events(event)
      
      manager.update(time_delta)
      
      screen.blit(background, (0,0))
      manager.draw_ui(screen)
      
      pg.display.flip()

def initboards():
    # comment
    global base_dir
    global text_files
    global pregenboardspath
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pregenboardspath = os.path.join(base_dir, 'pregenboards')  # folder is in the same directory as main.py
    text_files = [f for f in os.listdir(pregenboardspath) if f.endswith('.txt')]
    
def printtotal(arr, n, m):
    print("\nfull=\n")
    for i in range(0, 2 * n + 1, 1):
        for j in range(0, 2 * m + 1, 1):
          curr = arr[i][j]
          if(i % 2 == 0 and j % 2 == 0):
            curr = '•'
          if(i % 2 == 0 and j % 2 == 1):
            #vertical line
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
    with open(os.path.join(pregenboardspath, random_file), 'r') as file:
      content = file.read()
    
    #print(f"File:{random_file}")
    #print(content)
    
    parts = iter(content.split())
    n = int(next(parts))
    m = int(next(parts))
    v = np.zeros((2 * n +1, 2 * m + 1), dtype=np.int8)
    sol = np.zeros((2 * n + 1, 2 *m + 1), dtype=np.int8)
    solcalc = True
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
    
    initwindow()
    
    pg.quit()

if __name__ == "__main__":
    main()