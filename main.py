import pygame as pg
import pygame_gui as pgui
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
import sys
from collections import deque
import time
from pysat.solvers import Glucose42
from pysat.card import CardEnc
from pysat.formula import CNF
from pysat.formula import IDPool
import random
import math
from sortedcontainers import SortedList

# I have literally zero idea what I'm doing
# én amikor C++ programozónak érzem magam python-ban
# mondtam már, hogy utálom a pythont?

# három hét után: azért nem épp olyan rossz a python se

startingfile:str = "example_5x5.txt"

auttesting:bool = False
istestinginit:bool = False
testing:bool = False
nosol:bool = False

n = 1 # sorok szama, i-s iterator
m = 1 # oszlopok szama, j-s iterator

solcalc : bool = False # has the solution been calculated already?
# ez akkor igaz, ha egy pregeneralt board-ot veszunk
# vagy ha helyben generalunk egyet

sol = np.zeros((1, 1), dtype=np.int32)
v = np.zeros((1, 1), dtype=np.int32) # ez lesz a vektor ahol eltaroljuk a dolgokat
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

# intializes windows and runs the main game loop
def initwindow():
    global n
    global m
    global v
    global sol
    global solcalc
    
    global istestinginit
    global testing
    
    if(istestinginit): testing = True
    
    # pygame, do your magic  
    pg.init()
    height:int = 900
    width:int = 1600
    screen = pg.display.set_mode((width,height))
    pg.display.set_caption("Slitherlink")
    pg.display.init()
    
    winx, winy = pg.display.get_window_position()
    
    backgroundcolor = (3, 94, 29)
    boardbackgroundcolor = (12, 117, 42) # egy kellemes zold hatter
    # nem is égeti ki az ember szemét éjszaka
    # de nem is az a full fekete
    
    background = pg.Surface((width, height)) # ide kerulnek a szamok
    background.fill(backgroundcolor)
    foreground = pg.Surface((width, height), pg.SRCALPHA) # ide kerulnek a pontok
    foreground.fill((0,0,0,0))
    foreforeground = pg.Surface((width, height), pg.SRCALPHA) # ide irunk ki dolgokat
    foreforeground.fill((0,0,0,0))
    
    clock = pg.time.Clock()
    
    clock.tick(60)
    
    manager = pgui.UIManager((width, height), enable_live_theme_updates=True)
    manager.add_font_paths("comicsanstest", os.path.join("resources", "comicsans.ttf"))
    manager.get_theme().load_theme(os.path.join(resourcespath, "testtheme.json"))
    
    # minden elemrol kideritjuk, hogy micsoda
    # ha pont vagy szam, muszaj felrajzoljuk
    # ha viszont vonal, akkor csak egy lathatatlant rajzolunk be
    # vagyis egy olyant, ami a hatterszinnel egyenlo ;)
    
    # vagy legalabbis az volt a terv; igazabol legeneraljuk a teglalap objektumot
    # anelkul hogy megjelenitenenk
    
    y1:int = 0.10 * height; x1:int = 0.10 * width; # top left corner
    y2:int = 0.85 * height; x2:int = 0.75 * width; # bottom right corner
    
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
    
    pointradius = (5 * 18)/max(n,m);
    fontsize = int(pointradius * 3.33)
    
    # dynamic point radius calculation
    # it's no sweat
    # for n = 5, m = 5 . . . pointradius = 18, fontsize = 60
    # something something point density  
    
    # so take whichever is bigger and go by that
    # so based on that:
    
    # tehat ez egy forditott aranyossang : 5 * 18 = max(n,m) * (pointradius_current)    
    
    font = pg.font.Font(os.path.join(resourcespath, "comicsans.ttf"), fontsize)
    
    # rendering a second background?
    pg.draw.rect(background, boardbackgroundcolor, pg.Rect(x1 - 0.02 * width, y1 - 0.02 * width, (x2-x1) * 1.06, (y2-y1) * 1.1))
    
    lines = np.empty((2*n + 1, 2 * m + 1), dtype=object)
    
    # rendering points
    for i in range(0, 2 * n + 1, 2):
      for j in range(0, 2 * m + 1, 2):
        place[i][j][0] = cy;
        place[i][j][1] = cx;
        pg.draw.circle(foreground, (0, 0, 0), (cx, cy), pointradius)
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
    
    # precompute lines
    for i in range(0, 2 * n + 1, 1):
      jstart = 0
      if(i % 2 == 0):
        jstart = 1
      for j in range(jstart, 2 * m +1, 2):
        cx = 1; cy = 1; rectheight = 1; rectwidth = 1;
        adjy = pointradius * 0.28
        adjx = pointradius * 0.28
        if(i % 2 == 0):
          # horizontal block
          cx = place[i][j-1][1] - adjx; cy = place[i][j-1][0] - adjy
          rectwidth = place[i][j+1][1] - place[i][j-1][1];
          rectheight = pointradius * 0.75
        else:
          # vertical block
          cx = place[i-1][j][1] - adjx; cy = place[i-1][j][0] - adjy
          rectwidth = pointradius * 0.75
          rectheight = place[i+1][j][0] - place[i-1][j][0];
        lines[i][j] = pg.Rect(cx, cy, rectwidth, rectheight)
        pg.draw.rect(screen, (0,0,0), lines[i][j], width=0)
    
    newgame_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.08 * height), (0.18 * width, 0.1 * height)),text='New Game',manager=manager)
    checksol_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.25 * height), (0.18 * width, 0.15 * height)),text='Check if valid',manager=manager)
    showsol_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.5 * height), (0.18 * width, 0.2 * height)),text='Show Solution',manager=manager)

    pg.display.flip();

    showsol:bool = False

    showingcorectness:bool = False
    shownosol:bool = False

    running: bool = True
    stage:int = 0
    # stage 0: base, new game/check sol/show sol buttons
    # stage 1: (after pressing new game) load/gen/insert buttons
    # stage 2: (generate) two boxes for n and m, and one button for submit
    # stage 3: (insert) one large box for the loopy format, and button for submit
    while running:
      time_delta = clock.tick(60)/1000.0
      mousepress:bool = False
      mousecords = (1,1)
      for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
          mousepress = True
          mousecords = event.pos
          if(showingcorectness):
            showingcorectness = False
            valid = False
          if(shownosol):
            shownosol = False
        if event.type == pgui.UI_BUTTON_PRESSED:
          if(stage == 0):
            if event.ui_element == newgame_button:
                # clear existing buttons
                newgame_button.kill()
                checksol_button.kill()
                showsol_button.kill()
                
                stage = 1
                
                new_pregen_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.08 * height), (0.18 * width, 0.15 * height)),text='Load board',manager=manager)
                new_heregen_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.25 * height), (0.18 * width, 0.15 * height)),text='Generate board',manager=manager)
                new_insert_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.42 * height), (0.18 * width, 0.15 * height)),text='Insert board',manager=manager)         
            if event.ui_element == checksol_button:
              valid:bool = checkifvalid(v)
              showingcorectness = True
            if event.ui_element == showsol_button:
              if(showsol == False):
                showsol = True
                showsol_button.set_text("Hide Solution")
              else:
                showsol = False
                showsol_button.set_text("Show Solution")
          elif(stage == 1):
            if event.ui_element == new_pregen_button:
              winx, winy = pg.display.get_window_position()
              newgame_pregen(winx, winy)
              return
            if event.ui_element == new_heregen_button:

              new_pregen_button.kill()
              new_heregen_button.kill()
              new_insert_button.kill()
              
              labeln = pgui.elements.UILabel(relative_rect=pg.Rect((0.8 * width, 0.08 * height), (0.05 * width, 0.05 * height)),text="n =", manager=manager)
              newn_button = pgui.elements.UITextEntryLine(relative_rect=pg.Rect((0.85 * width, 0.08 * height), (0.10 * width, 0.05 * height)), manager=manager)
              labeln = pgui.elements.UILabel(relative_rect=pg.Rect((0.8 * width, 0.15 * height), (0.05 * width, 0.05 * height)),text="m =", manager=manager)
              newm_button = pgui.elements.UITextEntryLine(relative_rect=pg.Rect((0.85 * width, 0.15 * height), (0.10 * width, 0.05 * height)), manager=manager)
              
              submit_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.22 * height), (0.18 * width, 0.08 * height)),text='Submit',manager=manager)
              
              stage = 2              
            if event.ui_element == new_insert_button:
              new_pregen_button.kill()
              new_heregen_button.kill()
              new_insert_button.kill()
              
              stage = 3
              label = pgui.elements.UILabel(relative_rect=pg.Rect((0.8 * width, 0.08 * height), (0.18 * width, 0.05 * height)),text="Game ID:", manager=manager)
              loopystring = pgui.elements.UITextEntryLine(relative_rect=pg.Rect((0.8 * width, 0.15 * height), (0.18 * width, 0.05 * height)), manager=manager)
              submit_button = pgui.elements.UIButton(relative_rect=pg.Rect((0.8 * width, 0.22 * height), (0.18 * width, 0.08 * height)),text='Submit',manager=manager)
          
          elif(stage == 2):
            if event.ui_element == submit_button:
              newn = int(newn_button.text)
              newm = int(newm_button.text)
              newgame_genboard(newn, newm)
              return
          elif(stage == 3):
            if event.ui_element == submit_button:
              gameid = loopystring.text
              newgame_insertboard(gameid)
              return
            
        manager.process_events(event)
      
      screen.blit(background, (0,0))
      
      #if(mousepress):
        #print(f"Mouse click at {mousecords}")
      
      if(showsol):
        if(solcalc == False or testing == True):
          solcalc = True
          testing = False
          start = time.time()
          calculatesolution()
          end = time.time()
          if(nosol):
            shownosol = True
          print(f"Took {end-start} seconds")
      
      for i in range(0, 2 * n + 1, 1):
        jstart = 0
        if(i % 2 == 0):
          jstart = 1
        for j in range(jstart, 2 * m +1, 2):
          
          solinactivecolor = (49, 173, 83)
          inactiveedgecolor = (159, 214, 173)
          
          if(showsol):
            if(sol[i][j] == 1):
              pg.draw.rect(screen, (0,0,0), lines[i][j], width=0)
            else:
              pg.draw.rect(screen, boardbackgroundcolor, lines[i][j], width=0)
            continue
    
          pg.draw.rect(screen, solinactivecolor, lines[i][j], width=0)
          
          if(mousepress):
            if(lines[i][j].collidepoint(mousecords)):
              #print(f"Mouse press detected by {i, j}")
              v[i][j] = 1 - v[i][j]
          
          if(v[i][j] == 0):
            continue
              
          pg.draw.rect(screen, (0,0,0), lines[i][j], width=0)      
      
      screen.blit(foreground, (0,0))
      
      if(showingcorectness):
        validityboxcolor = (109, 9, 143)
        temprect = pg.Rect(width * 0.1, height * 0.2, width * 0.65, height * 0.5)
        pg.draw.rect(foreforeground, validityboxcolor, temprect, border_radius=100)
        font = pg.font.Font(os.path.join(resourcespath, "comicsans.ttf"), 100) 
        # ez egy csoppet sketchy
        # atallitom a font size-ot 100-ra manualisan, hogy ezt akkoraba irja ki
        # aztan visszaallitom az alapmeretre
        if(valid):
              #print("Correct solution! Good job!")
              text_surf = font.render("Correct solution", True, (255, 255, 255))
              text_rect = text_surf.get_rect(center=temprect.center)
              foreforeground.blit(text_surf, text_rect)
        else:
              #print("That still needs some work :/")
              text_surf = font.render("Incorrect solution", True, (255, 255, 255))
              text_rect = text_surf.get_rect(center=temprect.center)
              foreforeground.blit(text_surf, text_rect)
        font = pg.font.Font(os.path.join(resourcespath, "comicsans.ttf"), fontsize)
      
      if(nosol and shownosol):
        validityboxcolor = (138, 32, 32)
        temprect = pg.Rect(width * 0.1, height * 0.2, width * 0.65, height * 0.5)
        pg.draw.rect(foreforeground, validityboxcolor, temprect, border_radius=100)
        font = pg.font.Font(os.path.join(resourcespath, "comicsans.ttf"), 100) 
        # pontosan ugyanugy sketchy mint a masik
        # atallitom a font size-ot 100-ra manualisan, hogy ezt akkoraba irja ki
        # aztan visszaallitom az alapmeretre
        text_surf = font.render("No solution exists", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=temprect.center)
        foreforeground.blit(text_surf, text_rect)
        font = pg.font.Font(os.path.join(resourcespath, "comicsans.ttf"), fontsize)      
      
      screen.blit(foreforeground, (0,0))
      foreforeground.fill((0,0,0,0))
      manager.update(time_delta)
      manager.draw_ui(screen)
      pg.display.flip()

