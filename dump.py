import re, sys, film, trans

def makesearch(filename, lang):
    dbMap = (
        ('ww.smashits.com'          , 'S', ),
        ('www.musicindiaonline.com' , 'M', ),
        ('www.raaga.com'            , 'R', ),
        ('www.oosai.com'            , 'O', ),
#        ('www.dhingana.com'         , 'G', ),
#        ('www.mp3hungama.com'       , '3', ),
#        ('www.bollyfm.net'          , 'B', ),
#        ('www.dishant.com'          , 'D', ),
#        ('www.musicplug.in'         , 'P', ),
#        ('music.cooltoad.com'       , 'C', ),
#        ('www.youtube.com'          , 'Y', ),
    )

    file = open(filename, 'w')
    file.write("\t".join(('db', 'num', 'trans', 'movie', 'song', 'year', 'musicdirector', 'lyricist', 'actor', 'lyrics', 'singer')) + "\n")
    for item in dbMap:
        for sng in film.Entity.selectBy(db = item[0], type = 'song', lang=lang):
            # Get the first movie for the song. Unfortunately, MusicIndiaOnline has MULTIPLE movies (misspelt) accessing the same song
            mov      = film.Relation.selectBy(tgt=sng, rel='song')[0].src
            db       = item[1]
            num      = str(sng.num)
            movie    = mov.name
            song     = sng.name
            trans    = mov.tran + ' ' + sng.tran
            movierel = list(rel for rel in film.Relation.selectBy(src=mov))
            songrel  = list(rel for rel in film.Relation.selectBy(src=sng))
            year     = ','.join((rel.tgt.name for rel in movierel if rel.rel == 'year')) or ''
            md       = ','.join((rel.tgt.name for rel in movierel if rel.rel == 'composer')) or ''
            lyricist = ','.join((rel.tgt.name for rel in movierel if rel.rel == 'lyricist')) or ''
            actor    = ','.join((rel.tgt.name for rel in movierel if rel.rel == 'actor')) or ''
            lyrics   = ','.join((rel.tgt.url  for rel in songrel  if rel.rel == 'lyrics')) or ''
            singer   = ','.join((rel.tgt.url  for rel in songrel  if rel.rel == 'singer')) or ''
            file.write("\t".join((db, num, trans, movie, song, year, md, lyricist, actor, lyrics, singer)).encode('utf8') + "\n")
    file.close()

def makeMP3search(filename, lang):
    dbMap = (
        ('music.cooltoad.com'       , 'C', ),
    )

    file = open(filename, 'w')
    file.write("\t".join(('db', 'num', 'trans', 'movie', 'song', 'year', 'musicdirector', 'lyricist', 'actor')) + "\n")
    for item in dbMap:
        for sng in film.Entity.selectBy(db = item[0], type = 'song', lang=lang):
            # Get the first movie for the song. Unfortunately, MusicIndiaOnline has MULTIPLE movies (misspelt) accessing the same song
            db      = item[1]
            num     = str(sng.num)
            movie   = ''
            song    = sng.name.replace('^', '').replace('~', '')
            trans   = sng.tran
            year    = ''
            md      = ''
            file.write("\t".join((db, num, trans, movie, song, year, md)).encode('utf8') + "\n")
    file.close()


def retranslate():
    for item in film.Entity.select():
        if item.type in ('song', 'movie', 'person'):
            item.tran = trans.trans(item.name)
        else:
            item.tran = ''

def process(langs, what):
    for lang in langs:
        print lang
        if what.find('plain') >= 0:  makesearch(lang + ".search.txt", lang)
        if what.find('mp3')   >= 0:  makeMP3search(lang + "mp3.search.txt", lang)

film.connect()
process(sys.argv[1:] or film.__langs__, 'plain')
# retranslate()

# Create a load(SQLObject) that loads from a dumped file and APPENDS to the table
