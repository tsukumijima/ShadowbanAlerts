
# ShadowbanAlerts

<img width="100%" src="https://user-images.githubusercontent.com/39271166/158080038-1cab35fb-862b-4782-9e48-aa3bb2102a08.png"><br>

Twitter アカウントへのシャドウバンが開始・解除された時に Discord に通知するツールです。

## 導入

Windows でも Linux でも動くと思いますが、動作確認は Linux でしかしていません。  
事前に Python 3.10 / pip / pipenv / Git がインストールされていることが前提です。

```Shell
git clone https://github.com/tsukumijima/ShadowbanAlerts.git
cd ShadowbanAlerts/
cp ShadowbanAlertsConfig.example.py ShadowbanAlertsConfig.py
PIPENV_VENV_IN_PROJECT="true" pipenv sync
```

## 設定

`ShadowbanAlertsConfig.py` は設定ファイルです。

`SCREEN_NAMES` にはシャドウバンをチェックするアカウントのスクリーンネーム (@から始まるID) を指定します。  
Python のリスト形式になっているので、例にある通り複数のアカウントを指定できます。

`MENTION_TO` にはメンション先の Discord アカウントの ID を指定します。  
ID は Discord の設定から開発者モードを有効化し、自分のユーザーアイコンを右クリックで出てくる [IDをコピー] から取得できます。
`MENTION_TO = None` に設定するとメンションされません。

`WEBHOOK_URL` には Discord の Webhook URL を設定します。  
Discord の Webhook URL は別途取得してください。`https://discord.com/api/webhooks/～` のような URL になります。

## 実行

単独で実行させる場合は、`python3.10 ./ShadowbanAlerts.py` と実行します。  
この時点でいずれかのアカウントがシャドウバンされている場合は、Discord の Webhook を設定したチャンネルに通知が送信されます。

ShadowbanAlerts は常時起動機能を持ちません。継続的に実行させたい場合は、Cron やタスクスケジューラなどに ShadowbanAlerts を登録する必要があります。  
以下に Cron で1分おきに ShadowbanAlerts を実行させる例を示します (`ubuntu` は一般ユーザー)。

```
*/1 * * * * /home/ubuntu/ShadowbanAlerts/.venv/bin/python /home/ubuntu/ShadowbanAlerts/ShadowbanAlerts.py
```

## License

[MIT License](License.txt)
