from sqlobject import *
import re, sys, film, trans

def dump(filename, table):
    print filename
    file = open(filename, 'w')
    cols = list(col.dbName for col in table.sqlmeta.columnList)
    file.write("\t".join(cols) + "\n")
    for row in table.select():
        vals = (unicode(row.__getattribute__(col)) for col in cols)
        file.write("\t".join(vals).encode('utf8') + "\n")
    file.close()


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
    file.write("\t".join(('db', 'num', 'trans', 'movie', 'song', 'year', 'musicdirector')) + "\n")
    for item in dbMap:
        for sng in film.Entity.selectBy(db = item[0], type = 'song', lang=lang):
            # Get the first movie for the song. Unfortunately, MusicIndiaOnline has MULTIPLE movies (misspelt) accessing the same song
            mov     = film.Relation.selectBy(tgt=sng, rel='song')[0].src
            db      = item[1]
            num     = str(sng.num)
            movie   = mov.name
            song    = sng.name
            trans   = mov.tran + ' ' + sng.tran
            yearrel = mov and film.Relation.selectBy(src=mov, rel='year').getOne(None)
            year    = yearrel and yearrel.tgt.name or ''
            md      = ",".join((rel.tgt.name for rel in film.Relation.selectBy(src=mov, rel='composer'))) or ''
            file.write("\t".join((db, num, trans, movie, song, year, md)).encode('utf8') + "\n")
    file.close()

def makeMP3search(filename, lang):
    dbMap = (
        ('music.cooltoad.com'       , 'C', ),
    )

    file = open(filename, 'w')
    file.write("\t".join(('db', 'num', 'trans', 'movie', 'song', 'year', 'musicdirector')) + "\n")
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


def translate():
    for item in film.Entity.select():
        if item.type in ('song', 'movie', 'person'):
            item.tran = trans.trans(item.name)
        else:
            item.tran = ''

film.connect()

def process(langs, what):
    for lang in langs:
        print lang
        if what.find('plain'):  makesearch(lang + ".search.txt", lang)
        if what.find('mp3'):    makeMP3search(lang + "mp3.search.txt", lang)

def dumpAll():
    dump("Entity.txt", film.Entity)
    dump("Relation.txt", film.Relation)
    dump("Identity.txt", film.Identity)

# translate()
# dumpAll()
# process(sys.argv[1:], 'plain+mp3')
# process(film.__langs__, 'plain+mp3')

dumpAll()

# Create a load(SQLObject) that loads from a dumped file and APPENDS to the table
