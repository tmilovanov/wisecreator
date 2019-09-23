import sqlite3

with sqlite3.connect('WordWise.kll.en.en.db') as f:
    lemmas = f.execute('SELECT id,lemma FROM lemmas').fetchall()
    senses = dict(f.execute('SELECT display_lemma_id,id FROM senses WHERE id>0').fetchall()[::-1])

display_lemma_ids = senses.keys()

csv = []

print('Please wait a moment.')

for id_, word in lemmas:
    if id_ in display_lemma_ids:
        id = senses[id_]
        if ' ' in word or "'" in word:
            csv.append('"{0}",{1}'.format(word, id))
        else:
            csv.append('{0},{1}'.format(word, id))

with open('all.csv', 'wb') as f:
    f = f.write('\n'.join(csv).encode('utf-8'))

print('Success!')
