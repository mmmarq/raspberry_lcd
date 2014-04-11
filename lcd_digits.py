#!/usr/bin/python
# -*- coding: utf-8 -*-

import thread
import threading
import lcddriver
import datetime
import urllib2
import time
from time import gmtime, strftime
from xml.dom.minidom import parseString
from urllib2 import URLError
from urllib2 import HTTPError

#Weather translate table
weather = {}
weather["ec"] = "Encoberto com Chuvas Isoladas"
weather["ci"] = "Chuvas Isoladas"
weather["c"] = "Chuva"
weather["in"] = "Instável"
weather["pp"] = "Poss. de Pancadas de Chuva"
weather["cm"] = "Chuva pela Manhã"
weather["cn"] = "Chuva a Noite"
weather["pt"] = "Pancadas de Chuva a Tarde"
weather["pm"] = "Pancadas de Chuva pela Manhã"
weather["np"] = "Nublado e Pancadas de Chuva"
weather["pc"] = "Pancadas de Chuva"
weather["pn"] = "Parcialmente Nublado"
weather["cv"] = "Chuvisco"
weather["ch"] = "Chuvoso"
weather["t"] = "Tempestade"
weather["ps"] = "Predomínio de Sol"
weather["e"] = "Encoberto"
weather["n"] = "Nublado"
weather["cl"] = "Céu Claro"
weather["nv"] = "Nevoeiro"
weather["g"] = "Geada"
weather["ne"] = "Neve"
weather["nd"] = "Não Definido"
weather["pnt"] = "Pancadas de Chuva a Noite"
weather["psc"] = "Possibilidade de Chuva"
weather["pcm"] = "Possibilidade de Chuva pela Manhã"
weather["pct"] = "Possibilidade de Chuva a Tarde"
weather["pcn"] = "Possibilidade de Chuva a Noite"
weather["npt"] = "Nublado com Pancadas a Tarde"
weather["npn"] = "Nublado com Pancadas a Noite"
weather["ncn"] = "Nublado com Poss. de Chuva a Noite"
weather["nct"] = "Nublado com Poss. de Chuva a Tarde"
weather["ncm"] = "Nubl. c/ Poss. de Chuva pela Manhã"
weather["npm"] = "Nublado com Pancadas pela Manhã"
weather["npp"] = "Nublado com Possibilidade de Chuva"
weather["vn"] = "Variação de Nebulosidade"
weather["ct"] = "Chuva a Tarde"
weather["ppn"] = "Poss. de Panc. de Chuva a Noite"
weather["ppt"] = "Poss. de Panc. de Chuva a Tarde"
weather["ppm"] = "Poss. de Panc. de Chuva pela Manhã"

# User-defined chars (binary)
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

# Week day short name
weekday_name = {}
weekday_name[0] = "Seg"
weekday_name[1] = "Ter"
weekday_name[2] = "Qua"
weekday_name[3] = "Qui"
weekday_name[4] = "Sex"
weekday_name[5] = "Sab"
weekday_name[6] = "Dom"


def print_digit(digit,position,lcd,rs,lock):
   pos = position
   my_digit = digits[digit]

   lock.acquire()
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
   lock.release()

def print_dots(lcd,rs,lock):
   lock.acquire()
   lcd.lcd_write(0xC4)
   lcd.lcd_write(0x3A,rs)
   lcd.lcd_write(0xC9)
   lcd.lcd_write(0x3A,rs)
   lock.release()

def print_date(local_date,lcd,rs,lock):
   lock.acquire()
   lcd.lcd_write(0x8E)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(ord(local_date[0]),rs)
   lcd.lcd_write(ord(local_date[1]),rs)
   lcd.lcd_write(0x2F,rs)
   lcd.lcd_write(ord(local_date[3]),rs)
   lcd.lcd_write(ord(local_date[4]),rs)
   lcd.lcd_write(0xCE)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(ord(local_date[6]),rs)
   lcd.lcd_write(ord(local_date[7]),rs)
   lcd.lcd_write(ord(local_date[8]),rs)
   lcd.lcd_write(ord(local_date[9]),rs)
   lcd.lcd_write(0xA2)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0xFE,rs)
   lock.release()

def print_localdata(local_temp,local_ur,lcd,rs,lock):
   lock.acquire()
   lcd.lcd_write(0x8E)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0x41,rs)
   lcd.lcd_write(0x67,rs)
   lcd.lcd_write(0x6F,rs)
   lcd.lcd_write(0x72,rs)
   lcd.lcd_write(0x61,rs)

   lcd.lcd_write(0xCE)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0x54,rs)
   lcd.lcd_write(0x3A,rs)
   lcd.lcd_write(ord(local_temp[0]),rs)
   lcd.lcd_write(ord(local_temp[1]),rs)
   lcd.lcd_write(0xDF,rs)

   lcd.lcd_write(0xA2)
   lcd.lcd_write(0xFE,rs)
   lcd.lcd_write(0x55,rs)
   lcd.lcd_write(0x3A,rs)
   lcd.lcd_write(ord(local_ur[0]),rs)
   lcd.lcd_write(ord(local_ur[1]),rs)
   lcd.lcd_write(0x25,rs)
   lock.release()

