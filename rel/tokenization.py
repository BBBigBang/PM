'''
Created on 2017.7.1

@author: ZZH
'''

def token_common(text):
    
    text = text.replace('cannot','can not')\
                .replace("can't",'can not')\
                .replace("won't",'will not')\
                .replace("n't",' not')\
                .replace("where's",'where is')\
                .replace("there's",'there is')\
                .replace(" '", " ")\
                .replace("'s ", " 's ")\
                .replace("s' ", "s 's ")\
                .replace("' ", " ")\
                .replace('/',' / ')\
                .replace('--',' -- ')\
                .replace('+ ',' + ')\
                .replace('>',' > ')\
                .replace('<',' < ')\
                .replace(';', ' ; ')\
                .replace(':', ' : ')\
                .replace('?', ' ? ')\
                .replace("]", " ] ")\
                .replace("[", " [ ")\
                .replace("}", " } ")\
                .replace("{", " { ")\
                .replace("(", " ( ")\
                .replace(")", " ) ")\
                .replace('!', ' ! ')\
                .replace('#', ' # ')\
                .replace('$', ' $ ')\
                .replace('&', ' & ')\
                .replace('*', ' * ')\
                .replace('@', ' @ ')\
                .replace('~', ' ~ ')\
                .replace('|', ' | ')\
                .replace('%', ' % ')\
                .replace('^', ' ^ ')\
                .replace('"', '')\
                .replace('-', ' - ')\
                .replace(',',' , ')\
                .replace('. ',' . ')\
                .replace('  ', ' ')\
                .replace('  ', ' ').lower()

    return text


def token_4_parser(text):
    '''
        these items have ambiguity
        like she's will stands for she has and she is
        
                .replace("'d",' would')\
                .replace("she's",'she is')\
                .replace("who's",'who is')\
                .replace("what's",'what is')\
                .replace("that's",'that is')\
                .replace("shan't",'shall not')\
                .replace("who's",'who is')\
                .replace("he's",'he is')\
                .replace("it's",'it is')\
    '''
    text = text.replace('cannot','can not')\
            .replace("can't",'can not')\
            .replace("won't",'will not')\
            .replace("n't",' not')\
            .replace("'re",' are')\
            .replace("I'm",'I am')\
            .replace("'ll",' will')\
            .replace("let's",'let us')\
            .replace("where's",'where is')\
            .replace("there's",'there is')\
            .replace("'ve",' have')\
            .replace(" '", " ")\
            .replace("'s ", " 's ")\
            .replace("s' ", "s 's ")\
            .replace("' ", " ")\
            .replace('&quot;', '')\
            .replace('/ ',' ')\
            .replace(', ',' , ')\
            .replace('+',' + ')\
            .replace('>',' > ')\
            .replace('<',' < ')\
            .replace(';', ' ; ')\
            .replace(':', ' : ')\
            .replace('?', ' ? ')\
            .replace("]", " ] ")\
            .replace("[", " [ ")\
            .replace("}", " } ")\
            .replace("{", " { ")\
            .replace("(", " ( ")\
            .replace(")", " ) ")\
            .replace('!', ' ! ')\
            .replace('&', ' & ')\
            .replace('*', ' * ')\
            .replace('%', ' % ')\
            .replace('@', '')\
            .replace('~', '')\
            .replace('#', '')\
            .replace('$', '')\
            .replace('^', '')\
            .replace('"', '')\
            .replace('  ', ' ')\
            .replace('  ', ' ')
    
    return text


if __name__ == '__main__':
    dir = 'C:/Users/ZZH/Desktop/'
    
    writer = open(dir + 'liver.inst.token', 'a')

    count = 0
    list = []
    for line in open(dir + 'liver.inst'):
        list.append(token_common(line.strip()))
        count += 1
        if count % 1000 == 0:
            writer.write('\n'.join(list) + '\n')
            list = []
    writer.write('\n'.join(list))
    writer.close()
    print count
