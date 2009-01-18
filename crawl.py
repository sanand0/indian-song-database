# DROP DATABASE IF EXISTS `songs`;
# CREATE DATABASE `songs` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;

# TODO: avoid errors like UnicodeEncodeError: 'charmap' codec can't encode character u'\u2013' in position 27: character maps to <undefined> when Getting hindi ww.smashits.com movie (near GHAZALS - MEHDI...)

from sqlobject import *
import film, datetime, re, time, traceback, sys

film.connect()
film.create()

INDEX_DAYS = 3    # Default: 3
MOVIE_DAYS = 400  # Default: 400
__now__   = datetime.datetime.now()

def if_new(entity, age, function, item):
    if (__now__ - entity.date).days >= age:
        try:
            html = entity.read()
            function(entity, html, item)
            entity.date = __now__
            return html
        except Exception:
            traceback.print_exc(0)

# ================================================================================================================================
class SongsPk:
    pass

# ================================================================================================================================
class Raaga:
    lang = {
        'hindi'      : ( ('hindi'     , 'movies'), ),
        'tamil'      : ( ('tamil'     , 'movies'), ),
        'hindustani' : ( ('hindustani', 'movies'), ),
        'telugu'     : ( ('telugu'    , 'movies'), ),
        'malayalam'  : ( ('malayalam' , 'movies'), ),
        'kannada'    : ( ('kannada'   , 'movies'), ),
        'carnatic'   : ( ('carnatic'  , 'albums'),
                         ('sanskrit'  , 'albums'), ),
        'bengali'    : ( ('bengali'   , 'movies'), ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            index = film.entity('www.raaga.com', 'index', lang, item[0], item[0], 'channels/' + item[0] + '/' + item[1] + '.asp')
            if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        name = re.sub('\(\d+?\)', '', name)         # Ignore numbers in brackets
        return name

    def do_index(self, index, html, item):
        for match in re.findall('href="http://www.raaga.com/(channels/' + index.lang + '/moviedetail.asp\?mid=)(\w*)[^>]*>([^<]*)</a>', html, re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), match[0] + match[1])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def do_movie(self, movie, html, item):
        year = re.findall(movie.name + '\s+\((\d+)\)', html, re.UNICODE)
        if year: film.relate(movie, 'year', film.entity('', 'year', '', year[0], year[0], ''))

        for match in re.findall('"http://www.raaga.com/(channels/' + movie.lang + '/music/.*?\.html)".*?>(.*?)</a>', html, re.UNICODE):
            film.relate(movie, 'composer', film.entity(movie.db, 'person', movie.lang, match[1], match[1], match[0]))

        for songhtml in html.split('setList1(')[1:]:
            match = re.findall('^(\d+)[^>]+>(.*?)</a>', songhtml, re.UNICODE)
            if match:
                song = film.entity(movie.db, 'song', movie.lang, match[0][0], match[0][1], 'playerV31/index.asp?pick=' + match[0][0])
                film.relate(movie, 'song', song)

                for match in re.findall('http://www.raaga.com/(channels/' + song.lang + '/artist/[^"]*\.html)"[^>]*>([^<]*)<', songhtml, re.S + re.UNICODE):
                    film.relate(song, 'singer', film.entity(song.db, 'person', song.lang, match[1], match[1], match[0]))

                match = re.findall('\((\d+:\d+)\)', songhtml, re.UNICODE)
                if match: film.relate(song, 'duration', film.entity('', 'duration', '', match[0][0], match[0][0], ''))

                match = re.findall('RATING:\s*(\d+\.\d+)', songhtml, re.UNICODE)
                if match: film.relate(song, 'rating', film.entity('', 'rating', '', match[0][0], match[0][0], ''))

                match = re.findall('Lyricist:</b>(.*?)<', songhtml, re.S + re.UNICODE)
                if match: film.relate(song, 'lyricist', film.entity('', 'person', '', match[0][0], match[0][0], ''))

        # Keep this at the end, because the cast doesn't have a URL, and you don't want this overshadowing the same singer
        cast = re.findall('CAST:.*?<td.*?>(.*?)</td>', html, re.S + re.UNICODE)
        if cast:
            for actor in cast[0].split(','):
                film.relate(movie, 'actor', film.entity(movie.db, 'person', movie.lang, actor, actor, ''))

# ================================================================================================================================
class MusicIndiaOnline:
    lang = {
        'tamil'         :   ( ('tamil',                     'movie_name' ), ),
        'hindi'         :   ( ('hindi_bollywood',           'movie_name' ),
                              ('ghazals',                   'album'      ), ),
        'hindustani'    :   ( ('hindustani_instrumental',   'album'      ),
                              ('hindustani_special',        'album'      ),
                              ('hindustani_vocal',          'album'      ), ),
        'carnatic'      :   ( ('carnatic_vocal',            'album'      ),
                              ('carnatic_special',          'album'      ),
                              ('carnatic_instrumental',     'album'      ),
                              ('devotional',                'album'      ), ),
        'telugu'        :   ( ('telugu',                    'movie_name' ), ),
        'malayalam'     :   ( ('malayalam',                 'movie_name' ), ),
        'kannada'       :   ( ('kannada',                   'movie_name' ), ),
    }

    attr = {
        'movie_name'     : ( 'movie'        , 'movie'  ),
        'album'          : ( 'movie'        , 'movie'  ),
        'singer'         : ( 'singer'       , 'person' ),
        'artist'         : ( 'singer'       , 'person' ),
        'actors'         : ( 'actor'        , 'person' ),
        'music_director' : ( 'composer'     , 'person' ),
        'composer'       : ( 'composer'     , 'person' ),
        'year'           : ( 'year'         , 'year'   ),
        'director'       : ( 'director'     , 'person' ),
        'producer'       : ( 'producer'     , 'person' ),
        'lyrics'         : ( 'lyricist'     , 'person' ),
        'theme'          : ( 'tag'          , 'tag'    ),
        'type'           : ( 'tag'          , 'tag'    ),
        'instrument'     : ( 'instrument'   , 'tag'    ),
        'ragam'          : ( 'raaga'        , 'tag'    ),
        'raag'           : ( 'raaga'        , 'tag'    ),
        'thalam'         : ( 'beat'         , 'tag'    ),
        'taal'           : ( 'beat'         , 'tag'    ),
        'religion'       : ( 'religion'     , 'tag'    ),
        'diety'          : ( 'deity'        , 'tag'    ),
        'language'       : ( 'language'     , 'tag'    ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                name = item[0] + ":" + letter
                index = film.entity('www.musicindiaonline.com', 'index', lang, name, name, 'music/' + item[0] + '/i/' + letter + '/')
                if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        name = re.sub('<[^>]*>', '', name)          # Ignore tags
        name = re.sub('\(\d+?\)', '', name)         # Ignore numbers in brackets
        name = re.sub('(19|20)\d\d', '', name)      # Ignore year, even outside of brackets... TODO: What about 1947:Earth and 1942:A Love Story?
        name = re.sub('\s*\-\s*$', '', name)        # Ignore anything after the trailing hyphen
        return name

    def do_index(self, index, html, item):
        for match in re.findall('/(music/' + item[0] + '/s/' + item[1] + '.(\d+)/).>(.*?)</a>', html, re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), match[0])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def do_movie(self, movie, html, item):
        for match in re.findall('href=./(music/' + movie.lang + '/m/(\w+).(\d+)/).>(.*?)</a>', html, re.UNICODE):
            rel = self.attr[match[1]]
            film.relate(movie, rel[0], film.entity(movie.db, rel[1], movie.lang, match[2], match[3], match[0]))

        # Match song
        for match in re.findall('<tr.*?href=./p/x/([^/]*)/[^>]*>(.*?)</a>(.*?)</tr>', html, re.S + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[0], match[1], 'p/x/' + match[0])
            film.relate(movie, 'song', song)

            # Get song attributes
            for submatch in re.findall("onclick=.sltb_filt\('(.*?)',(\d+)\)[^>]+>(.*?)</a>", match[2], re.S + re.UNICODE):
                rel = self.attr[submatch[0]]
                film.relate(song, rel[0], film.entity(movie.db, rel[1], movie.lang, submatch[1], submatch[2], 'music/' + movie.lang + '/m/' + rel[0] + '.' + submatch[1]))

            # Get lyrics
            for submatch in re.findall('/(lr/(\d+/\d+)/)', match[2], re.S + re.UNICODE):
                film.relate(song, 'lyrics', film.entity(movie.db, 'tag', movie.lang, submatch[1], 'lyrics', submatch[0]))

# ================================================================================================================================
# TODO: Add Smashitsusa.com
class Smashits:
    lang = {
            'tamil'       : ( ( 'tamil'          , '41' ), ),
            'hindi'       : ( ( 'forthcoming'    , '24' ),
                              ( 'ghazals'        , '25' ),
                              ( 'karaoke'        , '29' ),
                              ( 'marriage-songs' , '32' ),
                              ( 'oldies'         , '35' ),
                              ( 'hindi-film'     , '40' ), ),
            'telugu'      : ( ( 'telugu'         , '42' ), ),
            'kannada'     : ( ( 'kannada'        , '28' ), ),
            'malayalam'   : ( ( 'malayalam'      , '30' ), ),
            'carnatic'    : ( ( 'carnatic'       , '22' ), ),
            'hindustani'  : ( ( 'classical'      , '23' ),
                              ( 'instrumental'   , '27' ),
                              ( 'n-ind-classical', '34' ), ),
            'bengali'     : ( ( 'bengali'        , '20' ), ),
            'punjabi'     : ( ( 'bhangra'        , '21' ), ),
            'gujarati'    : ( ( 'gujarati'       , '26' ), ),
            'marathi'     : ( ( 'marathi'        , '31' ), ),
    }

    attr = {
        'Year'              : ( 'year'      , 'year'    ),
        'Genre'             : ( 'tag'       , 'tag'     ),
        'Director'          : ( 'director'  , 'person'  ),
        u'Music\xa0Director': ( 'composer'  , 'person'  ),
        u'Leading\xa0Cast'  : ( 'actor'     , 'person'  ),
        'Label'             : ( 'tag'       , 'tag'     ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            index = film.entity('ww.smashits.com', 'index', lang, item[0], item[0], 'index.cfm?Page=Audio&SubPage=ShowSubCats&AudioCatID=' + item[1])
            if_new(index, INDEX_DAYS, self.do_index, item)

    def do_index(self, index, html, item):
        # TODO: Why not just index the collections as well? Why restrict it to movies?
        html = html.partition('Movies</span>')
        html = html[2] or html[0]
        for match in re.findall('href="/(music/' + item[0] + '/songs/(\d+).*?)">(.*?)</a>', html, re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], match[2], match[0])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def do_movie(self, movie, html, item):
        for match in re.findall('<td class="albumInfo"[^>]*><.*?>(.*?)\s*:\s*<.*?></td>\s*<td class="albumInfo"[^>]*>(.*?)</td>', html, re.S + re.UNICODE):
            rel = self.attr[match[0]]
            names = re.sub('<[^>]*>', '', match[1])     # Remove tags
            for item in names.split(','):
                urlfrag = re.findall('href="(.*?)"[^>]*>(.*?)</a>', item, re.S + re.UNICODE)
                (url, name) = urlfrag and urlfrag[0] or ('', item)
                film.relate(movie, rel[0], film.entity(movie.db, rel[1], movie.lang, name, name, url))

        for match in re.findall('onClick="loadPlayer\(.(\d+).\).*?>(.*?)</a>.*?Rating:(\d+\.\d+)', html, re.S + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[0], match[1], 'player/ra/ondemand/launch_player.cfm?' + match[0])
            film.relate(movie, 'song', song)
            film.relate(movie, 'rating', film.entity(movie.db, 'rating', '', match[2], match[2], ''))


# ================================================================================================================================
class Oosai:
    lang = {
        'tamil' : ( ('tamil', ), ),
    }
    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            for letter in ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','misc'):
                index = film.entity('www.oosai.com', 'index', lang, letter, letter, lang + 'movies/movielistby_' + letter + '.cfm')
                if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        name = re.sub('<img.*?alt=["\']?(.*?)(["\']|\w+=).*?>', r'\1', name)
        return name

    def do_index(self, index, html, item):
        for match in re.findall('href="(' + index.lang + 'songs/(.*?)\.cfm)".*?>(.*?)</a>', html, re.S + re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), match[0])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def do_movie(self, movie, html, item):
        for match in re.findall('Music Director\s*: <[^>]*>(.*?)<', html, re.S + re.UNICODE):
            for name in re.split('\s*,\s*', match):
                film.relate(movie, 'composer', film.entity(movie.db, 'person', movie.lang, name, name, ''))

        for match in re.findall('Stars\s*: <[^>]*>(.*?)<', html, re.S + re.UNICODE):
            for name in re.split('\s*[,&\r\n]+\s*', match):
                film.relate(movie, 'actor', film.entity(movie.db, 'person', movie.lang, name, name, ''))

#        for match in re.findall('onclick="setUsrlist.(\d*)[^>]>([^<]*)</a>.*class="ph1">([^<]*)<', html, re.S + re.UNICODE):
        for match in re.findall('onclick="setUsrlist.(\d*)[^>]*>([^<]*)</a>.*?class="ph1">([^<]*)<', html, re.S + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[0], match[1], '')
            film.relate(movie, 'song', song)

            for name in re.split('\s*[,&\r\n]+\s*', match[2]):
                film.relate(song, 'singer', film.entity(movie.db, 'person', movie.lang, name, name, ''))

# ================================================================================================================================
class Dishant:
    lang = {
        'bengali'   : ( ('bengali'     , ), ),
        'punjabi'   : ( ('bhangra'     , ), ),
        'carnatic'  : ( ('carnatic'    , ), ),
        'gujarati'  : ( ('gujarati'    , ), ),
        'hindi'     : ( ('hindi'       , ),
                        ('compilations', ),
                        ('pop'         , ),
                        ('remix'       , ),
                        ('old'         , ),
                        ('romantic'    , ),
                        ('wedding'     , ),
                        ('instrumental', ),
                        ('patiotic'    , ),
                        ('karaoke'     , ), ),
        'kannada'   : ( ('kannada'     , ), ),
        'malayalam' : ( ('malayalam'   , ), ),
        'marathi'   : ( ('marathi'     , ), ),
        'tamil'     : ( ('tamil'       , ), ),
        'telugu'    : ( ('telugu'      , ), ),
        'hindustani': ( ('qawwali'     , ),
                        ('classical'   , ),
                        ('religious'   , ), ),
    }

    attr = (
        ('cast'             , 'actor'   , 'person'),
        ('music-director'   , 'composer', 'person'),
        ('director'         , 'director', 'person'),
        ('producer'         , 'producer', 'person'),
        ('lyricist'         , 'lyricist', 'person'),
        ('jukebox'          , 'year'    , 'year'  ),
    )

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            index = film.entity('www.dishant.com', 'index', lang, item[0], item[0], item[0] + '-albums-index.html')
            if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        name = re.sub('\(\d+?\)', '', name)         # Ignore numbers in brackets
        return name

    # TODO: The movie 'Mr. 100% - The Real Player' causes problems
    def do_index(self, index, html, item):
        for match in re.findall('/(album/([^"]+)\.html)">(.*?)</a>', html, re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), match[0])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def do_movie(self, movie, html, item):
        for item in self.attr:
            for match in re.findall('href="../(' + item[0] + '/(\w+)\.html)">([^<]*)</a>', html, re.IGNORECASE + re.UNICODE):
                film.relate(movie, item[1], film.entity(movie.db, item[2], movie.lang, match[1], match[2], match[0]))

        for match in re.findall('width="60%">([^<]*)<.*?/(jukebox.php\?songid=(\d+))', html, re.S + re.IGNORECASE + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[2], match[0], match[1])
            film.relate(movie, 'song', song)

# ================================================================================================================================
class Dhingana:
    lang = {
        'hindi'     : ( ('latest'   , ),
                        ('oldies'   , ),
                        ('pop'      , ),
                        ('special'  , ),
                        ('ghazals'  , ),
                        ('bhajans'  , ), ),
        'tamil'     : ( ('album'    , ), ),
        'punjabi'   : ( ('punjabi'  , ),
                        ('bhangra'  , ), ),
        'marathi'   : ( ('album'    , ), ),
    }

    attr = (
        ('CAST',    'person',   'actor'     ),
        ('MUSIC',   'person',   'composer'  ),
        ('YEAR',    'year',     'year'      ),
    )

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            html = self.get_index(lang, item, '1')
            for count in re.findall('/home/' + lang + '/' + item[0] + '/a_a/at/page/(\d+)', html, re.UNICODE):
                self.get_index(lang, item, count[0])

    def get_index(self, lang, item, count):
        index = film.entity('www.dhingana.com', 'index', lang, item[0] + count, item[0] + count, 'home/' + lang + '/' + item[0] + '/a_a/at/page/' + count)
        return if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        return name

    def do_index(self, index, html, item):
        for match in re.findall('/([^\/]*/movie/songs/' + index.lang + '/' + item[0] + '/(\d+))">(.*?)</a>', html, re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), match[0])
            if_new(index, INDEX_DAYS, self.do_index, item)

    def do_movie(self, movie, html, item):
        for item in self.attr:
            for match in re.findall('<H3>' + item[0] + '</H3>\s*<p>(.*?)</p>', html, re.S + re.IGNORECASE + re.UNICODE):
                for thing in match[0].split(','):
                    print thing, item[1], item[2]
                    # film.relate(movie, item[1], film.entity(movie.db, item[2], movie.lang, match[1], match[2], match[0]))

        # TODO: Get the songs


