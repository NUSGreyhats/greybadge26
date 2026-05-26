from adafruit_display_text import label
import displayio
import terminalio
import time

def menu_layout(hw_state, header, text_in):
    main = hw_state["display"].root_group
    try:
        val = main.pop()
    except:
        pass
    
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


import apps.aoc25.prob1.solve as aoc1
def app(hw_state):
    #splashscreen()
    button_b = hw_state["btn_action"][1]
    is_hardcaml = (button_b.value == False)
    header_text = "Advent of Code\n2025" if not is_hardcaml else "Advent of Code\n2025 - Hardcaml"

    text_area = menu_layout(hw_state, header_text, "Part 1 - \nDeinit")
    hw_state["fpga_overlay"].deinit_mode_buttons()
    hw_state["fpga_overlay"].deinit()
    hw_state["fpga_overlay"].jtag_rst.deinit()
    
    text_area = menu_layout(hw_state, header_text, "Part 1 - Setup")
    aoc1.setup(hardcaml=is_hardcaml)
    aoc1.run()
    while (1):
        text_area = menu_layout(hw_state, header_text, "Part 1a - Run")
        aoc1.fp.part_b_enable(0)
        sol = aoc1.run()
        
        text_area = menu_layout(hw_state, header_text, "Part 1a Ans:\n" + str(sol))
        time.sleep(5)
        
        text_area = menu_layout(hw_state, header_text, "Part 1b - Run")
        aoc1.fp.part_b_enable(1)
        sol = aoc1.run()
        
        text_area = menu_layout(hw_state, header_text, "Part 1b Ans:\n" + str(sol))
        time.sleep(5)
        #text_area = menu_layout(hw_state, "Advent of Code\n2025", "Reset Board")
    
    
if __name__ == "__main__":
    import gc 
    import hardware.main as hardware
    import apps
    hw_state = hardware.hw_state
    hw_state["fpga_overlay"].init()
    fpga_buttons = hw_state["fpga_overlay"].set_mode_buttons()
    app(hw_state)