def week_day(d):
   if ( strftime("%Y-%m-%d", gmtime()) == d ): return "Hoje"
   temp = datetime.date(int(d.split('-')[0]),int(d.split('-')[1]),int(d.split('-')[2])).weekday()
   return weekday_name[temp]

def iuv_translator(iuv):
   if (( iuv >= 1 ) and ( iuv <= 2)): return "Baixo"
   if (( iuv >= 3 ) and ( iuv <= 5)): return "Moderado"
   if (( iuv >= 6 ) and ( iuv <= 7)): return "Alto"
   if (( iuv >= 8 ) and ( iuv <= 10)): return "Muito alto"
   return "Extremo"

def parse_xml(location_code):
   file = urllib2.urlopen('http://servicos.cptec.inpe.br/XML/cidade/'+location_code+'/previsao.xml')
   data = file.read()
   file.close()
   return parseString(data)

def get_weather_data(dom,position):
   if ( position >= 4 ): return []

   xmlTag = dom.getElementsByTagName('dia')[position].toxml()
   dia=xmlTag.replace('<dia>','').replace('</dia>','')

   xmlTag = dom.getElementsByTagName('tempo')[position].toxml()
   tempo=xmlTag.replace('<tempo>','').replace('</tempo>','')

   xmlTag = dom.getElementsByTagName('maxima')[position].toxml()
   max=xmlTag.replace('<maxima>','').replace('</maxima>','')

   xmlTag = dom.getElementsByTagName('minima')[position].toxml()
   min=xmlTag.replace('<minima>','').replace('</minima>','')

   xmlTag = dom.getElementsByTagName('iuv')[position].toxml()
   iuv=xmlTag.replace('<iuv>','').replace('</iuv>','')

   return [dia,tempo,max,min,iuv]

def run_date(lcd,mRs,lock,proc_lock):
   proc_lock.acquire()
   curr_date = strftime("%d/%m/%Y", gmtime())
   print_date(curr_date,lcd,mRs,lock)
   proc_lock.release()

   while True:
      proc_lock.acquire()
      curr_date = strftime("%d/%m/%Y", gmtime())
      print_date(curr_date,lcd,mRs,lock)
      proc_lock.release()
      time.sleep(1)

def run_localdata(lcd,mRs,lock,proc_lock):
   while True:
      time.sleep(15)
      proc_lock.acquire()
      print_localdata("27","45",lcd,mRs,lock)
      time.sleep(15)
      proc_lock.release()

def run_clock(lcd,mRs,lock):
   cell = {}
   cell[0] = 0x00
   cell[1] = 0x02
   cell[3] = 0x05
   cell[4] = 0x07
   cell[6] = 0x0A
   cell[7] = 0x0C

   prev_time = "AA:AA:AA"
   while True:
      curr_time = strftime("%H:%M:%S", gmtime())
      for pos in [0,1,3,4,6,7]:
         if ( curr_time[pos] != prev_time[pos] ):
            print_digit(int(curr_time[pos]),cell[pos],lcd,mRs,lock)
            print_dots(lcd,mRs,lock)

      prev_time = curr_time
      time.sleep(1)

def run_banner(lcd,lock):
   loop_count = 0
   dom = parse_xml("2586")
   while True:
      #Update forecast data only after 100th turn 
      if ( loop_count > 100 ):
         dom = parse_xml("2586")
         loop_count = 0
      loop_count += 1
      for position in [0,1,2,3]:
         weather_data = get_weather_data(dom,position)
         text = week_day(weather_data[0]) + ":"
         output = (text + "Max " + weather_data[2] + unichr(223) + " Min " + weather_data[3] + unichr(223)).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(3)
         output = (text + (" UV " + iuv_translator(weather_data[4])).center(20-len(text))).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(3)
         start = 0
         end = 20 - len(text)
         weather_now = " " + weather[weather_data[1]]
         output = (text + weather_now[start:(start + end)]).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(1)
         start += 1
         while ( start + end < len(weather_now)+1 ):
            output = (text + weather_now[start:(start + end)]).ljust(20)
            lock.acquire()
            lcd.lcd_display_string(output, 4)
            lock.release()
            start += 1
            time.sleep(0.2)
         time.sleep(0.8)

def main():
   mRs = 0b00000001

   lcd = lcddriver.lcd()
   lock = threading.Lock()
   proc_lock = threading.Lock()

   #load user-defined graphs
   lcd.lcd_write(0x40)
   for mycells in ['1','2','3','4','5','6','7','8']:
      for cell in cells[mycells]:
         lcd.lcd_write(cell,mRs)

   lcd.lcd_clear()
   t1 = thread.start_new_thread(run_clock, (lcd,mRs,lock))
   t2 = thread.start_new_thread(run_banner, (lcd,lock))
   t3 = thread.start_new_thread(run_date, (lcd,mRs,lock,proc_lock))
   t4 = thread.start_new_thread(run_localdata, (lcd,mRs,lock,proc_lock))

   while True:
      #pass
      time.sleep(1)
   

if __name__ == '__main__':
   main()


