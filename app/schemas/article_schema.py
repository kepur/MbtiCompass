a=list('fasd....fasd...fatr..eth2.2.g.a')
def only_char(listchar,sep):
    while sep in listchar:
        del listchar[listchar.index(sep)]
        return listchar
nub_char=only_char(a,'f')
print(a)
print(nub_char)
