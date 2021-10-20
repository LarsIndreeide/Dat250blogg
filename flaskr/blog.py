
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)



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
        title = request.form['title']
        body = request.form['body']
        body2 = request.form['body2']
        pris = request.form['pris']
        error = None 

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, body2, pris, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, body, body2, pris, g.user['id'] )
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

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        body2 = request.form['body2']
        pris = request.form['pris']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, body2 = ?, pris = ?'
                ' WHERE id = ?',
                (title, body, body2, pris, id)
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