# checks whether a given pair of (i, j) coordinates are inside a standardly structured board
def valid(i, j) -> bool:
  global n
  global m
  
  if(i >= 0 and j >= 0 and i < 2 * n +1 and j < 2 * m + 1):
    return True
  else:
    return False

# checks whether the given board configuration is a valid solution
def checkifvalid(v) -> bool:
  
  global n
  global m
  #global v
  global sol
  
  # 3 tests:
  # point test : checks for each point: each one must have either 0 or 2 lines attached to it
  # cell test : checks for each cell, whether its neighbouring active edges equals its value
  # flood test : checks whether a flood fill is able to fill the entire grid
  
  ground = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  vis = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  
  # point test
  for i in range(0, 2 * n + 1, 2):
    for j in range(0, 2 * m + 1, 2):
      actedges = 0
      if(valid(i, j-1)):
        actedges += v[i][j-1]
        ground[i][j-1] = v[i][j-1]
      if(valid(i,j+1)):
        actedges += v[i][j+1]
        ground[i][j+1] = v[i][j+1]
      if(valid(i+1, j)):
        actedges += v[i+1][j]
        ground[i+1][j] = v[i+1][j]
      if(valid(i-1, j)):
        actedges += v[i-1][j]
        ground[i-1][j] = v[i-1][j]
      
      if(actedges == 0):
        ground[i][j] = 0;
      if(actedges == 2):
        ground[i][j] = 1
      
      if(actedges != 0 and actedges != 2):
        print("Point test failed")
        ret = False
        return ret
      
  # cell test
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      if(v[i][j] == -1):
        continue
      actedges = 0
      actedges += v[i-1][j]
      actedges += v[i+1][j]
      actedges += v[i][j-1]
      actedges += v[i][j+1]
      if(actedges != v[i][j]):
        print("Cell test failed")
        ret = False
        return ret              
  
  # and now I'm starting to wonder whether we need flood test at all?
  # hmm
  # we
  # think, for example, of this 2 x 3 grid
  # 3 . 3
  # 3 . 3
  '''
  
  the following solution:
 • ⎯ •   • ⎯ •
 | 3 |   | 3 |
 •   •   •   •
 | 3 |   | 3 |
 • ⎯ •   • ⎯ •
  would pass by current standards
  even though it's not correct
  
  '''
  
  # so, next idea:
  # we still do a flood fill
  # except, we treat the lines as the walkable path
  # and everythign else as the walls
  # and if there are unvisited lines after
  # well, its incorrect
  
  #print(f"Ground:\n{ground}")
  
  #print("Flood test:")
  
  q = deque()
  # we search until we find an "active cell"
  # ie, a ground with 1
  found:bool = False
  for i in range(0, 2 * n + 1, 1):
    for j in range(0, 2 * m + 1, 1):
      if(ground[i][j] == 1):
        vis[i][j] = 1
        q.append((i,j))
        found = True
        break
    if(found):
      break
    
  #print(f"Starting queue:{q}")
  
  while(len(q) > 0):
    #print(f"Len(q)={len(q)}")
    i, j = q.popleft()
    #print(f"ci={i}, cj={j}")
    
    if(valid(i, j-1) and ground[i][j-1] == 1 and vis[i][j-1] == 0):
      vis[i][j-1] = 1
      q.append((i, j-1))
      
    if(valid(i,j+1) and ground[i][j+1] == 1 and vis[i][j+1] == 0):
      vis[i][j+1] = 1
      q.append((i, j+1))
    
    if(valid(i+1, j) and ground[i+1][j] == 1 and vis[i+1][j] == 0):
      vis[i+1][j] = 1
      q.append((i+1, j))
    
    if(valid(i-1, j) and ground[i-1][j] == 1 and vis[i-1][j] == 0):
      vis[i-1][j] = 1
      q.append((i-1, j))
  
  #print(f"vis=\n{vis}")
      
  for i in range(0, 2 * n + 1, 1):
    for j in range(0, 2 * m + 1, 1):
      if(ground[i][j] != vis[i][j]):
        print("Flood test failed")
        return False 
        
  return True

