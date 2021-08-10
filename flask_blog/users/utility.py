import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message

from flask_blog import mail


def save_profile_image(image):
    # make a random file name (but not a random file extension) in order to prevent
    # profile picture file path collisions
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(image.filename)
    image_file_name = random_hex + ext
    image_storage_path = os.path.join(current_app.root_path, 'static/user_profile_images', image_file_name)

    # resize image to 125x125
    storage_size = (125, 125)
    _image = Image.open(image)
    _image.thumbnail(storage_size)

    # save from the resized file
    _image.save(image_storage_path)
    return image_file_name

def remove_stored_profile_image(filename):
    # note: don't delete our default image.
    # happens the first time user attempts to update their profile
    if filename == 'default.jpg':
        return
    _image = os.path.join(current_app.root_path, 'static/user_profile_images', filename)
    if os.path.isfile(_image):
        os.remove(_image)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Flask Blog: Password Reset Request'
                  , sender='noreply@demo.com'
                  , recipients=[user.email])
    msg.body = f'''{ user.username },
Use this link to reset your password.
{url_for("users.password_reset", token=token, _external=True)}

If you did not make this request, please contact the web administrator.

If you did make the request, but you don't want to reset your password, you can ignore this email.

Sincerely,
FlaskBlog Team
'''
    mail.send(msg)