# ================================================================================================================================
# http://www.mp3hungama.com/music/genre_albums.php?id=3

class MP3Hungama:
    lang = {
        'hindi':        ( ('indian-movies'    , '3', ),
                          ('oldies'           , '2', ),
                          ('remix'            , '5', ), ),
    }

    attr = {
        'Cast'          : ( 'actor'     , 'person' ),
        'Music Director': ( 'composer'  , 'person' ),
        'Director'      : ( 'director'  , 'person' ),
        'Producer'      : ( 'producer'  , 'person' ),
        'Lyrics'        : ( 'lyricist'  , 'person' ),
        'Year'          : ( 'year'      , 'year'   ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            index = film.entity('www.mp3hungama.com', 'index', lang, item[1], item[1], 'music/genre_albums.php?id=' + item[1])
            if_new(index, INDEX_DAYS, self.do_index, item)

    def strip_name(self, name):
        name = re.sub('<[^>]*>', '', name)          # Ignore tags
        name = re.sub('\([^\)]+\)', '', name)       # Ignore anything in brackets (TODO: risky)
        name = re.sub('\s*\-\s*$', '', name)        # Ignore anything after the trailing hyphen
        return name

    def do_index(self, index, html, item):
        for match in re.findall('href="(index.php\?action=album&id=(\d+))">(.*?)</a>', html, re.IGNORECASE + re.S + re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], self.strip_name(match[2]), 'music/' + match[0])
            if_new(index, INDEX_DAYS, self.do_index, item)

    def do_movie(self, movie, html, item):
        for info in re.findall('<b>Album Info:</b>(.*?)<BR>', html, re.IGNORECASE + re.S + re.UNICODE):
            for match in re.findall('^(.*?):(.*?)$', info[0], re.IGNORECASE + re.S + re.UNICODE + re.MULTILINE):
                rel = self.attr[match[0]]
                # for name in match[1].split(', '):
                #     film.relate(movie, rel[0], film.entity(movie.db, rel[1], movie.lang, match[1], match[1], url))

        for match in re.findall('playSong\((\d+)\)(.*?)</b>', html, re.IGNORECASE + re.S + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[0], self.strip_name(match[1]), 'music/index.php?action=song&id=' + match[0])
            # film.relate(movie, 'song', song)

# ================================================================================================================================
class Cooltoad:
    lang = {
        'tamil':        ( ('tamil'    , '10003', ), ),
        'hindi':        ( ('hindi'    , '10004', ), ),
        'telugu':       ( ('telugu'   , '10251', ), ),
        'malayalam':    ( ('malayalam', '10238', ), ),
        'kannada':      ( ('kannada'  , '10284', ), ),
        'punjabi':      ( ('punjabi'  , '10000', ), ),
        'bengali':      ( ('bengali'  , '10308', ), ),
        'marathi':      ( ('marathi'  , '10293', ), ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            index = film.entity('music.cooltoad.com', 'index', lang, item[0], item[0], 'music/category.php?id=' + item[1])
            if_new(index, INDEX_DAYS, self.do_index, item)

    def do_index(self, index, html, item):
        for match in re.findall('<A HREF="\?id=(\d+)[^<]*</A>\s*<SMALL>\((\d+)\)</SMALL>', html, re.IGNORECASE + re.S + re.UNICODE):
            for page in range(1, (int(match[1])+39)/40):
                key = match[0] + "-" + str(page)
                subindex = film.entity(index.db, 'index', index.lang, key, key, 'music/category.php?id=' + match[0] + '&page=' + str(page) + '&order=title')
                if_new(subindex, INDEX_DAYS, self.do_subindex, item)

    def do_subindex(self, subindex, html, item):
        for match in re.findall('song\.php\?id=(\d+).*?>(.*?)</A>', html, re.S + re.UNICODE):
            song = film.entity(subindex.db, 'song', subindex.lang, match[0], match[1], 'music/song.php?id=' + match[0])


"""
# ================================================================================================================================
class MusicPlugin:
    lang = {
        'tamil'     : (  '8', ),
        'hindi'     : (  '2', ),
        'telugu'    : ( '12', ),
        'kannada'   : ( '11', ),
        'malayalam' : ( '15', ),
        'punjabi'   : ( '16', ),
    }
    attr = {
        'Artists'           : ( 'person', 'actor'       ),
        'Director'          : ( 'person', 'director'    ),
        'Music Director'    : ( 'person', 'composer'    ),
        'Year'              : ( 'year',   'year'        ),
    }

    def __init__(self, lang):
        for item in self.lang.get(lang, ()):
            htmlload.url('http://www.musicplug.in/get_language.php?langid=' + item + '&movietypeid=1')
            for letter in ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0-9'):
                index = film.entity('www.musicplug.in', 'index', lang, letter, letter, 'movie_list.php?letter=' + letter)
                if_new(index, INDEX_DAYS, self.do_index, item)

    def do_index(self, index, html, item):
        for match in re.findall("href='(songs.php\?movieid=(\d+))'[^>]*?>([^<]*?)</a>", html, re.S + re.UNICODE):
            movie = film.entity(index.db, 'movie', index.lang, match[1], match[2], match[0])
            if_new(movie, MOVIE_DAYS, self.do_movie, item)

    def strip_name(self, name):
        name = re.sub(r'\s*\-\s*:.*$', '', name) # TODO: Remove stuff like 'Ponnumani -  :  anbaigreat song' or 'Pasumpon - Thamarai :  wht a superp song'
        return name

    def do_movie(self, movie, html):
        for match in re.findall('<td class=.main.><b>([A-Za-z]*)\s*:\s*</b>(.*?)</td>', html, re.S + re.UNICODE):
            item = self.attr[match[0]]
            for submatch in re.findall('href=.(artist_movie_list.php?artistid=(\d+))[^>]*>([^<]*)</a>', match[1], re.S + re.UNICODE):
                film.relate(movie, item[1], film.entity(movie.db, item[0], movie.lang, 'a-' + submatch[1], submatch[2], submatch[0]))
            if item[0] == 'year':
                film.relate(movie, item[1], film.entity(movie.db, item[0], '', match[1], match[1], ''))

        for match in re.findall("javascript:flashplayer\('(\d+)','(\d+)'\). class='main'>\s*<b>([^<]*)</b>(.*?)</td>", html, re.S + re.UNICODE):
            song = film.entity(movie.db, 'song', movie.lang, match[0] + "," + match[1], match[2], 'multiple_song_flashplayer.php?songid=' + match[0] + '&id=' + match[1])
            for submatch in re.findall('href=.(singers_songlist.php?artistid=(\d+))[^>]*>(.*?)</a>', match[1], re.S + re.UNICODE):
                film.relate(song, 'singer', film.entity(song.db, 'person', song.lang, 's-' + submatch[1], submatch[2], submatch[0]))
"""

for lang in film.__langs__:
    MusicIndiaOnline(lang)
    Raaga(lang)
    Smashits(lang)
    Oosai(lang)
    Dishant(lang)

for lang in film.__langs__:
    Cooltoad(lang)
#    MP3Hungama(lang)
