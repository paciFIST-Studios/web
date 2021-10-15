from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ViewStoryFragmentsForm(FlaskForm):
    dev_name = StringField('DevName', validators=[DataRequired()])

    dev_notes = TextAreaField('DevNotes', validators=[])

    pub_name = StringField('PubName', validators=[])

    pub_description = TextAreaField('PubDescription', validators=[])

    tags = StringField('Tags', validators=[])

    citation = StringField('Citation', validators=[])



class EditStoryFragmentsForm(FlaskForm):
    dev_name = StringField('DevName', validators=[DataRequired()])

    dev_notes = TextAreaField('DevNotes', validators=[])

    pub_name = StringField('PubName', validators=[])

    pub_description = TextAreaField('PubDescription', validators=[])

    tags = StringField('Tags', validators=[])

    citation = StringField('Citation', validators=[])

    @staticmethod
    def validate_dev_name(dev_name):
        already_taken = StoryFragment.query.filter_by(dev_name=dev_name.data).first()
        if already_taken:
            raise ValidationError('This entry already exists!')

    @staticmethod
    def validate_pub_name(pub_name):
        already_taken = StoryFragment.query.filter_by(pub_name=pub_name.data).first()
        if already_taken:
            raise ValidationError('This entry already exists!')

    @staticmethod
    def check_banned_words(line):
        if 'fuck' in line:
            raise ValidationError('Profanity filter has discovered a banned word.  Please recheck entry and remove profanity')

