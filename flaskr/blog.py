
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename


from flaskr.auth import login_required
from flaskr.db import get_db
import os


ALLOWED_EXTENSIONS = {'png', 'jpg'}
UPLOAD_FOLDER = ('/templates/blog/images')
bp = Blueprint('blog', __name__)





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/' , methods=('GET', 'POST', 'COMMENT'))
def index():


    db = get_db( )
    posts = db.execute(
        'SELECT *'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    comments = db.execute(
        'SELECT *'
        ' FROM comment c JOIN user u ON c.cAuthor_id = u.id'
        ' ORDER BY cCreated DESC'
        ).fetchall()
    if request.method == 'POST':
        ctext = request.form['commenttext']
        ctid = request.form['ctid']
        
        error = None

        if not ctext:
            error = 'Comment text is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (commenttext, postid, cAuthor_id)'
                ' VALUES (?, ?, ?)',
                (ctext, ctid, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    else:
        return render_template('blog/index.html', posts=posts, comments=comments)




@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':

        app = Flask(__name__, instance_relative_config=True)
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass



        title = request.form['title']
        body = request.form['body']
        body2 = request.form['body2']
        pris = request.form['pris']
        file = request.files['file']
        error = None 

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploadpath = os.path.join('./flaskr/static/', 'images')
            print(uploadpath)
            #url = images.url(filename)
 
            
            file.save(os.path.join(uploadpath, filename))

            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, body2, pris, file, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (title, body, body2, pris, file.filename, g.user['id'] )
            )
            db.commit()
            return redirect(url_for('blog.index'))


        
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT *'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    app = Flask(__name__, instance_relative_config=True)
       

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        body2 = request.form['body2']
        pris = request.form['pris']
        file = request.files['file']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            uploadpath = os.path.join('Dat250blogg/static/images', 'images')
            
            file.save(os.path.join(uploadpath, filename))
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, body2 = ?, pris = ?, file = ?'
                ' WHERE id = ?',
                (title, body, body2, pris, file.filename, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index')) 

