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

def print_dots(lcd,rs):
   lcd.lcd_write(0xC4)
   lcd.lcd_write(0x3A,rs)
   lcd.lcd_write(0xC9)
   lcd.lcd_write(0x3A,rs)

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

def week_day(d):
   if ( strftime("%Y-%m-%d", gmtime()) == d ): return "Hoje"
   temp = datetime.date(int(d.split('-')[0]),int(d.split('-')[1]),int(d.split('-')[2])).weekday()
   if ( temp == 0 ): return "Seg"
   if ( temp == 1 ): return "Ter"
   if ( temp == 2 ): return "Qua"
   if ( temp == 3 ): return "Qui"
   if ( temp == 4 ): return "Sex"
   if ( temp == 5 ): return "Sab"
   if ( temp == 6 ): return "Dom"

def iuv_translator(iuv):
   if (( iuv >= 1 ) and ( iuv <= 2)): return "Baixo"
   if (( iuv >= 3 ) and ( iuv <= 5)): return "Moderado"
   if (( iuv >= 6 ) and ( iuv <= 7)): return "Alto"
   if (( iuv >= 8 ) and ( iuv <= 10)): return "Muito alto"
   return "Extremo"

def parse_xml(location_code):
   try:
      file = urllib2.urlopen('http://servicos.cptec.inpe.br/XML/cidade/'+location_code+'/previsao.xml')
   except (URLError, HTTPError):
      return None

   try:
      #convert to string:
      data = file.read()
      #close file because we dont need it anymore:
      file.close()
      #parse the xml you downloaded
   except (IOError):
      return None

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

def run_clock(lcd,mRs,lock):
   while True:
      curr_time = strftime("%H:%M:%S", gmtime())
      lock.acquire()
      print_dots(lcd,mRs)
      print_digit(int(curr_time[0]),0x00,lcd,mRs)
      print_digit(int(curr_time[1]),0x02,lcd,mRs)
      print_digit(int(curr_time[3]),0x05,lcd,mRs)
      print_digit(int(curr_time[4]),0x07,lcd,mRs)
      print_digit(int(curr_time[6]),0x0A,lcd,mRs)
      print_digit(int(curr_time[7]),0x0C,lcd,mRs)
      print_date(strftime("%d:%m:%Y", gmtime()),lcd,mRs)
      lock.release()
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
         #print text + "Max " + weather_data[2] + " Min " + weather_data[3]
         output = (text + " Max " + weather_data[2] + " Min " + weather_data[3]).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(3)
         #print text + "IUV " + iuv_translator(weather_data[4])
         output = (text + " UV " + iuv_translator(weather_data[4])).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(3)
         start = 0
         end = 20 - len(text)
         weather_now = " " + weather[weather_data[1]]
         #output = text + weather_now[start:(start + end)]
         #print output
         output = (text + weather_now[start:(start + end)]).ljust(20)
         lock.acquire()
         lcd.lcd_display_string(output, 4)
         lock.release()
         time.sleep(1)
         start += 1
         while ( start + end < len(weather_now)+1 ):
            #output = text + weather_now[start:(start + end)]
            #print output
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

   #load user-defined graphs
   lcd.lcd_write(0x40)
   for mycells in ['1','2','3','4','5','6','7','8']:
      for cell in cells[mycells]:
         lcd.lcd_write(cell,mRs)

   lcd.lcd_clear()
   t1 = thread.start_new_thread(run_clock, (lcd,mRs,lock))
   t2 = thread.start_new_thread(run_banner, (lcd,lock))
   while True:
      pass
   

if __name__ == '__main__':
   main()


