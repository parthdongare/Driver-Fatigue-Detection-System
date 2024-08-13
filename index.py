from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    Response
)
import cv2
from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from drowsinessDetection import drowsy_prediction,reset_score
from app import create_app,db,login_manager,bcrypt
from models import User
from forms import login_form,register_form
stopCamera = False
scoresTrackList = []
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
@app.route("/", methods=("GET","POST"),strict_slashes=False)
def index():
    global stopCamera
    stopCamera = True
    return render_template("index.html",
        text="Home",
        title="Home",
        btn_action="Home"
        )
@app.route("/precaution", methods=("GET","POST"),strict_slashes=False)
def cond():
    global stopCamera
    stopCamera = True
    return render_template("cond.html",
        text="Home",
        title="Home",
        btn_action="Home"
        )

@app.route("/predictor", methods=("GET", "POST"), strict_slashes=False)
def pred():
    global stopCamera
    stopCamera = False
    def gen():
        video = cv2.VideoCapture(0)
        while True:
            global stopCamera
            if(stopCamera):
                stopCamera = False
                video.release()
                cv2.destroyAllWindows()
                break
            success, image = video.read()
            try:
                image,score = drowsy_prediction(image)
                global scoresTrackList
                scoresTrackList.append(score)
                if(len(scoresTrackList)>30):
                    scoresTrackList.pop(0)
                ret, jpeg = cv2.imencode('.jpg', image)
                frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                cv2.waitKey(1)
            except:
                print("error")
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route("/score/reset", methods=("GET", "POST"), strict_slashes=False)
def resetScore():
    reset_score()
    global scoresTrackList
    scoresTrackList = []
    return Response("ok")
@app.route("/stop-camera",methods=("GET","POST"),strict_slashes=False)
def stopCam():
    global stopCamera
    stopCamera = True
    reset_score()
    global scoresTrackList
    scoresTrackList = []
    return Response("ok")
@app.route("/scoreslist",methods=("GET","POST"),strict_slashes=False)
def scoreslist():
    global scoresTrackList
    return Response(str(scoresTrackList))
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    global stopCamera
    stopCamera = True
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            print(user.pwd,form.pwd.data)
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )



@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    global stopCamera
    stopCamera = True
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
