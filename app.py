from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import requests
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class ViewCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.postID'), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)

    board = db.relationship('Posts', backref=db.backref(
        'view_count_relation', uselist=False))

    def __repr__(self):
        return f'노래 ID {self.board_post_id}의 조회수: {self.count}'


class Users(db.Model):
    userID = db.Column(db.Integer, primary_key=True, nullable=False)
    loginID = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)  # 이메일 중복 방지
    profile_img = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return f"<Users {self.userID}>"


class Posts(db.Model):
    postID = db.Column(db.Integer, primary_key=True, nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey(
        'users.userID'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Posts {self.postID}>"


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
    webtoon_data = db.session.query(Webtoon).filter(Webtoon.adult == 'False').order_by(
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
        func.random()).limit(40).all()

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


@app.route("/total/")
def total():
    post_list = Posts.query.all()
    return render_template('total.html', data=post_list)


@app.route("/total/<userID>")
def render_total_filter(userID):
    filter_list = Posts.query.filter_by(userID=userID).all()
    return render_template('total.html', data=filter_list)


@app.route("/music/")
def music():
    music_list = Posts.query.filter_by(type="music").all()
    return render_template('music.html', data=music_list)


@app.route("/movie/")
def movie():
    movie_list = Posts.query.filter_by(type="movie").all()
    return render_template('movie.html', data=movie_list)


@app.route("/instagram/")
def instagram():
    instagram_list = Posts.query.filter_by(type="instagram").all()
    return render_template('instagram.html', data=instagram_list)


@app.route("/total/create/")
def total_create():
    # Get user ID from the session
    user_id_from_session = session.get('user_id')

    if user_id_from_session:  # Check if the user is logged in
        # Access the user ID from the session
        userID_receive = user_id_from_session
        title_receive = request.args.get("title")
        image_receive = request.args.get("image_url")
        content_receive = request.args.get("content")
        url_receive = request.args.get("url")
        type_receive = request.args.get("type")

        current_time = datetime.datetime.now()

        # Use the user ID in your database operation
        post = Posts(userID=userID_receive, title=title_receive, image_url=image_receive,
                     content=content_receive, url=url_receive, type=type_receive, date=current_time)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('render_total_filter', userID=userID_receive))
    else:
        # Redirect the user to the login page if not authenticated
        return redirect(url_for('login'))


@app.route("/delete_post/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('total'))


@app.route('/webtoon/<titleId>')
def webtoon_specific(titleId):
    webtoon_data = Webtoon.query.filter_by(titleId=titleId).first()
    return render_template('detail_webtoon.html', data=webtoon_data)

# 계정 회원가입 페이지 (찬)


@app.route("/signup")
def signup():
    return render_template('signup.html')

# 계정 로그인 페이지 (찬)


@app.route("/login")
def login():
    return render_template('login.html')

# 계정 회원가입 (찬)


@app.route("/signup/create", methods=["POST"])
def signup_create():
    loginID_receive = request.form.get("loginID")
    password_receive = request.form.get("password")
    name_receive = request.form.get("name")
    nickname_receive = request.form.get("nickname")
    email_receive = request.form.get("email")
    profile_img_receive = request.form.get("profile_img")
    isNotNone = Users.query.filter_by(loginID=loginID_receive).first()

    # 중복ID가 있는 경우
    if isNotNone is not None:
        duplicate_message = True
        return render_template('signup.html', duplicate_message=duplicate_message)
    # 중복ID가 없는 경우
    else:
        hashed_password = generate_password_hash(
            password_receive, method='pbkdf2:sha256')
        newUsers = Users(loginID=loginID_receive,
                         password=hashed_password,
                         name=name_receive,
                         nickname=nickname_receive,
                         email=email_receive,
                         profile_img=profile_img_receive)
        db.session.add(newUsers)
        db.session.commit()

    return redirect(url_for('signup'))


# 토큰화 (찬)
app.config['SECRET_KEY'] = 'your_secret_key'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 세션에서 토큰 가져오기
        token = session.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(userID=data['userID']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# 계정 로그인 (찬)


@app.route("/login/login", methods=["POST"])
def login_login():
    loginID_receive = request.form.get("loginID")
    password_receive = request.form.get("password")
    user = Users.query.filter_by(loginID=loginID_receive).first()

    if user and check_password_hash(user.password, password_receive):
        session['user_id'] = user.userID
        session['token'] = jwt.encode({'userID': user.userID, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        yesExist_message = True
        return render_template('login.html', yesExist_message=yesExist_message, token=session['token'])
    else:
        notExist_message = True
        return render_template('login.html', notExist_message=notExist_message)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('token', None)

    return redirect(url_for('login'))


# 토큰관련 (찬)
@app.route("/protected", methods=["GET"])
@token_required
def protected(current_user):
    # 세션에서 사용자 ID 가져오기
    user_id_from_session = session.get('user_id')

    # 세션의 사용자 ID와 토큰의 사용자 ID 비교
    if user_id_from_session == current_user.userID:
        return jsonify({'message': f'안녕하세요 {current_user.name}, 보호된 경로입니다!'})
    else:
        return jsonify({'message': '유효하지 않은 세션입니다. 다시 로그인해주세요.'}), 401

# 토큰확인용 temp.html로 이동하는 라우팅


@app.route('/check_token')
def check_token():
    print(session['user_id'])
    return render_template('check_token.html')

# 노래 조회수 증가 함수


@app.route("/increase_view_count", methods=['POST', 'GET'])
def increase_view_count():
    board_post_id = request.form.get('board_post_id')
    board = Posts.query.get(board_post_id)
    if board:
        view_count = ViewCount.query.filter_by(
            board_post_id=board_post_id).first()
        if view_count:
            view_count.count += 1
        else:
            view_count = ViewCount(board_post_id=board_post_id, count=1)
            db.session.add(view_count)
        db.session.commit()
        return jsonify({"message": "View count increased successfully"})
    else:
        return jsonify({"error": "Song not found"}), 404


if __name__ == '__main__':
    app.run()
