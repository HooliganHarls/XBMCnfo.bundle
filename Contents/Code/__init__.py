#xbmc-nfo importer
#spec'd from: http://wiki.xbmc.org/index.php?title=Import_-_Export_Library#Video_nfo_Files
import os, re, os.path



class xbmcnfo(Agent.Movies):
  name = 'XBMC .nfo Importer'
  primary_provider=True
  languages = [Locale.Language.English]

  #contributes_to = ['com.plexapp.agents.imdb']
  
  
  def search(self, results, media, lang):
    Log("Searching")
    
    fname=Media
    id=media.name
    pageUrl="http://localhost:32400/library/metadata/" + media.id
    page=HTTP.Request(pageUrl)
    Log(media.primary_metadata)
    nfoXML = XML.ElementFromURL(pageUrl).xpath('//MediaContainer/Video/Media/Part')[0]
    path1=nfoXML.get('file')
    path = os.path.dirname(path1)
    if os.path.exists(path):
      for f in os.listdir(path):
        if f.split(".")[-1].lower() == "nfo":
          nfoName=f.split(".")[0]
          fname1=path1.split("/")[-1]
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
                nfoTextLower = nfoText.lower()
                if nfoTextLower.count('<movie>') > 0 and nfoTextLower.count('</movie>') > 0:
                  #likely an xbmc nfo file
                  nfoXML = XML.ElementFromString(nfoText).xpath('//movie')[0]
            
                  #title
                  try: media.id = nfoXML.xpath('./id')[0].text
                  except: pass
                  #title
                  try: media.year = nfoXML.xpath('./year')[0].text
                  except: pass
   
    Log(path1)
    
    Log("++++++++++++++++++++++++")
    Log("media")
    Log(media)
    Log("metadata")
    #Log(metadata)
    score=100
    #Log(metadata.year)
    id=id+"_nfo"
    Log(media.id)
    Log(media.items)
    Log("++++++++++++++++++++++++")
    
    name=media.name
    results.Append(MetadataSearchResult(id=media.id,name=name,year=media.year,lang=lang,score=100))
    for result in results:
		Log('scraped results: ' + result.name + ' | year = ' + str(result.year) + ' | id = ' + result.id + '| score = ' + str(result.score))
   
  def update(self, metadata, media, lang):
    results=MediaContainer()
    id=""
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
                  try: 
                    tempdirector=nfoXML.xpath('./director')[0].text
                    directors=tempdirector.split("/")
                    Log(directors)
                  except: pass
                  if directors != "":
                        metadata.directors.clear()
                        Log("cleared directors")
                        for r in directors:
                            Log(r)
                            metadata.directors.add(r)

                  
                  #studio
                  try: metadata.studio = nfoXML.findall("studio")[0].text
                  except: pass
                  #duration
                  try: metadata.duration = float(nfoXML.xpath("runtime")[0].text)
                  except: pass
                  Log(metadata.id)
                  #genre, cant see mulltiple only sees string not seperate genres
                  metadata.genres.clear()
                  try: 
                    tempgenre=nfoXML.xpath('./genre')[0].text
                    genres=tempgenre.split("/")
                  except: pass
                  Log(genres)
                  if genres != "":
                        metadata.genres.clear()
                        Log("cleared genres")
                        for r in genres:
                            Log(r)
                            metadata.genres.add(r)
                            Log(metadata.genres)
                  #actors
                  metadata.roles.clear()
                  for actor in nfoXML.findall('./actor'):
                        role = metadata.roles.new()
                        try: role.role = actor.xpath("role")[0].text
                        except: pass
                        try: role.actor = actor.xpath("name")[0].text
                        except: pass


                  #nfo thumbs
                  thumbs=[]

                  try: thumbs=nfoXML.xpath("./thumb")
                  except: pass
  
                  #checks to see if the poster already exists
                  #if not it adds it.
                  name = metadata.title
                  for thumb in thumbs:
                    Log(thumb.text)
                  @parallelize
                  def loopThroughPosters(thumbs=thumbs):
                    try:
                      i = 0
                      for thumb in thumbs:
                          i += 1
                          @task
                          def grabPoster(pUrl=thumb.text, i=i):
                            posterUrl = pUrl
                            Log("Adding: " + pUrl)
                            thumbpic = HTTP.Request(pUrl)
                            metadata.posters[posterUrl] = Proxy.Preview(thumbpic, sort_order = i)
                    except:
                      pass

                                    
                  Log("++++++++++++++++++++++++")
                  Log("Movie nfo Information")
                  Log("++++++++++++++++++++++++")
                  Log("Title: " + str(metadata.title))
                  Log("id: " + str(metadata.guid))
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
                  Log(metadata.id)
                  Log("++++++++++++++++++++++++")
                  return id, metadata
 

                        
   

 
 