# initializes filepaths
def initboards():
    # comment
    global base_dir
    #global text_files
    global pregenboardspath
    global resourcespath
    
    if getattr(sys, 'frozen', False):  # running as EXE
      base_dir = os.path.dirname(sys.executable)
    else:
      base_dir = os.path.dirname(os.path.abspath(__file__))
    
    pregenboardspath = os.path.join(base_dir, 'pregenboards')  # folder is in the same directory as main.py
    resourcespath = os.path.join(base_dir, 'resources')
    #text_files = [f for f in os.listdir(pregenboardspath) if f.endswith('.txt')]

# prints the cell values of a standardly structured board    
def printtotal(arr, n, m):
    #print("full=\n")
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

# prints a standardly structured board
def printnumbers(arr, n, m):
  #print("numbers=")
  for i in range(1, 2 * n + 1, 2):
      for j in range(1, 2 * m + 1, 2):
          curr = arr[i][j]
          if(curr == -1):
            curr = '.'
          print(curr, end=" ")
      print(" ")

# reads in a borad from a file
def getboard(startup:bool, source):
    global v
    global sol
    global n
    global m
    global solcalc
    global nosol
  
    # kinyitunk egy random file-t a pregenboards-bol
    
    #random_file = random.choice(text_files)
    
    # de amugy megse
    
    content = 1
    
    if(startup):
      with open(os.path.join(pregenboardspath, startingfile), 'r') as file:
        content = file.read()
    else:
      with open(source, 'r') as file:
        content = file.read()
    #print(f"File:{random_file}")
    #print(content)
    
    parts = iter(content.split())
    n = int(next(parts))
    m = int(next(parts))
    solcheck = int(next(parts))
    v = np.zeros((2 * n +1, 2 * m + 1), dtype=np.int32)
    sol = np.zeros((2 * n + 1, 2 *m + 1), dtype=np.int32)
    solcalc = True
    nosol = False
    
    if(solcheck == 1):
      solcalc = True
    else:
      solcalc = False
    
    print(f"n={n},m={m}")
    
    for i in range(1, 2 * n + 1, 2):
        for j in range(1, 2 * m + 1, 2):
            #print(f"i={i},j={j}, v[]=", end=" ")
            curr = next(parts)
            if(curr == '.' or curr == -1):
              v[i][j] = -1
            else:
              v[i][j] = curr
            sol[i][j] = v[i][j]
            #print(v[i][j])
     
    if(solcalc == True):       
      for i in range(0, 2 * n + 1):
          jstart = 0
          if(i % 2 == 0):
            jstart = 1
          
          for j in range(jstart, 2 * m + 1, 2):
            sol[i][j] = next(parts)
          
    printnumbers(v, n, m)
    #if(solcalc):
    #   printtotal(sol, n, m)

# starts a new game, in which the board is pregenerated
def newgame_pregen(winx, winy):
  root = tk.Tk()
  root.withdraw()
  root.geometry(f"+{winx}+{winy}")
  root.update()
  
  file_path = filedialog.askopenfilename(
        title="Select a text file",
        initialdir=pregenboardspath,
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
  )
  
  root.destroy()
  
  getboard(False, file_path)
  pg.quit()
  initwindow()

# starts a new game in which a new board will be generated
def newgame_genboard(newn:int, newm:int):
  start = time.time()
  genboard(newn, newm)
  end = time.time()

  print(f"Took {end-start} seconds")
  
  pg.quit()
  initwindow()

# starts a new game in which the board will be initialized based on a Loopy-style ID
def newgame_insertboard(input:str):
  global v
  global sol
  global n
  global m
  global solcalc
  global nosol
  
  # feltetelezzuk, hogy n, m < 100
  # kb. ~40 x 40 a max amit tud renderelni
  # marmint tud tobbet is, de akkor a click detection kezdi feladni
  
  # tehat
  
  nstr:str = ""; mstr:str = ""
  
  xyet:bool = False
  tyet:bool = False
  
  j:int = 0
  
  for i in range(0, len(input), 1):
    # csak megkeressuk az n, m-et, eloszor
    if(input[i] == "x"):
      xyet = True
    if(input[i] == 't'):
      tyet = True
      
    if(input[i] == ':'):
      j = i+1
      break
    
    if(xyet == False):
      nstr += input[i]
    elif(tyet == False and input[i] != 'x'):
      mstr += input[i]
  
  input = input[j:]
  
  print(f"n={mstr}, m={nstr}")
  print(input)
  
  solcalc = False
  nosol = False
  
  n = int(mstr)
  m = int(nstr) # this is done because it is width * height in the loopy format
  
  v = np.zeros((2 * n + 1 , 2 * m + 1), dtype=np.int32)
  sol = np.zeros((2 * n + 1 , 2 * m + 1), dtype=np.int32)
  
  k:int = 0 # ignore current char counter
  
  parts = iter(input)        
  print(f"n={n},m={m}")
  
  for i in range(1, 2 * n + 1, 2):
      for j in range(1, 2 * m + 1, 2):
          #print(f"i={i},j={j}, v[]=", end=" ")
          
          #print(f"i={i},j={j}")
          #print(f"k={k}")
          
          if(k > 0):
            v[i][j] = -1
            sol[i][j] = -1
            k -= 1
            continue
          
          curr = next(parts)
          
          #print(f"curr={curr}")
          
          if(str.isalpha(curr)):
            k += ord(curr) - ord('a')
            v[i][j] = -1
            sol[i][j] = -1
          else:
            v[i][j] = int(curr)
          sol[i][j] = v[i][j]
          #print(v[i][j])
  
  if(solcalc == True):       
    for i in range(0, 2 * n + 1):
        jstart = 0
        if(i % 2 == 0):
          jstart = 1
        
        for j in range(jstart, 2 * m + 1, 2):
          sol[i][j] = next(parts)
        
  printnumbers(v, n, m)
  if(solcalc):
    printtotal(sol, n, m)
    
  pg.quit()
  initwindow()

