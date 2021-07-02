SYSTEM_PROMPT = 'S| '
USER_PROMPT = 'U| '

def main():
    print('Starting Dialogue Agent...')
    print(SYSTEM_PROMPT+'Each time are finished talking, type RET twice.')
    while True:
        s = '\n'.join(iter(lambda: input(USER_PROMPT), ''))
        # TODO: 空白文字 or 改行だけ、などの場合は以降の処理を行わないようにした方が良さそう
        fw = s.split()[-1].replace('。', '').replace('、', '').replace('.', '').replace(',', '')
        if fw in {'またね', 'じゃあね', '終わり', 'おわり', 'finish', 'end', 'exit', 'see you'}:
            break
        # おうむ返しBotをまずは実装した方が良さそう？
        print(s)
    print(SYSTEM_PROMPT+fw)
    print('Finished Dialogue Agent...')

if __name__ == '__main__':
    main()