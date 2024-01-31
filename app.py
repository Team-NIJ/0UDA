from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def home():
    name = '최지웅'
    motto = "행복해서 웃는게 아니라 웃어서 행복합니다."

    context = {
        "name": name,
        "motto": motto,
    }
    return render_template('motto.html', data=context)

@app.route('/webtoon')
def webtoon():
    
    r = requests.get('https://comic.naver.com/api/webtoon/titlelist/weekday?week=dailyPlus&order=user%27')
    rjson = r.json()

    webtoon_data = rjson['titleList']

    return render_template('webtoon.html', data=webtoon_data)

if __name__ == '__main__':
    app.run()

