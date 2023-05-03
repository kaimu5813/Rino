import asyncio
import json
import websockets

import MeCab
import markovify

from misskey import Misskey


TOKEN='d0t3WO65gXveACoZLKqYKkhZ1JneOcQG'

mk = Misskey('voskey.icalo.net', i=TOKEN)
MY_ID = mk.i()['id']
WS_URL='wss://voskey.icalo.net/streaming?i='+TOKEN
hatudou = 0
count_count = 0
i = 1

print("起動したよ！")
#test_note = mk.notes_create(text=":igyo_wide_yuru:")

async def runner():
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({
            "type":"connect",
            "body":{
                    "channel":"localTimeline",
                    "type":"something",
                    "id": "foobar",
                    "body":{
                        "some":"thing"
                    }
            }
        }))

        while True:
            data = json.loads(await ws.recv())
            #print(data)
            if data['body']['body']['cw'] == None:
                if data['type'] == 'channel':
                    if data['body']['type'] == 'note':
                        note = data['body']['body']
                        await on_note(note) , search(note)
            else:
                pass

                """if data['body']['type'] == 'followed':
                    user = data['body']['body']
                    await on_follow(user)"""
#使わないけど残しておくコード
"""def first(note):
    if os.stat('./text/igyourino.csv').st_size == 0:
        timeline = note['text']
        print(timeline)
        with open('./text/igyourino.csv',encoding='utf-8',mode='w') as hatugen:
            hatugen.write(timeline.replace("\n",""))"""


async def on_note(note):
    if note.get('mentions'):
        if MY_ID in note['mentions']:
            cheer = note['text']
            if 'ほめて' in cheer:
                mk.notes_create(text = ":igyo_wide_yuru:", reply_id=note['id'])
            elif not 'ほめて' in cheer:
                mk.notes_create(text = ":rino_yuru:", reply_id=note['id'])
            else:
                pass

def main():
    with open('./text/igyourino.txt',encoding='utf-8',mode='r') as fire:
        text = fire.read().replace("\n",",")
    
    mecab = MeCab.Tagger()

    # 上手く解釈できない文字列を定義しておく
    breaking_chars = ['(', ')', '[', ']', '"', "'",'!',".","？","‼️","/","?",'@','<','>',"$","%"," "]
    # 最終的に1文に収めるための変数
    splitted_hatugen = ''

    for line in text:
        #print('Line : ', line)
        # lineの文字列をパースする
        parsed_nodes = mecab.parseToNode(line)

        while parsed_nodes:
            try:
                # 上手く解釈できない文字列は飛ばす
                if parsed_nodes.surface not in breaking_chars:
                    splitted_hatugen += parsed_nodes.surface
                # 句読点以外であればスペースを付与して分かち書きをする
                if parsed_nodes.surface != '。' and parsed_nodes.surface != '、':
                    splitted_hatugen += ' '
                # 句点が出てきたら文章の終わりと判断して改行を付与する
                if parsed_nodes.surface == '。':
                    splitted_hatugen += '\n'
            except UnicodeDecodeError as error:
                print('Error:',error)
                print('Error : ', line)
            except KeyError as key_error:
                print('Error:',key_error)
            finally:
                # 次の形態素に上書きする。なければNoneが入る
                parsed_nodes = parsed_nodes.next

            #print('解析結果 :\n', splitted_meigen)

    # マルコフ連鎖のモデルを作成
    model = markovify.NewlineText(splitted_hatugen, state_size=2)
        
    # 文章を生成する
    sentence = model.make_sentence(tries=25)
        
    if sentence is not None:
        # 分かち書きされているのを結合して出力する
        print('---------------------------------------------------')
        print(''.join(sentence.split()))
        mk.notes_create(sentence.replace(" ","").replace(",",""))
        print('---------------------------------------------------')
        with open ('./text/igyourino.txt',encoding='utf-8',mode='w') as hatugen:
            hatugen.write("")
    else:
        print('None')
        with open ('./text/igyourino.txt',encoding='utf-8',mode='w') as hatugen:
            hatugen.write("")


def search(note):
    if note.get('text'):
        global hatudou , count_count,i
        tax = note['text']
        hatudou = hatudou + 1
        print(hatudou)
        if hatudou == 5:
            count_count = count_count + 1
            hatudou = 0
            print(count_count)
            hatugen = tax
            if i == count_count:
                with open('./text/igyourino.txt',encoding='utf-8',mode='a') as hatugen:
                    hatugen.write("'" + tax.replace("\n","").replace(" ","")+ "。" + "'" + "," + "\n")
                print("ノートにかいたよ~")
                i = i + 1
            #n回学習したらmainを起動してノートする
            if count_count == 10:
                if __name__ == '__main__':
                    main()
                    count_count = 0
                    i = 1

                        
    

#schedule.every(1).minutes.do(search)
"""async def on_follow(user):
    try:
        mk.users_followers(user_id=['id'])
    except:
        pass"""             

#asyncio.get_event_loop().run_until_complete(runner())
loop = asyncio.get_event_loop()
loop.run_until_complete(runner())
loop.run_until_complete(search())
#while True:
        #schedule.run_pending()
        #sleep(1)
