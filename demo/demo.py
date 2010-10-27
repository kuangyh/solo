from solo import *

atomfeed = Q + {
    'title' : 'Atom feed',
    'entry' : Q >> {
        'title' : Q['title'],
        'link' : {
            'href' : I['http://mail.qq.com/mail/{0}.html'.format](Q['id']),
            'rel' : 'alternative'
            },
        'author' : {
            'name' : Q['username'],
            'mail' : I['{0}@mail.qq.com'.format](Q['username']).lower()
            }
        }
    }

if __name__ == '__main__':
    ctx = makectx()
    data = [
        { 'title' : 'hahaha', 'id' : 123, 'username' : 'Ben' },
        { 'title' : 'asdgasegaseg', 'id' : 234, 'username' : 'Ligil' }
        ]

    print (~atomfeed)(data)
