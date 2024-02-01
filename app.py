from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import requests

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Webtoon(db.Model):
    titleId = db.Column(db.Integer, primary_key=True, nullable=False)
    titleName = db.Column(db.String, nullable=True)
    author = db.Column(db.String, nullable=True)
    thumbnail_url = db.Column(db.String, nullable=True)
    up = db.Column(db.String, nullable=True)
    rest = db.Column(db.String, nullable=True)
    bm = db.Column(db.String, nullable=True)
    adult = db.Column(db.String, nullable=True)
    starScore = db.Column(db.Float, nullable=True)
    viewCount = db.Column(db.String, nullable=True)
    openToday = db.Column(db.String, nullable=True)
    potenUp = db.Column(db.String, nullable=True)
    bestChallengeLevelUp = db.Column(db.String, nullable=True)
    finish = db.Column(db.String, nullable=True)
    new = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Webtoon {self.titleName}>"


with app.app_context():
    db.create_all()


def update_webtoon_data():
    r = requests.get(
        'https://comic.naver.com/api/webtoon/titlelist/weekday?week=dailyPlus&order=user%27')
    rjson = r.json()
    webtoon_data = rjson['titleList']

    # 데이터베이스 초기화
    db.session.query(Webtoon).delete()

    for webtoon_info in webtoon_data:
        webtoon = Webtoon(
            titleId=webtoon_info['titleId'],
            titleName=webtoon_info['titleName'],
            author=webtoon_info['author'],
            up=str(webtoon_info['up']),
            thumbnail_url=webtoon_info['thumbnailUrl'],
            rest=str(webtoon_info['rest']),
            bm=str(webtoon_info['bm']),
            adult=str(webtoon_info['adult']),
            starScore=webtoon_info['starScore'],
            viewCount=str(webtoon_info['viewCount']),
            openToday=str(webtoon_info['openToday']),
            potenUp=str(webtoon_info['potenUp']),
            bestChallengeLevelUp=str(webtoon_info['bestChallengeLevelUp']),
            finish=str(webtoon_info['finish']),
            new=str(webtoon_info['new'])
        )
        db.session.add(webtoon)

    db.session.commit()

@app.route("/")
def home():
    name = '최지웅'
    motto = "행복해서 웃는게 아니라 웃어서 행복합니다."

    # Check if the Webtoon table is empty and update data if necessary
    if not db.session.query(Webtoon).first():
        update_webtoon_data()

    # Retrieve the top 10 webtoons based on star score
    webtoon_data = db.session.query(Webtoon).order_by(
        func.random()).limit(10).all()

    # Format webtoon data for rendering in the template
    webtoon_data = [
        {
            "titleId": webtoon.titleId,
            "titleName": webtoon.titleName,
            "author": webtoon.author,
            "thumbnailUrl": webtoon.thumbnail_url,
            "up": webtoon.up,
            "rest": webtoon.rest,
            "bm": webtoon.bm,
            "adult": webtoon.adult,
            "starScore": webtoon.starScore,
            "viewCount": webtoon.viewCount,
            "openToday": webtoon.openToday,
            "potenUp": webtoon.potenUp,
            "bestChallengeLevelUp": webtoon.bestChallengeLevelUp,
            "finish": webtoon.finish,
            "new": webtoon.new
        }
        for webtoon in webtoon_data
    ]

    # Add webtoon_data to the context dictionary
    context = {
        "name": name,
        "motto": motto,
        "webtoon_data": webtoon_data
    }

    return render_template('motto.html', data=context)


@app.route('/webtoon')
def webtoon():
    # Check if the Webtoon table is empty
    if not db.session.query(Webtoon).first():
        update_webtoon_data()  # If empty, update the data

    webtoon_data = db.session.query(Webtoon).order_by(
        Webtoon.starScore.desc()).limit(10).all()

    # Load data from the database
    webtoon_data = [
        {
            "titleId": webtoon.titleId,
            "titleName": webtoon.titleName,
            "author": webtoon.author,
            "thumbnailUrl": webtoon.thumbnail_url,
            "up": webtoon.up,
            "rest": webtoon.rest,
            "bm": webtoon.bm,
            "adult": webtoon.adult,
            "starScore": webtoon.starScore,
            "viewCount": webtoon.viewCount,
            "openToday": webtoon.openToday,
            "potenUp": webtoon.potenUp,
            "bestChallengeLevelUp": webtoon.bestChallengeLevelUp,
            "finish": webtoon.finish,
            "new": webtoon.new
        }
        for webtoon in webtoon_data
    ]
    return render_template('webtoon.html', data=webtoon_data)


@app.route('/webtoon/reload')
def webtoon_reload():
    update_webtoon_data()
    return redirect(url_for('webtoon'))


if __name__ == '__main__':
    app.run()
