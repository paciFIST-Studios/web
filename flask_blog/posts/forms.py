from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FieldList
from wtforms.validators import DataRequired, ValidationError

from flask_blog.models import Tag


class EditPostForm(FlaskForm):
    # note: we can add profanity filters in the validation step
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Submit')


class EditPostTagsForm(FlaskForm):
    tags = FieldList(StringField('Tag', validators=[]))

    submit = SubmitField('Update Tags')

    def validate_tags(self, tags):
        pass
        #tag = Tag.query.filter_by(tag=tags)
        #already_taken = User.query.filter_by(username=username.data).first()
        #if already_taken:
        #    raise ValidationError('Tag already exists!')

