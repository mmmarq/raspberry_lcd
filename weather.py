#!/usr/bin/python
# -*- coding: utf-8 -*-

#import library to do http requests:
import urllib2
import datetime
import time
from time import gmtime, strftime
from xml.dom.minidom import parseString

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
   file = urllib2.urlopen('http://servicos.cptec.inpe.br/XML/cidade/'+location_code+'/previsao.xml')
   #convert to string:
   data = file.read()
   #close file because we dont need it anymore:
   file.close()
   #parse the xml you downloaded
   dom = parseString(data)
   return dom

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

def run_banner(lcd,mRs,lock):
   while True:
      for position in [0,1,2,3]:
         weather_data = get_weather_data(parse_xml("2586"),position)
         text = week_day(weather_data[0]) + ": "
         print text + "Max " + weather_data[2] + " Min " + weather_data[3]
         time.sleep(3)
         print text + "IUV " + iuv_translator(weather_data[4])
         time.sleep(3)
         start = 0
         end = 20 - len(text)
         weather_now = weather[weather_data[1]]
         output = text + weather_now[start:(start + end)]
         print output
         time.sleep(1)
         start += 1
         while ( start + end < len(weather_now)+1 ):
            output = text + weather_now[start:(start + end)]
            print output
            start += 1
            time.sleep(0.3)

def main():

   run_banner("Marcelo",'b','a')

if __name__ == '__main__':
   main()


