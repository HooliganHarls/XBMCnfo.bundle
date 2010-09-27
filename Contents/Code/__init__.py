#xbmc-nfo importer
#spec'd from: http://wiki.xbmc.org/index.php?title=Import_-_Export_Library#Video_nfo_Files
import os, re



class xbmcnfo(Agent.Movies):
  name = 'XBMC .nfo Importer'
  primary_provider=False
  languages = [Locale.Language.English]

  contributes_to = ['com.plexapp.agents.imdb']
  
  
  def search(self, results, media, lang):
    Log("Searching")
    metadata=(media.primary_metadata)
    fname=Media
    m = re.search('(tt[0-9]+)', media.guid)
    if m:
      id = m.groups(1)[0]
    Log("++++++++++++++++++++++++")
    Log("media")
    Log(media)
    Log("metadata")
    Log(metadata)
    score=100
    Log(metadata.year)
    id=id+"_nfo"
    Log(id)
    Log("++++++++++++++++++++++++")
    name="XBMC Nfo"
    results.Append(MetadataSearchResult(id=id,name=name,year=metadata.year,score=100))
    for result in results:
		Log('scraped results: ' + result.name + ' | year = ' + str(result.year) + ' | id = ' + result.id + '| score = ' + str(result.score))
   
  def update(self, metadata, media, lang):
    results=MediaContainer()
    (id, metadata)=self.scrapeNfo(metadata, media, lang)
    Log("Back in your datas, sending you the results")
    name=metadata.title
    results.Append(MetadataSearchResult(id=id,name=name,score=100))
    for result in results:
		Log('scraped results: ' + result.name + ' | year = ' + str(result.year) + ' | id = ' + result.id + '| score = ' + str(result.score))

  def scrapeNfo(self, metadata, media, lang):
    Log("all your datas are belong to us")
    Log('UPDATE: ' + media.items[0].parts[0].file)
    path = os.path.dirname(media.items[0].parts[0].file)
    id=media.title
    nfoFile=''
    Log(path)
    if os.path.exists(path):
      for f in os.listdir(path):
        if f.split(".")[-1].lower() == "nfo":
          nfoName=f.split(".")[0]
	  fname1=media.items[0].parts[0].file.split("/")[-1]
          fname2=fname1.split(".")[0]
          if fname2.lower() == "the":
            fname2=fname2+"." + fname1.split(".")[1]    

          if len(fname2) < len(nfoName):
            nfoName2=nfoName[len(fname2)]
          else:
            nfoName2=nfoName
          Log(len(fname2))
          Log(nfoName2)
          if fname2==nfoName2:
	    nfoFile = os.path.join(path, f)
	  
            nfoText = Core.storage.load(nfoFile)
            #nfoText = t.read()
            nfoTextLower = nfoText.lower()
            if nfoTextLower.count('<movie>') > 0 and nfoTextLower.count('</movie>') > 0:
              #likely an xbmc nfo file
              nfoXML = XML.ElementFromString(nfoText).xpath('//movie')[0]
            
              #title
              try: metadata.title = nfoXML.xpath('./title')[0].text
              except: pass
              #summary
              try: metadata.summary = nfoXML.xpath('./plot')[0].text
              except: pass            
              #year
              try: metadata.year = int(nfoXML.xpath("year")[0].text)
              except: pass
              #rating
              try: metadata.rating = float(nfoXML.xpath('./rating')[0].text)
              except: pass
              Log(metadata.rating)
              #content rating
              try: metadata.content_rating = nfoXML.xpath('./mpaa')[0].text
              except: pass
              #director
              metadata.directors.clear()
              try: metadata.directors.add(nfoXML.xpath("director")[0].text)
              except: pass
              #studio
              try: metadata.studio = nfoXML.findall("studio")[0].text
              except: pass
              #duration
              try: metadata.duration = float(nfoXML.xpath("runtime")[0].text)
              except: pass
              #genre, cant see mulltiple only sees string not seperate genres
              metadata.genres.clear()
              try: 
                tempgenre=nfoXML.xpath('./genre')[0].text
                genres=tempgenre.split("/")
      	    	Log(genres)
                if genres != "":
                  metadata.genres.clear()
                  Log("cleared genres")
                  for r in genres:
     		      Log(r)
                  metadata.genres.add(r)
                  Log(metadata.genres)
              except: pass

              #actors
 	      metadata.roles.clear()
 	      for actor in nfoXML.findall('./actor'):
			role = metadata.roles.new()
			try: role.role = actor.xpath("role")[0].text
                        except: pass
			try: role.actor = actor.xpath("name")[0].text
			except: pass
            try: role.photo = actor.xpath("thumb")[0].text
            except: pass
            m = re.search('(tt[0-9]+)', metadata.guid)
 	    if m:
              id = m.groups(1)[0]
        


              
              data = HTTP.Request(nfoXML.xpath('./thumb')[0].text)
              name = 'xbmc-nfo-thumb'
             # if name not in metadata.posters:
              #  metadata.posters[name] = Proxy.Media(data)
              #break
        #    else:
         #     continue
              Log("++++++++++++++++++++++++")
              Log("Movie nfo Information")
              Log("++++++++++++++++++++++++")
              Log("Title: " + str(metadata.title))
              Log("Summary: " + str(metadata.summary))
              Log("Year: " + str(metadata.year))
              Log("IMDB rating: " + str(metadata.rating)) 
              Log("Content Rating: " + str(metadata.content_rating))
              Log("Director " + str(metadata.directors))
              Log("Studio: " + str(metadata.studio))
              Log("Duration: " + str(metadata.duration))
             # Log("Actors")
             # for r in metadata.roles:
	     #   Log("Actor: " + r.actor + " | Role: " + r.role)
              Log("Genres")
              for r in metadata.genres:
	        Log("genres: " + r)
              Log("++++++++++++++++++++++++")
 
              return id, metadata
 

                        
    #ratings = {}
    #for rating in HTML.ElementFromURL(RT_BASE_URL + metadata.id).xpath('//div[@class="movie_info_area"]//li/a'):
    #  ratingText = rating.get('title')
     # if ratingText != "N/A" and len(ratingText) > 0:
      #  ratings[rating.xpath('span')[0].text] = float(ratingText.replace('%',''))/10
    #metadata.rating = ratings['T-Meter Critics']

 
 