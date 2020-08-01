from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, BooleanField, TextAreaField, DateField
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
    """ Form for cutting a slab """
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
    slab_num = IntegerField("Slab Number", validators=[DataRequired()])
    length = FloatField('Length')
    width = FloatField('Width')
    type_id = SelectField('Slab Type', validators=[DataRequired()])

class JobForm(FlaskForm):
    """ Form to Add/Edit Jobs """
    name=StringField('Name', validators=[DataRequired()])
    po_number=StringField('PO Number')
    contractor_id=SelectField('Contractor/Customer', validators=[DataRequired()])
    sf=FloatField('Squared Feet')
    edge_id=SelectField('Edge Detail')
    lf=IntegerField('linear feet')
    installation_date=DateField(' Installation Date',format='%Y-%m-%d')
    fabrication_date=DateField('Fabrication Date',format='%Y-%m-%d')
    notes=TextAreaField('Notes')