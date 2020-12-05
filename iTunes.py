
import win32com.client
import re
import html2text
import urllib.request
import traceback
from time import sleep


app = win32com.client.Dispatch("iTunes.Application")


mainLibrary = app.Libraryplaylist



PATTERN =  '\||\(|\[|\{|\.m4a|\.mp4|\.mp3| ft| feat| prod|\n'
IMPORTANT_PHRASES = ['remix', 'demo']
def stripString(string):
    processed = re.split(PATTERN, string.lower())[0]
    for phrase in IMPORTANT_PHRASES:
        if phrase in string.lower() and phrase not in processed.lower():
            processed += ' ' + phrase
    return processed
    
commonNames = {'intro','introduction', 'outro'}

notURLCompatibleChars = ['&','#','?','"',"'","ꞌ","’",'Ø']
convertible = dict()
for char in notURLCompatibleChars:
    convertible[char] = ' '
convertible['é'] = '%C3%A9'
convertible['•'] = '%E2%80%A2'
convertible['Ø'] = 'O'
convertible['à'] = 'a' 
convertible['ä'] = 'a' 
convertible['ł'] = 'l' 
convertible['ø'] = 'o'


tooManyRequests = True
countGoogleRequests = 0
def getBingURL(name, albumArtist, album):    
    if name.lower() in commonNames:
        albumArtist = album
    name = stripString(name)
    albumArtist = stripString(albumArtist)
    nam = re.split(PATTERN, name.lower())[0]
    art = re.split(PATTERN, albumArtist.lower())[0]
    out = nam + ' ' + art
    for  char, val in convertible.items():
        if char in out:
            out = out.replace(char, val)

    
    url = 'https://www.bing.com/search?q=site:genius.com ' + out
    if not tooManyRequests:
        url = 'https://www.google.com/search?q=site:genius.com ' + out 
    return url.replace(' ', '%20')
    
def getGeniusURL(bingURL):
    global countGoogleRequests
    countGoogleRequests += 1
    req = urllib.request.Request(
        bingURL, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    out = f.read().decode('utf-8')
    beginningPattern = 'href="https://genius.com'
    endPattern = '"'

    results = re.findall( beginningPattern + '.*?' + endPattern, out)
    #processed = []
    for string in results:
        if("//genius.com" in string and  not ("genius.com/albums" in string) and not ("genius.com/artists" in string)            and not ("genius.com/a/" in string) and not ("genius.com/discussions/" in string)            and not ("genius.com/songs") in string             and not ("genius.com/videos/") in string):
            return string[6:-1]
            '''
            processed.append(string[6:-1])
    return processed[0]'''
    return ''

def getLyrics(geniusURL):
    if geniusURL == '' or geniusURL == None:
        return ''
    req = urllib.request.Request(
        geniusURL, 
        data=None, 
        headers={
            'User-Agent': \
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    out = f.read().decode('utf-8')
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    fullText = h.handle(out)
    l = 'Lyrics'
    start = fullText.index(l) + len(l) + 2
    end = fullText.index('More on Genius') - 2
    rDate = 'Release Date '
    releaseDate = 0
    try:
        release = fullText[fullText.index(rDate):]
        date = release[len(rDate):release.index('\n')]
        releaseDate = date.split()[-1]
    except:
        pass
    return fullText[start:end], releaseDate

artistNames = []    
#artistNames = {'kanye west', 'city morgue', 'brockhampton'}
for i, track in enumerate(mainLibrary.Tracks):
    #if track.year == 0:
    '''
    if i<150:
        continue'''
    if (track.AlbumArtist).lower() in artistNames:
        continue
    if track.lyrics == '':# or (len(track.lyrics) > 0 and track.lyrics[0] == '['):
        try:
            track.lyrics = ''
        except:
            print(track.name, 'Lyrics could not be set, track is probably deleted')
            #track.delete() # Maybe I should add this, the only other time this exception occurs is when the file is open in another program, so potentially 
            #                   undesirable / unexpected behaviour
            continue
        art = track.AlbumArtist
        if art.lower() == 'various artists':
            art = track.Artist
            if art.lower() == 'various artists':
                art = track.album
        elif art.lower() == 'bh':
            art = 'brockhampton'
        try:
            bng = getBingURL( track.name, art, track.album)
            
            print(bng)
            gen = getGeniusURL(bng)
            if not tooManyRequests:
                sleep(10) # can make many requests to bing, only Google limits requests
            print(gen)
            lyrics, year = getLyrics(gen)
            print(i,track.name, track.year)
            track.lyrics = lyrics
            if track.year == 0:
                track.year = year
        except IndexError:
            traceback.print_exc()
            print(track.Name, track.AlbumArtist, getBingURL(track.Name, art, track.album,'\n'))
        except Exception as e:
            traceback.print_exc()
            bng = getBingURL(track.Name, art, track.album)
            print('FIX\n',track.Name, track.AlbumArtist, bng)
            print( getGeniusURL(bng),'\n')

