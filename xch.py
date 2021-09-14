from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
import board
import digitalio
import json
import requests
import adafruit_character_lcd.character_lcd as characterlcd

# Initialise screen characters
lcd_columns = 16
lcd_rows = 2

# Initialise RPi IO 
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d4 = digitalio.DigitalInOut(board.D13)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d7 = digitalio.DigitalInOut(board.D11)
lcd_backlight = digitalio.DigitalInOut(board.D9) # not connected

# Initialise the LCD with class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

# Create custom characters for display
lcd.create_char(0, [0x00, 0x04, 0x04, 0x0E, 0x0E, 0x1F, 0x04, 0x04]) # Arrow up
lcd.create_char(1, [0x00, 0x04, 0x04, 0x1F, 0x0E, 0x0E, 0x04, 0x04]) # Arrow down
lcd.create_char(2, [0x04, 0x04, 0x1F, 0x04, 0x04, 0x00, 0x1F, 0x00]) # +-

lastPrice = 0

def getSavedPrice():
    try:
        with open("data.json", "r") as read_file:
            price_data = json.load(read_file)["priceData"]
            old_price = price_data["lastPrice"]
            print("Fetched last price successfully! $" + str(old_price) + " at " + str(price_data["timeStamp"]))
            return old_price
    except:
         print("Error parsing price data")

def xchPrice():
    try:
        b = requests.get('https://min-api.cryptocompare.com/data/price?fsym=XCH&tsyms=USD')
        price = float(json.loads(b.text)['USD'])
        
        
        # save last known price with time stamp before overwriting, if it's new data
        if not lastPrice == price:
            price_data = { 
                          "priceData": {
                            "lastPrice": lastPrice,
                            "timeStamp": datetime.now().strftime(' %b %d %H:%M:%S')
                            }
                          }

            with open("data.json", "w") as write_file:
                json.dump(price_data, write_file)
                print("Saved price data: $" + str(lastPrice) + " on " + datetime.now().strftime(' %b %d %H:%M:%S') +". New price: $" + str(price))
                
        return price

    except requests.ConnectionError:
        print ("Error querying Crytocompare API")

# Determines direction of the arrow
def arrow(price_input):
    try:
        
        currentPrice = price_input
        if lastPrice < currentPrice:
            return "\x00"
        elif lastPrice > currentPrice:
           return "\x01"
        elif lastPrice == currentPrice:
            return "\x02"
            
    except:
        print("Error comparing prices.")

# wipe LCD screen before we start
lcd.clear()

# start screen
lcd.backlight = True

# set last price empty
lastPrice = getSavedPrice()

# Main loop
while True:
    # show xch price
    price = xchPrice()
    
    # clear screen if price is less than 7 characters
    # because otherwise we'll get some weird overlaps..
    if len(str(price)) < 6:
        lcd.clear()
        print("Cleared screen to prevent decimal issues!")
    
    # print current price
    lcd_line_1 = " XCH: $" + str(price) + str(arrow(price)) + "\n"
    
    # update to last known price after we've compared
    lastPrice = price

    # date and time
    lcd_line_2 = datetime.now().strftime(' %b %d %H:%M:%S')

    # combine both lines into one update to the display
    lcd.message = lcd_line_1 + lcd_line_2

    sleep(5)