# tests generation/solution speed
def automatedtesting():
  # gyors teszteles a generalas gyorsasagara
    testfor:int = 1000
    ntest:int = 5
    soltest:bool = True # if false, it test generation time
    # if true, it tests solution time
    for i in range(0, testfor):
      
      if(soltest == False):    
        start = time.time()
        genboard(ntest, ntest)
        end = time.time()

        print(f"Test {i+1}:Took {end-start} seconds")
        with open("out.txt", "a") as f:
          if(i == 0):
            f.seek(0)
            f.truncate()
          f.write(f"{end-start} \n")
      else:
        start = time.time()
        genboard(ntest, ntest)
        end = time.time()
        print(f"Test {i+1}: Generation took {end-start} seconds")
        
        start = time.time()
        calculatesolution()
        end = time.time()

        print(f"Test {i+1}: Solution took {end-start} seconds")
        with open("out.txt", "a") as f:
          if(i == 0):
            f.seek(0)
            f.truncate()
          f.write(f"{end-start} \n")
          if((end-start) > 60):
            with open("newb.txt", "a") as f:
              f.write(f"{ntest} {ntest}\n")
              for i in range(1, 2 * n + 1, 2):
                for j in range(1, 2 *  m + 1, 2):
                  f.write(f"{v[i][j]} ")
                f.write("\n")
              f.write("\n")
          
# starts the program
def main():
    # test comment

    # kinyitunk egy windowt
    # es felrajzoljuk
    global auttesting
    
    # set working directory to script location
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    
    #print("Current working dir:", os.getcwd())
    #print("Font exists:", os.path.exists("resources/comicsans.ttf"))
    
    initboards()
    
    getboard(True, "dummy")
    
    if(auttesting):
      automatedtesting()     
      return
    
    initwindow()
    
    pg.quit()

