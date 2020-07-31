from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, BooleanField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class CreateUserForm(FlaskForm):
    """ Create new user form """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    type = SelectField('Account Type')
    
class ScanBarcodeForm(FlaskForm):
    """ Form to scan in barcode """

    label = IntegerField('Barcode #', validators=[DataRequired()])

class CutSlabForm(FlaskForm):
    picture = FileField('Picture')
    job = SelectField('Job Name')
    cut_amount = FloatField('Amount used in %', validators=[DataRequired(), NumberRange(min=0,max=100,message=" Amount must be between 0 and 1")])
    notes = TextAreaField('Notes')



class SlabForm(FlaskForm):
    """ Form to add/edit slabs """
    picture = FileField('Picture')
    vendor = SelectField('Vendor')
    color = SelectField('Slab Color')
    batch_num = IntegerField("Batch Number", validators=[DataRequired()])
    length = FloatField('Length')
    width = FloatField('Width')
    type_id = SelectField('Slab Type', validators=[DataRequired()])
    completed = BooleanField('Entire Slab Used')
