import sys
sys.path.append('/app/')
from model.agent import GPT2Agent

SYSTEM_PROMPT = '] '
USER_PROMPT = '> '

def main() -> None:
    print("Loading Dialogue Agent...")
    agent = GPT2Agent("data/gpt-2")  # 対話エージェントの初期化

    print(SYSTEM_PROMPT+'Each time are finished talking, type RET twice.')
    while True:
        s = '\n'.join(iter(lambda: input(USER_PROMPT), ''))
        # TODO: 空白文字 or 改行だけ、などの場合は以降の処理を行わないようにした方が良さそう
        print(s)
        r = agent.reply(s)
        print(SYSTEM_PROMPT+r, end='\n\n')
    print(SYSTEM_PROMPT+fw)
    print('Finished Dialogue Agent...')

if __name__ == '__main__':
    main()