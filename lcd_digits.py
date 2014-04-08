#!/usr/bin/python

import thread
import threading
import lcddriver
import datetime
import time
from time import gmtime, strftime

# Cells to be printed definition
cells = {}
cells['1'] = [0b00011,0b00011,0b00011,0b00000,0b00000,0b00000,0b00000,0b00000]
cells['2'] = [0b00111,0b00111,0b00111,0b00111,0b00111,0b00111,0b00111,0b00111]
cells['3'] = [0b11111,0b11111,0b11111,0b00111,0b00111,0b00111,0b00111,0b00111]
cells['4'] = [0b00011,0b00011,0b00011,0b00011,0b00011,0b00011,0b00011,0b00011]
cells['5'] = [0b11111,0b11111,0b11111,0b10000,0b10000,0b10000,0b10000,0b10000]
cells['6'] = [0b11100,0b11100,0b11100,0b11100,0b11100,0b11100,0b11100,0b11100]
cells['7'] = [0b11111,0b11111,0b11111,0b00000,0b00000,0b00000,0b00000,0b00000]
cells['8'] = [0b00111,0b00111,0b00111,0b00000,0b00000,0b00000,0b00000,0b00000]

# Numbers are printed based on cells
digits = {}
digits[1] = [0x00,0x05,0xFE,0x05,0x00,0x06]
digits[2] = [0x00,0x02,0x03,0x04,0x00,0x06]
digits[3] = [0x00,0x02,0x00,0x02,0x00,0x06]
digits[4] = [0x03,0x01,0x00,0x02,0xFE,0x07]
digits[5] = [0x03,0x04,0x00,0x02,0x00,0x06]
digits[6] = [0x03,0x06,0x03,0x02,0x00,0x06]
digits[7] = [0x00,0x02,0xFE,0x01,0xFE,0x07]
digits[8] = [0x03,0x02,0x03,0x02,0x00,0x06]
digits[9] = [0x03,0x02,0x00,0x02,0x00,0x06]
digits[0] = [0x03,0x02,0x03,0x01,0x00,0x06]

def print_digit(digit, position, lcd, rs):
   #pos = get_position(position)
   pos = position

   my_digit = digits[digit]

   lcd.lcd_write(0x80 + pos)
   lcd.lcd_write(my_digit[0],rs)
   lcd.lcd_write(0x80 + pos + 0x01)
   lcd.lcd_write(my_digit[1],rs)
   lcd.lcd_write(0xC0 + pos)
   lcd.lcd_write(my_digit[2],rs)
   lcd.lcd_write(0xC0 + pos + 0x01)
   lcd.lcd_write(my_digit[3],rs)
   lcd.lcd_write(0x94 + pos)
   lcd.lcd_write(my_digit[4],rs)
   lcd.lcd_write(0x94 + pos + 0x01)
   lcd.lcd_write(my_digit[5],rs)

def print_dots(lcd,rs,lock):
   lock.acquire()
   lcd.lcd_write(0xC4)
   lcd.lcd_write(0x3A,rs)
   lcd.lcd_write(0xC9)
   lcd.lcd_write(0x3A,rs)
   lock.release()

def print_date(local_data,lcd,rs):
   lcd.lcd_write(0x8F)
   lcd.lcd_write(ord(local_data[0]),rs)
   lcd.lcd_write(ord(local_data[1]),rs)
   lcd.lcd_write(ord('/'),rs)
   lcd.lcd_write(ord(local_data[3]),rs)
   lcd.lcd_write(ord(local_data[4]),rs)
   lcd.lcd_write(0xD0)
   lcd.lcd_write(ord(local_data[6]),rs)
   lcd.lcd_write(ord(local_data[7]),rs)
   lcd.lcd_write(ord(local_data[8]),rs)
   lcd.lcd_write(ord(local_data[9]),rs)

def run_clock(lcd,mRs,lock):
   print_dots(lcd,mRs,lock)
   while True:
      curr_time = strftime("%H:%M:%S", gmtime())
      lock.acquire()
      print_digit(int(curr_time[0]),0x00,lcd,mRs)
      print_digit(int(curr_time[1]),0x02,lcd,mRs)
      print_digit(int(curr_time[3]),0x05,lcd,mRs)
      print_digit(int(curr_time[4]),0x07,lcd,mRs)
      print_digit(int(curr_time[6]),0x0A,lcd,mRs)
      print_digit(int(curr_time[7]),0x0C,lcd,mRs)
      print_date(strftime("%d:%m:%Y", gmtime()),lcd,mRs)
      lock.release()
      time.sleep(1)

def run_banner(lcd,mRs,lock):
   count = 0
   while True:
      lock.acquire()
      lcd.lcd_display_string(("Bom dia %d" % count), 4)
      lock.release()
      count += 1
      time.sleep(1)

def main():

   mRs = 0b00000001
   lcd = lcddriver.lcd()
   lock = threading.Lock()

   #load user-defined graphs
   lcd.lcd_write(0x40)
   for mycells in ['1','2','3','4','5','6','7','8']:
      for cell in cells[mycells]:
         lcd.lcd_write(cell,mRs)

   lcd.lcd_clear()
   t1 = thread.start_new_thread(run_clock, (lcd,mRs,lock))
   t2 = thread.start_new_thread(run_banner, (lcd,mRs,lock))
   while True:
      pass
   

if __name__ == '__main__':
   main()


