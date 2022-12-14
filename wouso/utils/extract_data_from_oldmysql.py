import MySQLdb as mdb


class Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.dbc = self.db.cursor()

    def __getitem__(self, item):
        self.dbc.execute("select * from %s limit %s, 1" % (self.name, item))
        return self.dbc.fetchone()

    def __len__(self):
        self.dbc.execute("select count(*) from %s" % (self.name))
        length = int(self.dbc.fetchone()[0])
        return length


db = mdb.connect(db="baza", user='root', passwd='mihnea', charset='latin1')

questions = {}
records = Table(db, "questionschall")
for i in range(len(records)):
    a = records[i][1].encode('latin-1')
    b = unicode(a, 'utf-8')
    questions[int(records[i][0])] = b

# print questions

answers = {}
records = Table(db, "anschall")
for i in range(len(records)):
    qid = int(records[i][1])

    if answers.get(qid) is None:
        answers[qid] = []

    ans = records[i][2].encode('latin-1')
    ans = unicode(ans, 'utf-8')
    answers[qid].append((ans, records[i][3]))

import codecs
with codecs.open("chall.txt", 'w', 'utf-8') as f:
    for qid in questions.keys():
        f.write('? ' + questions[qid] + '\n')

        for ans in answers[qid]:
            if ans[1] == 1:
                type = '+'
            else:
                type = '-'
            f.write(type + ' ' + ans[0] + '\n')
        f.write('\n')
