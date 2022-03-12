#!/usr/bin/env python3

import argparse
import datetime
import json
import pathlib
import requests
import shutil
import sys

from ShadowbanAlertsConfig import SCREEN_NAMES, MENTION_TO, WEBHOOK_URL


# Twitter Shadowban Test の API URL
API_URL = 'https://shadowban.hmpf.club/'

# 前回のデータを保存する JSON のパス
JSON_PATH = pathlib.Path(sys.argv[0]).parent / 'ShadowbanAlerts.json'

# バージョン情報
VERSION = '1.1.0'


def main():

    # ターミナルの横幅
    # conhost.exe だと -1px しないと改行されてしまう
    terminal_columns = shutil.get_terminal_size().columns - 1

    # 引数解析
    parser = argparse.ArgumentParser(
        description='Twitter アカウントへのシャドウバンが開始・解除された時に Discord に通知するツール',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='version', help='バージョン情報を表示する', version='ShadowbanAlerts version ' + VERSION)
    parser.parse_args()

    # 行区切り
    print('=' * terminal_columns)
    print('***** ShadowbanAlerts *****')
    print('=' * terminal_columns)

    if len(SCREEN_NAMES) == 0:
        print('Error: スクリーンネームが指定されていません。')
        print('=' * terminal_columns)
        sys.exit(1)

    # Discord に通知を投げる関数
    def SendDiscord(screen_name:str, ban_name:str, is_banning:bool):
        now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        if is_banning is True:
            message = f'https://twitter.com/{screen_name} への ⚠**{ban_name}**⚠ が **{now}** から開始されました。'
        else:
            message = f'https://twitter.com/{screen_name} への ⚠**{ban_name}**⚠ は **{now}** に解除されました。'
        message = (f'<@{MENTION_TO}> ' if MENTION_TO is not None else '') + message  # メンション先を設定
        requests.post(WEBHOOK_URL, json={
            'username': 'ShadowbanAlerts',
            'content': message,
        })

    # まだ JSON がなければ初期値を設定
    if JSON_PATH.exists() is False:
        initial_save_data = {'LastUpdatedAt': datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
        for screen_name in SCREEN_NAMES:
            initial_save_data[screen_name.replace('@', '')] = {
                'SearchSuggestionBan': False,
                'SearchBan': False,
                'GhostBan': False,
                'ReplyDeboosting':  False,
            }
        with open(JSON_PATH, mode='w', encoding='utf-8') as fp:
            json.dump(initial_save_data, fp, ensure_ascii=False, indent=4)

    # 今回 JSON に保存するデータが入る辞書
    with open(JSON_PATH, mode='r', encoding='utf-8') as fp:
        save_data = json.load(fp)

    # 前回の更新時刻
    print(f'Last Updated Time : {save_data["LastUpdatedAt"]}')
    print(f'Current Time      : {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
    print('-' * terminal_columns)

    # スクリーンネームごとに実行
    for screen_name in SCREEN_NAMES:

        # @ が付かない方に統一
        screen_name = screen_name.replace('@', '')

        # 前回の値がないなら初期値をセット
        if screen_name not in save_data:
            save_data[screen_name] = {
                'SearchSuggestionBan': False,
                'SearchBan': False,
                'GhostBan': False,
                'ReplyDeboosting':  False,
            }

        # API にリクエスト
        response = requests.get(f'{API_URL}{screen_name}', headers={'user-agent': f'ShadowbanAlerts/{VERSION}'})
        if response.status_code != 200:
            print(f'Error: Twitter Shadowban Test の API アクセスに失敗しました。(HTTP Error {response.status_code})')
            print('-' * terminal_columns)
            continue
        if 'protected' in response.json()['profile'] and response.json()['profile']['protected'] == True:
            print(f'Error: @{screen_name} は鍵アカウントです。')
            print('-' * terminal_columns)
            continue
        if 'suspend' in response.json()['profile'] and response.json()['profile']['suspended'] == True:
            print(f'Error: @{screen_name} は凍結されています。')
            print('-' * terminal_columns)
            continue
        if response.json()['profile']['exists'] == False:
            print(f'Error: @{screen_name} は存在しません。')
            print('-' * terminal_columns)
            continue
        result = response.json()['tests']

        # BAN されているかの値を取得
        is_search_suggestion_ban = not result['typeahead']  # BAN のとき False になる
        is_search_ban = not result['search']  # BAN のとき False になる
        is_ghost_ban = result['ghost']['ban']
        is_reply_deboosting = result['more_replies']['ban']
        print(f'@{screen_name} Shadowban Status:')
        print(f'  Search Suggestion Ban : {is_search_suggestion_ban}')
        print(f'  Search Ban            : {is_search_ban}')
        print(f'  Ghost Ban             : {is_ghost_ban}')
        print(f'  Reply Deboosting      : {is_reply_deboosting}')

        # 前回の値と異なっていたら通知を送る
        if save_data[screen_name]['SearchSuggestionBan'] != is_search_suggestion_ban:
            SendDiscord(screen_name, 'Search Suggestion Ban', is_search_suggestion_ban)
        if save_data[screen_name]['SearchBan'] != is_search_ban:
            SendDiscord(screen_name, 'Search Ban', is_search_ban)
        if save_data[screen_name]['GhostBan'] != is_ghost_ban:
            SendDiscord(screen_name, 'Ghost Ban', is_ghost_ban)
        if save_data[screen_name]['ReplyDeboosting'] != is_reply_deboosting:
            SendDiscord(screen_name, 'Reply Deboosting', is_reply_deboosting)

        # データをセット
        save_data[screen_name] = {
            'SearchSuggestionBan': is_search_suggestion_ban,
            'SearchBan': is_search_ban,
            'GhostBan': is_ghost_ban,
            'ReplyDeboosting':  is_reply_deboosting,
        }

        print('-' * terminal_columns)

    # 前回の更新時刻を更新
    save_data['LastUpdatedAt'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    # 次回実行時用にデータを保存しておく
    with open(JSON_PATH, mode='w', encoding='utf-8') as fp:
        json.dump(save_data, fp, ensure_ascii=False, indent=4)

    print('Completed.')
    print('=' * terminal_columns)


if __name__ == '__main__':
    main()