# calculates the solution to the current board using a SAT solver
def calculatesolution():
  global n
  global m
  global v
  global sol
  
  global nosol
  
  # oke, szoval eloszor ezt a modszert fogom alkalmazni
  # ha nem jon ossze, akkor meg finomitok rajta
  # fo forrasok:
  # modszer: https://www.dougandjean.com/slither/howitsolves.html
  # altalanos overview: https://esolangs.org/wiki/User:Hakerh400/How_to_solve_Slitherlink_using_SAT_solver
  # a PySAT library altal bocsatott Glucose 4.2.1 solver segitsegevel

  # oke, szoval legeloszor szuksegunk van egy bijektiv lekepezesre
  # ahol minden edge kap egy egyedi id-t
  # c++-ban kifejezve:
  # map<pair<ll,ll>, ll> ahol egy megadott (i,j)-re kiadja, hogy milyen indexu edge van ott
  # illetve egy map<ll,pair<ll,ll>> ami megadja, hogy az adott indexu edge melyik koordinatakert felel

  cordtoindex = {}
  indextocord = {}
  
  counter:int = 1
  
  g = Glucose42()
  
  globcnf = CNF()
  
  vpool = IDPool()
  
  skippoint:bool = False
  skipcell:bool = False
  
  # standard edge bejaras
  for i in range(0, 2 * n + 1, 1):
    jstart = 0
    if(i % 2 == 0):
      jstart = 1
    for j in range(jstart, 2 * m +1, 2):
      cordtoindex[(i,j)] = vpool.id((i,j))
      indextocord[cordtoindex[(i,j)]] = (i,j)
      #print(f"edge[{i}][{j}]={cordtoindex[(i,j)]}")
  
  # point clauses
  for i in range(0, 2 * n + 1, 2):
    for j in range(0, 2 * m + 1, 2):
      if(skippoint):
        continue
      actedges = 0
      edg = []
      if(valid(i, j-1)):
        edg.append(vpool.id((i,j-1)))
        actedges += 1
      if(valid(i,j+1)):
        edg.append(vpool.id((i,j+1)))
        actedges += 1
      if(valid(i+1, j)):
        edg.append(vpool.id((i+1,j)))
        actedges += 1
      if(valid(i-1, j)):
        edg.append(vpool.id((i-1,j)))
        actedges += 1
      #print(f"For point at i={i},j={j}, edges around it are:{edg}")
      
      # alright, so I have seven clauses, one of which must be true
      # which means I need to declare them all in the same add_clause
      # those seven clauses are:
      # all possible 2-way combinations of edges, plus the negative case
      # so basically i'd have
      '''
      add_clause():
        edg[0], edg[1], -edg[2], -edg[3] OR
        .
        .
        .
        -edg[0], -edg[1], -edg[2], -edg[3]
        
      illetve kevesebb kisebb esetekben
      '''
      if(actedges == 2):
        # 2 cases : both or nothing
        A = vpool.id(counter); counter += 1 # 1,2
        B = vpool.id(counter); counter += 1 # none
        
        localclauses = [A, B]
        
        # 1, 2
        globcnf.append([-A, edg[0]])
        globcnf.append([-A, edg[1]])
        globcnf.append([-edg[0], -edg[1], A])
        
        # -1, -2
        globcnf.append([-B, -edg[0]])
        globcnf.append([-B, -edg[1]])
        globcnf.append([edg[0], edg[1], B])
        
        cnf = CardEnc.equals(lits=localclauses, bound=1, encoding=1, vpool=vpool)
        for clause in cnf.clauses:
            globcnf.append(clause)
      
      elif(actedges == 3):
        # 4 cases : 3 combinations (1,2), (1,3), (2,3) plus null
        
        A = vpool.id(counter); counter += 1 # (1,2)
        B = vpool.id(counter); counter += 1 # (1,3)
        C = vpool.id(counter); counter += 1 # (2,3)
        D = vpool.id(counter); counter += 1 # (none)
        
        localclauses = [A, B, C, D]
        
        # 1, 2, -3
        globcnf.append([-A, edg[0]])
        globcnf.append([-A, edg[1]])
        globcnf.append([-A, -edg[2]])
        globcnf.append([-edg[0], -edg[1], edg[2], A])
        # so now A is only true if all four are true
        # add negations as needed, but this template works
        
        # 1, -2, 3,
        globcnf.append([-B, edg[0]])
        globcnf.append([-B, -edg[1]])
        globcnf.append([-B, edg[2]])
        globcnf.append([-edg[0], edg[1], -edg[2], B])
        
        # -1, 2, 3
        globcnf.append([-C, -edg[0]])
        globcnf.append([-C, edg[1]])
        globcnf.append([-C, edg[2]])
        globcnf.append([edg[0], -edg[1], -edg[2], C])
        
        # -1, -2, -3
        globcnf.append([-D, -edg[0]])
        globcnf.append([-D, -edg[1]])
        globcnf.append([-D, -edg[2]])
        globcnf.append([edg[0], edg[1], edg[2], D])
        
        cnf = CardEnc.equals(lits=localclauses, bound=1, encoding=1, vpool=vpool)
        for clause in cnf.clauses:
            globcnf.append(clause)
      
      elif(actedges == 4):
        # 7 cases: 6 combinations, 1 null
        A = vpool.id(counter); counter += 1 # (1,2)
        B = vpool.id(counter); counter += 1 # (1,3)
        C = vpool.id(counter); counter += 1 # (1,4)
        D = vpool.id(counter); counter += 1 # (2,3)
        E = vpool.id(counter); counter += 1 # (2,4)
        F = vpool.id(counter); counter += 1 # (3,4)
        G = vpool.id(counter); counter += 1 # (none)
        
        localclauses = [A, B, C, D, E, F, G]
        
        # so for each of these 
        # I'll have to do
        '''
          CNF Encoding for A = X ∧ Y ∧ Z ∧ V:

          To represent this in CNF, we break it into implications:
          1. If A is true, then all of X, Y, Z, V must be true:

          A → X → ¬A ∨ X

          A → Y → ¬A ∨ Y

          A → Z → ¬A ∨ Z

          A → V → ¬A ∨ V

          2. If all of X, Y, Z, V are true, then A must be true:

          (X ∧ Y ∧ Z ∧ V) → A → ¬X ∨ ¬Y ∨ ¬Z ∨ ¬V ∨ A
        '''
        # how fun
        # let's get to it, I suppose
        
        # 1, 2, -3, -4
        globcnf.append([-A, edg[0]])
        globcnf.append([-A, edg[1]])
        globcnf.append([-A, -edg[2]])
        globcnf.append([-A, -edg[3]])
        globcnf.append([-edg[0], -edg[1], edg[2], edg[3], A])
        
        # 1, -2, 3, -4
        globcnf.append([-B, edg[0]])
        globcnf.append([-B, -edg[1]])
        globcnf.append([-B, edg[2]])
        globcnf.append([-B, -edg[3]])
        globcnf.append([-edg[0], edg[1], -edg[2], edg[3], B])
        
        # 1, -2, -3, 4
        globcnf.append([-C, edg[0]])
        globcnf.append([-C, -edg[1]])
        globcnf.append([-C, -edg[2]])
        globcnf.append([-C, edg[3]])
        globcnf.append([-edg[0], edg[1], edg[2], -edg[3], C])
        
        # -1, 2, 3, -4
        globcnf.append([-D, -edg[0]])
        globcnf.append([-D, edg[1]])
        globcnf.append([-D, edg[2]])
        globcnf.append([-D, -edg[3]])
        globcnf.append([edg[0], -edg[1], -edg[2], edg[3], D])
        
        # -1, 2, -3, 4
        globcnf.append([-E, -edg[0]])
        globcnf.append([-E, edg[1]])
        globcnf.append([-E, -edg[2]])
        globcnf.append([-E, edg[3]])
        globcnf.append([edg[0], -edg[1], edg[2], -edg[3], E])
        
        # -1, -2, 3, 4
        globcnf.append([-F, -edg[0]])
        globcnf.append([-F, -edg[1]])
        globcnf.append([-F, edg[2]])
        globcnf.append([-F, edg[3]])
        globcnf.append([edg[0], edg[1], -edg[2], -edg[3], F])
        
        # -1, -2, -3, -4
        globcnf.append([-G, -edg[0]])
        globcnf.append([-G, -edg[1]])
        globcnf.append([-G, -edg[2]])
        globcnf.append([-G, -edg[3]])
        globcnf.append([edg[0], edg[1], edg[2], edg[3], G])
        
        # final conjuction
        cnf = CardEnc.equals(lits=localclauses, bound=1, encoding=1, vpool=vpool)
        for clause in cnf.clauses:
            globcnf.append(clause)      
               
  # cell clauses
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      if(v[i][j] == -1 or skipcell):
        continue
      edgeindexes = []
      edgeindexes.append(cordtoindex[(i,j-1)])
      edgeindexes.append(cordtoindex[(i,j+1)])
      edgeindexes.append(cordtoindex[(i-1,j)])
      edgeindexes.append(cordtoindex[(i+1,j)])
      
      #print(f"For cell at i={i},j={j}, edges around it are:{edgeindexes}")
      #print(f"v[i][j]={v[i][j]}")
      
      cnf = CardEnc.equals(lits=edgeindexes, bound=v[i][j], encoding=1, vpool=vpool)
      
      #print("Adding clauses:\n")
      for clause in cnf.clauses:
        globcnf.append(clause)
        #print(clause)
  
  #print(f"Vars:\n{g.nof_vars()}\nClauses:\n{g.nof_clauses()}")
        
  #globcnf.to_file("test.cnf")      

  exhausted:bool = False

  temp = Glucose42()

  for clause in globcnf:
    temp.add_clause(clause)

  totalsolcounter:int = 1

  while(exhausted == False):
    
    #print(f"Current solution:{totalsolcounter}")
    
    solvstat:bool = temp.solve()
    
    if(solvstat == False):
      print("No possible solution exists")
      exhausted = True
      nosol = True
      return
      
    model = temp.get_model()

    for lit in model:
      var_id = abs(lit)
      name = vpool.obj(var_id)
      if name is not None:
          value = lit > 0
          #print(f"{name} = {value}")
          if var_id in indextocord:
            ci, cj = indextocord[var_id]
            sol[ci][cj] = value
    
    ground = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
    vis = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
    
    # building ground
    for i in range(0, 2 * n + 1, 2):
      for j in range(0, 2 * m + 1, 2):
        actedges = 0
        if(valid(i, j-1)):
          actedges += sol[i][j-1]
          ground[i][j-1] = sol[i][j-1]
        if(valid(i,j+1)):
          actedges += sol[i][j+1]
          ground[i][j+1] = sol[i][j+1]
        if(valid(i+1, j)):
          actedges += sol[i+1][j]
          ground[i+1][j] = sol[i+1][j]
        if(valid(i-1, j)):
          actedges += sol[i-1][j]
          ground[i-1][j] = sol[i-1][j]
        
        if(actedges == 0):
          ground[i][j] = 0;
        if(actedges == 2):
          ground[i][j] = 1
        
    #flood test
    
    # at each active cell, we start a BFS
    # and afterwards, negate the loop
    # we also keep a counter
    # if, at the end, there was only one loop
    # we return the solution
    # otherwise, the loop continues
    
    q = deque()
    loopcounter:int = 0
    for i in range(0, 2 * n + 1, 1):
      for j in range(0, 2 * m + 1, 1):
        if(ground[i][j] == 1 and vis[i][j] == 0):
          vis[i][j] = 1
          q.append((i,j))
          loopcounter += 1
          containededges = []
          while(len(q) > 0):
            #print(f"Len(q)={len(q)}")
            i, j = q.popleft()
            if(sol[i][j] == 1):
              containededges.append(cordtoindex[(i,j)])
            #print(f"ci={i}, cj={j}")
            
            if(valid(i, j-1) and ground[i][j-1] == 1 and vis[i][j-1] == 0):
              vis[i][j-1] = 1
              q.append((i, j-1))
              
            if(valid(i,j+1) and ground[i][j+1] == 1 and vis[i][j+1] == 0):
              vis[i][j+1] = 1
              q.append((i, j+1))
            
            if(valid(i+1, j) and ground[i+1][j] == 1 and vis[i+1][j] == 0):
              vis[i+1][j] = 1
              q.append((i+1, j))
            
            if(valid(i-1, j) and ground[i-1][j] == 1 and vis[i-1][j] == 0):
              vis[i-1][j] = 1
              q.append((i-1, j))
          
          neg_clause = [-lit for lit in containededges]
          #globcnf.append(neg_clause)
          temp.add_clause(neg_clause)
    
    if(loopcounter == 1):
      printtotal(sol, n, m)
      return
    else:
      totalsolcounter += 1
      print(f"{loopcounter} loops found, retrying")
      #return

