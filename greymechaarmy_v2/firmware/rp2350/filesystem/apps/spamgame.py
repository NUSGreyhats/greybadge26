import time
import board
    
# What's without the game that got me into electronics ~ Hackin7
from adafruit_display_text import label
import displayio
import terminalio
import time

def menu_layout(hw_state, header, text_in):
    main = hw_state["display"].root_group
    val = main.pop()
    
    header_text_area = label.Label(terminalio.FONT, text=header, color=0xFFFF00,
                            anchor_point=(0.5,0.5), anchored_position=(0,0))
    #header_text_area.x = 0
    header_text_area.y = -20
    ## Menu Text
    text = text_in
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00,
                            anchor_point=(0.5,0.5), anchored_position=(0,0))
    #text_area.x = 0
    text_area.y = 15
    
    # direction = label.Label(terminalio.FONT, text="< >  A/B", color=0xFFFF00,
    #                         anchor_point=(0.5,0.5), anchored_position=(0,0))
    # direction.y = 50
    
    text_group = displayio.Group(scale=2)
    text_group.append(header_text_area) 
    text_group.append(text_area) 
    #text_group.append(direction) 
    main.append(text_group)
    
    text_group.x = 120 
    text_group.y = 120
    return text_area

def spamgame(hw_state):
    #splashscreen()
    text_area = menu_layout(hw_state, "SpamGame", "spam A in 60s")
    time.sleep(5)
    text_area.text = "Go!"
    
    score = 0
    time_start = time.time()
    timediff = 60 - (time.time() - time_start)
    trigger = True
    prevtime = True
    while timediff > 0:
        # Select Code
        if timediff != prevtime:
            text_area.text = f"Score: {score}\nTime: {timediff}"
            text_area.y = 15
        
        if hw_state["btn_action"][0].value == False and prevpress == True:
            score += 1
            text_area.text = f"Score: {score}\nTime: {timediff}"
            text_area.y = 15
        if hw_state["btn_action"][1].value == False:
            return
        prevpress = hw_state["btn_action"][0].value
        prevtime = timediff
        timediff = 60 - (time.time() - time_start)
    menu_layout(hw_state, "SpamGame", f"Times Up!")
    time.sleep(5)
    menu_layout(hw_state, "SpamGame", f"Score: {score}")
    time.sleep(5)

