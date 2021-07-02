import sys
print(sys.path.append('/app/'))
from model.agent import Agent

SYSTEM_PROMPT = ''
USER_PROMPT = '> '

def main():
    agent = Agent()  # 対話エージェントの初期化

    print('Starting Dialogue Agent...')
    print(SYSTEM_PROMPT+'Each time are finished talking, type RET twice.')
    while True:
        s = '\n'.join(iter(lambda: input(USER_PROMPT), ''))
        # TODO: 空白文字 or 改行だけ、などの場合は以降の処理を行わないようにした方が良さそう
        fw = s.split()[-1].replace('。', '').replace('、', '').replace('.', '').replace(',', '')
        if fw in {'またね', 'じゃあね', '終わり', 'おわり', 'finish', 'end', 'exit', 'see you'}:
            break
        # TODO: 今は入力をそのまま返すだけなので、要修正
        r = agent.reply(s)
        print(SYSTEM_PROMPT+r, end='\n\n')
    print(SYSTEM_PROMPT+fw)
    print('Finished Dialogue Agent...')

if __name__ == '__main__':
    main()