# generates a new board of given (n, m) dimensions
def genboard(newn:int, newm:int):
  global n
  global m
  global v
  global sol
  global solcalc
  global nosol
  
  n = newn
  m = newm
  
  solcalc = True
  nosol = False
  
  v = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  sol = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  
  # valahogy ez még nehezebbnek tűnik, mint a solver
  # mert ott ugye, szigoruan meg van hatarozva, hogy mi a helyes megoldas
  # itt viszont erzesre megy
  # es az a problema, hogy annak ellenere, hogy mar vagy 40 oraja programozom ezt
  # egy csoppet sem lettem jobb magaban a slitherlink jatekban
  
  # na jo
  # tehat alap otlet:
  # valasztunk egy cellat valahol kozeptajt
  # olyan ~ 35%-tol 65%-ig
  # es onnan egy flood fill, felturbozva egy kicsi randomsaggal/heurisztikaval?
  # es akkor a szinezes hatara menten beallitjuk a korvanalt/szamokat, aztan kitorolunk valamennyit
  # a szamok ~70%-at?
  
  # nem tartom olyan fontosnak, hogy az elkeszult puzzle-nek szigorúan egy helyes megoldása legyen
  # ami megkönnyíti az életemet 
  
  # oke, az nem jott be
  # masodik nekifutas:
  # https://liamappelbe.medium.com/how-to-generate-slither-link-puzzles-6c65510b2ba1
  # rajzolunk egy beszinezett teglalapot ugy kozeptajt
  # es igyekszunk a "wigglyness-t" novelni minden lepesben
  
  # na jo
  # tegnap azzal elpazaroltam ot orat
  # tehat most itt az ido, hogy megprobaljunk egyfajta cellular automata-t
  # hogy generaljunk egy blob-ot
  
  flood = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  comp = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32) # grafelmelet
  dist = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int16)
  
  # tehat betoltjuk az egesz grid-et
  # es kivulrol inditunk u.n. "incursion"-oket
  # amikkel kivagunk szeleteket belole
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      flood[i][j] = 1 # tudom, hogy tudnek visszafele dolgozni, hogy felcserelem a 0-1 jelenteset
      # de nem akarok
  
  # szoval
  # kitalaljuk elore, hogy mekkorak lesznek a beturemkedesek
  # es mindig amikor elkezdunk egyet, akkor mar elore tuddjuk a meretet
  # pelda egy jo elosztasra, amit a loopy-val generaltam:
  # 10x10-es
  # 2/3/3/3 incursion per oldal
  # mereteik: negy 1-es, harom 2-es, egy 4-es, egy 7-es, egy 9-es, 
  # tehat osszesen kb a felet kene lefedni
  
  # tehat 36 elcellara, 11 incursionpoint kell
  # kb ~3 cellankent 1 incursionpoint kell
  
  # hmmmmmm
  # kozben generaltam egy szep 9x9-est
  # a sajat kodom altal
  # ami szinten eleg szep
  # viszont ennek az elosztasa elegge kulonbozik: 
  # egy kicsi incursion fent/lent, es ket nagy oldalt
  # ezek ugy jobban tetszenek
  # tehat inkabb kevesebb > nagyobb
  # vagy valahogy preferalja azt, hogy nagyon nagy vagy nagyon kicsi ertekeket generaljon a lehetseges tartomanybol
  
  compctr:int = 0
  
  toflood = random.randint(math.ceil((n * m)/2), math.ceil((n * m) * 3/4))
  # somewhere between 4 and 8
  # so one for each side
  # hmmm
  # one per side for 5
  # two per side for 10, etc
  # tehat visszaterve az elozohoz, kb 4 szelso cellankent egy
  edgecells = 2 * n + 2 * (m-2)
  
  intrusions = math.floor(0.66 * random.randint(math.floor(edgecells/5), 2 * math.floor(edgecells/5)))
  
  values = np.random.dirichlet(np.ones(intrusions)) * toflood # gives back floats, but we can mitigate that
  
  #random.shuffle(values)
  values.sort()
  sizes = deque()
  for val in reversed(values):
    sizes.append(math.ceil(val))
  
  #print(f"Cells to flood={toflood}")
  #print(f"Intrusions={intrusions}")
  #print(f"Areas={values}")
  
  # legeneralunk egy kezdopontot mind a negy oldalra
  # aztan pedig ujra generalunk, amig kifogyunk a generalando intrusionokbol
  # (aztan ha kesobb egy intrusionpoint mar el van arasztva, ujrageneraljuk)
  
  startq = [(1, 0), (2*n - 1, 0), (0, 1), (0, 2 * m - 1)]
  nextq = []
  
  random.shuffle(startq)
  
  bigq = deque()
  
  for i in range(0, intrusions):
    ci, cj = startq.pop()
    
    nextq.append((ci, cj))
    if((len(startq) == 0)):
      random.shuffle(nextq)
      for x in nextq:
        startq.append(x)
      nextq.clear()
    
    if(cj == 0):
      cj = random.randint(0, m-1)
      cj = 1 + 2 * cj
    if(ci == 0):
      ci = random.randint(0, n-1)
      ci = 1 + 2 * ci
    
    bigq.append((ci, cj))
  
  floodedcells:int = 0
  
  aroundedgecurrent = 1 
  #ari = 1; arj = 1
  
  totaltries:int = 0
    
  totalfailures = 0
  maxfailures = 20  
    
  while (toflood - floodedcells > 0 and totaltries <= intrusions * 5 and totalfailures < maxfailures * 2):
          i = 1; j = 1
          
          if(len(bigq) > 0):
            i, j = bigq.popleft()
          else:
            # go around until we find a possible insertion-point
            templist = []
            if(aroundedgecurrent == 1):
              ari = 1
              for arj in range(3, 2 * m - 3):
                if(flood[ari][arj] == 1 and flood[ari][arj-2] == 1 and flood[ari][arj + 2] == 1):
                  templist.append((ari, arj))
                
            elif(aroundedgecurrent == 2):
              arj = 2 * m - 1
              for ari in range(3, 2 * n - 3):
                if(flood[ari][arj] == 1 and flood[ari-2][arj] == 1 and flood[ari+2][arj] == 1):
                  templist.append((ari, arj))
            elif(aroundedgecurrent == 3):
              ari = 2 * n - 1
              for arj in range(3, 2 * m - 3):
                if(flood[ari][arj] == 1 and flood[ari][arj-2] == 1 and flood[ari][arj + 2] == 1):
                  templist.append((ari, arj))
            elif(aroundedgecurrent == 4):
              arj = 1
              for ari in range(3, 2 * n - 3):
                if(flood[ari][arj] == 1 and flood[ari-2][arj] == 1 and flood[ari+2][arj] == 1):
                  templist.append((ari, arj))
              
            aroundedgecurrent += 1
            if(aroundedgecurrent > 4):
              aroundedgecurrent -= 4
            
            if(len(templist) == 0):
              totaltries += 1
              totalfailures += 1
              continue
            else:
              i, j = templist[random.randint(0, len(templist) - 1)]
            
          totaltries += 1
          
          #print(f"\nAt edge, i={i}, j={j}")
          #print(f"In human terms,i={math.floor((i-1)/2)}, j={math.floor((j-1)/2)}")
    
          if(flood[i][j] == 0):
            # already flooded
            # for the moment, skip
            totalfailures += 1
            #print(f"Already flooded ;(")
            continue
          
          if(len(sizes) > 0):
            fsize = sizes.popleft()
          else:
            rem = toflood - floodedcells
            fsize = random.randint(math.ceil(rem/2), math.ceil(rem * 1.25))
          
          startsize = fsize
          
          #print(f"Currcomp={compctr+1}")
          #print(f"Size to be={fsize}")
          compctr += 1
          # edges: top=1, left=2, down=3, right=4, clockwise
          # if the edge of the current cell isn't equal to its starting edge, 
          
          ideali = 0 # "ideal" coordinates, as in, I want the inner "cave" to bloat out here
          idealj = 0
          
          startedge = 0
          if(i == 1):
            startedge = 1
            ideali = 1 + (2 * n - 2) * 0.4
            idealj = 1 + (2 * m - 2) * 0.5
          elif(j == 2 * m - 1):
            startedge = 2
            ideali = 1 + (2 * n - 2) * 0.5
            idealj = 1 + (2 * m - 2) * 0.6
          elif(i == 2 * n - 1):
            startedge = 3
            ideali = 1 + (2 * n - 2) * 0.6
            idealj = 1 + (2 * m - 2) * 0.5
          elif(j == 1):
            startedge = 4
            ideali = 1 + (2 * n - 2) * 0.5
            idealj = 1 + (2 * m - 2) * 0.4
          
          #print(f"startedge={startedge}")
          
          q = SortedList()
          q.add((1, i, j)) # weight, i, j
          # larger weight to those more inwards/those with more unfamiliar neighbors
          # weight also depends on place in ortho
          # and distance from start
          dist[i][j] = 0
          while(len(q) > 0 and fsize > 0):
            danger:bool = False
            
            cw, ci, cj = q.pop(-1) # current-weight (unimportant), current-i, current-j
            #print(f"ci={ci}, cj={cj}")
            comp[ci][cj] = compctr
            flood[ci][cj] = 0
            fsize -= 1
            ortho = []
            # ortho is carefully designed: first, is the opposite direction from where we're coming
            # then, left or right are shuffled (or up and down)
            # then, and only then, the backwards direction
            if(startedge == 1):
              ortho.append((1, 0))
              if(random.randint(1,2) == 1):
                ortho.append((0, -1))
                ortho.append((0, 1))
              else:
                ortho.append((0, 1))
                ortho.append((0, -1))
              ortho.append((-1, 0))
            elif(startedge == 2):
              ortho.append((0, -1))
              if(random.randint(1,2) == 1):
                ortho.append((1, 0))
                ortho.append((-1, 0))
              else:
                ortho.append((-1, 0))
                ortho.append((1, 0))
              ortho.append((0, 1))
            elif(startedge == 3):
              ortho.append((-1, 0))
              if(random.randint(1,2) == 1):
                ortho.append((0, -1))
                ortho.append((0, 1))
              else:
                ortho.append((0, 1))
                ortho.append((0, -1))
              ortho.append((1, 0))
            elif(startedge == 4):
              ortho.append((0, 1))
              if(random.randint(1,2) == 1):
                ortho.append((1, 0))
                ortho.append((-1, 0))
              else:
                ortho.append((-1, 0))
                ortho.append((1, 0))
              ortho.append((0, -1))
            
            maxorthoweight = 200 
            maxdistweight = 200
            
            maxrandmin = 50
            maxrandmax = 150
             
            orthoweight = [1, 0.9, 0.8, 0.7]
            posexp = [] # possible expansions, only added if currently considered cell fits
            jw = 0
            for dir in ortho:
              
              hi, hj = dir # here-i, here-j
              hi = ci + hi * 2
              hj = cj + hj * 2
              
              hw = 0
              # weight is influenced by: 
              # place in ortho
              # distance from ??? 
              # heuristic? heatmap? something something create big pockets inside
              # prefer spaces which are like 40% of m or n
              # and of course, a healthy dose of randomness
              
              distfromperfecti = abs(hi - ideali)
              distfromperfectj = abs(hj - idealj)
              
              distweight = maxdistweight - (distfromperfecti + distfromperfectj)
              
              randomweight = random.randint(maxrandmin, maxrandmax)
              
              hw = math.floor(maxorthoweight * orthoweight[jw]) + distweight + randomweight
              
              if(valid(hi, hj) == False):
                continue
              
              if(flood[hi][hj] == 0 and comp[hi][hj] != comp[ci][cj]):
                danger = True
                break 
              
              if(flood[hi][hj] == 1):
                posexp.append((hw, hi, hj))
                
              jw += 1
            
            # masodik feltetel: ha van olyan diagonalis, amelyik csak 0 de nem egy kompban van
            # akkor is rossz
            # modositas: ha van egy diagonalis
            # ahol legalabb az egyik hozza tartozo cella nem nulla
            diag = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dir in diag:
              hi, hj = dir # here-i, here-j
              hi = ci + hi * 2
              hj = cj + hj * 2
              
              if(valid(hi, hj) == False):
                continue
              
              if(flood[hi][hj] == 0 and comp[hi][hj] != comp[ci][cj]):
                danger = True
                break
              
              posdang = False
              
              if(flood[hi][hj] == 0):
                posdang = True
                if(valid(hi, cj) and flood[hi][cj] == 0):
                  posdang = False
                if(valid(ci, hj) and flood[ci][hj] == 0):
                  posdang = False
                
              if(posdang):
                danger = True
                          
            # hogyha a szelen van
            # de nem ugyanazon a szelen ahonnan kezdte
            # az is bajos
            
            curredge = 0
            if(ci == 1):
              curredge = 1
            elif(cj == 2 * m - 1):
              curredge = 2
            elif(ci == 2 * n - 1):
              curredge = 3
            elif(cj == 1):
              curredge = 4
            
            #print(f"Curredge={curredge}")
            
            if(curredge != 0 and curredge != startedge):
              danger = True
            
            # tovabbi kiegeszites: ha a szelen van,
            # akkor kotelezoen kell legyen mellette egy masik cella, amelyik a szelen van
            # (es nullas, termeszetesen)
            
            atleast = True
            
            if(curredge != 0):
              atleast:bool = False
              for dir in ortho:     
                hi, hj = dir # here-i, here-j
                hi = ci + hi * 2
                hj = cj + hj * 2
                
                if(valid(hi, hj) == False):
                  continue
                
                if(hi == 1 or hi == 2 * n - 1 or hj == 1 or hj == 2 * m - 1): # if on-edge
                  if(flood[hi][hj] == 0):
                    atleast = True
                    break
            
            if(ci == i and cj == j):
              atleast = True
            
            if(atleast == False):
              danger = True
            
            #print(f"Danger?={danger}") 
            
            if(danger == True):
              flood[ci][cj] = 1
              fsize += 1
            else: 
              for nw in posexp:
                q.add(nw)
                hw, hi, hj = nw
                dist[hi][hj] = dist[ci][cj] + 1
          
          if(startsize - fsize >= 3):
            sizes.append(startsize)
            floodedcells += startsize - fsize       
  
  # na es akkor egy par finomitas
  # ha van egy cella, ami egyedul egy, es korulotte mind zerosok vannak
  # azt szepen atallitjuk
  
  # es majd azutan lefuttattjuk a flood-check-et
  # ami alapjan ujrageneralja, ha meg mindig vannak kulonallo szigetek
  
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      if(flood[i][j] == 0):
        continue;
      sameo = 0 # same, orthogonally
      # if there is none, but it is still active
      # we'll just quietly turn this cell off
      
      ortho = [(0, -1), (0, 1), (1, 0), (-1, 0)]
      for dir in ortho:
        ci, cj = dir
        ci = i + 2 * ci
        cj = j + 2 * cj
        
        if(valid(ci, cj) and flood[ci][cj] == 1):
          sameo += 1
      
      if(sameo == 0):
        flood[i][j] = 0
  
  # illetve egy apro "wiggliness increase"
  # a blogposzt alapjan, amire a masodik megoldas alapult
  # vesszuk a mar meghuzott vonalat, es ahol biztosan lehet
  # pl, a szelen ahol nincs semmi bemelyedes
  # vagy ahol van egy "fal", kb
  # ott is valtjuk a szint
  
  #print("Pre-wiggle:")
  #printnumbers(flood, n, m)
  
  maxwiggleincrease = 3 # how many times we loop through the table to try and increaase wiggliness
  
  maxwiggleincrease -= math.floor((n * m)/1000)
  
  for w in (0, maxwiggleincrease):
    for i in range(3, 2 * n - 1, 2): # a szeleket kihagyjuk
      for j in range(3, 2 * m - 1, 2): # ez igazabol inkabb csak kisebb tablaknal latszik meg
        if(flood[i][j] == 1):
          continue
        # ket eset van amit itt lekezelunk
        # 0 0 0
        # 0 0 0
        # 1 1 1, es szimmetrikusai
        
        # illetve
        # 1 0 0
        # 1 0 0
        # 1 1 1, es szimmetrikusat
        # a szeleket kihagyjuk
        
        # mindket esetben, a kozepso cella az, amelyiket epp nezunk a loopban'
        
        # mivel mar elegge ki vagyok faradva
        # elegge kecsegteto, hogy egyszeruen bruteforcal lekezeljem mindket esetet
        # oh well
        # akkor legyen
        
        switch:bool = False
        
        status:str = ""
        for ci in range(-2, 2 + 1, 2):
          for cj in range(-2, 2 + 1, 2):
            hi = i + ci
            hj = i + cj
            status += str(flood[hi][hj])
        
        validconfs = ["000000111", "111000000", "100100100", "001001001", "100100111", "001001111", "111100100", "111001001"]
        for conf in validconfs:
          if(status == conf):
            switch = True
            break
        
        randmax = 1
        
        if(switch and random.randint(1, randmax) == 1):
          #print(f"At i={i},j={j}")
          #print(f"Alt i={math.floor((i -1)/2)}, j={math.floor((i-1)/2)}")
          #print(f"Status={status}")
          flood[i][j] = 1         
  # wiggliness-increase turned out to not work
  # or at least, it's very buggy
  # it increases loading-times by a LOT
  # ruining a lot of tables
  # but it also produces pretty nice ones, so eh, 50% on where I'll leave it
  
  #print(f"Floodedcells={floodedcells}")
  #print(f"Totaltries={totaltries}, totalfailures={totalfailures}")
  
  #print("Flood res:")
  #printnumbers(flood, n, m)

  # tehat legutolsonak a floodcheck

  singleloop:bool = True

  floodtest = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int32)
  yet:bool = False
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      # get v values
      curr = 0
      if(valid(i-2, j)):
        if(flood[i-2][j] != flood[i][j]):
          curr += 1
          floodtest[i-1][j] = 1
      elif(flood[i][j] == 1):
        floodtest[i-1][j] = 1
        curr += 1
      
      if(valid(i+2, j)):
        if(flood[i+2][j] != flood[i][j]):
          curr += 1
          floodtest[i+1][j] = 1
      elif(flood[i][j] == 1):
        floodtest[i+1][j] = 1
        curr += 1
      
      if(valid(i, j+2)):
        if(flood[i][j+2] != flood[i][j]):
          curr += 1
          floodtest[i][j+1] = 1
      elif(flood[i][j] == 1):
        floodtest[i][j+1] = 1
        curr += 1
        
      if(valid(i, j-2)):
        if(flood[i][j-2] != flood[i][j]):
          curr += 1
          floodtest[i][j-1] = 1    
      elif(flood[i][j] == 1):
        floodtest[i][j-1] = 1
        curr += 1
      
      floodtest[i][j] = curr
      
  if(checkifvalid(floodtest) == False):
    genboard(n, m)
    return
  
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      # get v values
      curr = 0
      v[i][j] = -1
      if(valid(i-2, j)):
        if(flood[i-2][j] != flood[i][j]):
          curr += 1
          sol[i-1][j] = 1
      elif(flood[i][j] == 1):
        sol[i-1][j] = 1
        curr += 1
      
      if(valid(i+2, j)):
        if(flood[i+2][j] != flood[i][j]):
          curr += 1
          sol[i+1][j] = 1
      elif(flood[i][j] == 1):
        sol[i+1][j] = 1
        curr += 1
      
      if(valid(i, j+2)):
        if(flood[i][j+2] != flood[i][j]):
          curr += 1
          sol[i][j+1] = 1
      elif(flood[i][j] == 1):
        sol[i][j+1] = 1
        curr += 1
        
      if(valid(i, j-2)):
        if(flood[i][j-2] != flood[i][j]):
          curr += 1
          sol[i][j-1] = 1    
      elif(flood[i][j] == 1):
        sol[i][j-1] = 1
        curr += 1
      
      # removal rules:
      # if, 0, 75% chance to remove
      # if, 1 or 3, 50% chance
      # if  2, 35%
      
      sol[i][j] = curr
      
      v[i][j] = -1
      
      remove = random.randint(1, 100)
      
      if(curr == 0 and remove <= 65):
        continue
      
      if((curr == 1 or curr == 3) and remove <= 40):
        continue
      
      if(curr == 2 and remove <= 35):
        continue
      
      v[i][j] = curr

  # meg egy run-through
  # ahol sok elem megjelenik, ott egyet-kettot kiszedunk
  # ahol egy sincs, ott megjelenitunk
  
  cq = deque()
  
  for i in range(1, 2 * n + 1, 2):
    for j in range(1, 2 * m + 1, 2):
      
      set:bool = True
      if(v[i][j] == -1):
        set = False
      
      totaround:int = 0
      setaround:int = 0
      samearound:int = 0
      ortho = [(0,1), (0, -1), (1, 0), (-1, 0)]
      for dir in ortho:
        ci, cj = dir
        ci = i + 2 * ci
        cj = i + 2 * cj
        
        if(valid(ci, cj)):
          totaround += 1
          if(v[ci][cj] != -1):
            setaround += 1
          if(v[ci][cj] == v[i][j]):
            samearound += 1
      
      if(set):
        if(totaround == samearound):
          cq.append((-1, i, j))
        elif(totaround == setaround):
          if(random.randint(1, 8) <= 5):
            cq.append((-1, i, j))
      else:
        if(random.randint(1, 3) > 1):
          cq.append((1, i, j))
  
  for change in cq:
    c, ci, cj = change
    if(c == -1):
      v[i][j] = -1
    else:
      v[i][j] = sol[i][j]      

if __name__ == "__main__":
    main()