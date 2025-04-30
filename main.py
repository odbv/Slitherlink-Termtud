import pygame as pg
import pygame_gui as pgui
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
from collections import deque
import time

# I have literally zero idea what I'm doing
# én amikor C++ programozónak érzem magam python-ban
# mondtam már, hogy utálom a pythont?

# oké, tehát
# kinyit egy ablakot, es kivalaszt egy random easy slithersnake-t
# de aztan van egy opcio, hogy valasszon egy uj randomat
# vagy hogy az ember beadja a sajatjat

testing:bool = False

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
    global n
    global m
    global v
    global sol
    global solcalc
    
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
    
    background = pg.Surface((width, height))
    background.fill(backgroundcolor)
    foreground = pg.Surface((width, height), pg.SRCALPHA)
    foreground.fill((0,0,0,0))
    foreforeground = pg.Surface((width, height), pg.SRCALPHA)
    foreforeground.fill((0,0,0,0))
    
    clock = pg.time.Clock()
    
    clock.tick(60)
    
    manager = pgui.UIManager((width, height), theme_path=os.path.join(resourcespath, "testtheme.json"))
    
    # minden elemrol kideritjuk, hogy micsoda
    # ha pont vagy szam, muszaj felrajzoljuk
    # ha viszont vonal, akkor csak egy lathatatlant rajzolunk be
    # vagyis egy olyant, ami a hatterszinnel egyenlo ;)
    
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
    
    font = pg.font.Font(os.path.join(resourcespath, "ComicSansMS.ttf"), fontsize)
    
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

    # tehat pg.display.update az objektumonkent mukodik
    # pg.display.flip() baszik rea es ujrarajzol mindent
    
    # tehat egy atlagos loopban, amikor csak toggle-elunk egy elt, akkor nekunk csak display.update kell
    # display.flip csak akkor kell, amikor direkt berajzoljuk az egesz solutiont
    # mondjuk igazabol akkor is mehet az update, kell egy harmadik array ahol a line objecteket taroljuk

    pg.display.flip();

    showsol:bool = False

    showingcorectness:bool = False

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
        if event.type == pg.QUIT:  # This fires when the window close button is clicked
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
          mousepress = True
          mousecords = event.pos
          if(showingcorectness):
            showingcorectness = False
            valid = False
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
              valid:bool = checkifvalid()
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
      
      inactiveedgecolor = (159, 214, 173)
      
      if(showsol):
        if(solcalc == False or testing == True):
          solcalc = True
          start = time.time()
          calculatesolution()
          end = time.time()
          print(f"Took {end-start} seconds")
      
      for i in range(0, 2 * n + 1, 1):
        jstart = 0
        if(i % 2 == 0):
          jstart = 1
        for j in range(jstart, 2 * m +1, 2):
          
          if(showsol):
            if(sol[i][j] == 1):
              pg.draw.rect(screen, (0,0,0), lines[i][j], width=0)
            else:
              pg.draw.rect(screen, inactiveedgecolor, lines[i][j], width=0)
            continue
    
          pg.draw.rect(screen, inactiveedgecolor, lines[i][j], width=0)
          
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
        font = pg.font.Font(os.path.join(resourcespath, "ComicSansMS.ttf"), 100) 
        # ez kurva sketchy
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
        font = pg.font.Font(os.path.join(resourcespath, "ComicSansMS.ttf"), fontsize)
              
      screen.blit(foreforeground, (0,0))
      foreforeground.fill((0,0,0,0))
      manager.update(time_delta)
      manager.draw_ui(screen)
      pg.display.flip()

def valid(i, j) -> bool:
  global n
  global m
  
  if(i >= 0 and j >= 0 and i < 2 * n +1 and j < 2 * m + 1):
    return True
  else:
    return False

def checkifvalid() -> bool:
  
  global n
  global m
  global v
  global sol
  
  # 3 tests:
  # point test : checks for each point: each one must have either 0 or 2 lines attached to it
  # cell test : checks for each cell, whether its neighbouring active edges equals its value
  # flood test : checks whether a flood fill is able to fill the entire grid
  
  ground = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int8)
  vis = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int8)
  
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

def initboards():
    # comment
    global base_dir
    #global text_files
    global pregenboardspath
    global resourcespath
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pregenboardspath = os.path.join(base_dir, 'pregenboards')  # folder is in the same directory as main.py
    resourcespath = os.path.join(base_dir, 'resources')
    #text_files = [f for f in os.listdir(pregenboardspath) if f.endswith('.txt')]
    
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

def getboard(startup:bool, source):
    global v
    global sol
    global n
    global m
    global solcalc
  
    v = np.zeros((1, 1), dtype=np.int8) # reset-eljuk a vektort
    # kinyitunk egy random file-t a pregenboards-bol
    
    #random_file = random.choice(text_files)
    content = 1
    
    if(startup):
      with open(os.path.join(pregenboardspath, "example_3x3.txt"), 'r') as file:
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
    v = np.zeros((2 * n +1, 2 * m + 1), dtype=np.int8)
    sol = np.zeros((2 * n + 1, 2 *m + 1), dtype=np.int8)
    solcalc = True
    
    if(solcheck == 1):
      solcalc = True
    else:
      solcalc = False
    
    print(f"n={n},m={m}")
    
    for i in range(1, 2 * n + 1, 2):
        for j in range(1, 2 * m + 1, 2):
            #print(f"i={i},j={j}, v[]=", end=" ")
            curr = next(parts)
            if(curr == '.'):
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
    if(solcalc):
      printtotal(sol, n, m)

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

def newgame_genboard(newn:int, newm:int):  
  genboard(newn, newm)
  
  pg.quit()
  initwindow()

def newgame_insertboard(input:str):
  global v
  global sol
  global n
  global m
  global solcalc
  
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
  
  n = int(mstr)
  m = int(nstr) # this is done because it is width * height in the loopy format
  
  v = np.zeros((2 * n + 1 , 2 * m + 1), dtype=np.int8)
  sol = np.zeros((2 * n + 1 , 2 * m + 1), dtype=np.int8)
  
  k:int = 0 # ignore current char counter
  
  parts = iter(input)        
  print(f"n={n},m={m}")
  
  for i in range(1, 2 * n + 1, 2):
      for j in range(1, 2 * m + 1, 2):
          #print(f"i={i},j={j}, v[]=", end=" ")
          
          print(f"i={i},j={j}")
          print(f"k={k}")
          
          if(k > 0):
            v[i][j] = -1
            sol[i][j] = -1
            k -= 1
            continue
          
          curr = next(parts)
          
          print(f"curr={curr}")
          
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

def main():
    # kinyitunk egy windowt
    # es felrajzoljuk
    initboards()
    
    getboard(True, "dummy")
    
    initwindow()
    
    pg.quit()

def calculatesolution():
  global n
  global m
  global v
  global sol
  
  # oke, szoval eloszor ezt a modszert fogom alkalmazni
  # ha nem jon ossze, akkor meg finomitok rajta
  # fo forrasok:
  # modszer: https://www.dougandjean.com/slither/howitsolves.html
  # altalanos overview: https://esolangs.org/wiki/User:Hakerh400/How_to_solve_Slitherlink_using_SAT_solver
  # a PySAT library altal bocsatott Glucose 4.2.1 solver segitsegevel

def genboard(newn:int, newm:int):
  global n
  global m
  global v
  global sol
  global solcalc
  
  n = newn
  m = newm
  
  solcalc = True
  
  v = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int8)
  sol = np.zeros((2 * n + 1, 2 * m + 1), dtype=np.int8)

if __name__ == "__main__":
    main()