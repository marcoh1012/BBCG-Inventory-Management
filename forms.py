from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

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
    cut_amount = FloatField('Amount used in %', validators=[DataRequired(), NumberRange(min=0,max=100,message=" Amount must be between 0 and 100")])
    length = FloatField('New Length',validators=[DataRequired("Please Enter New Length")])
    width = FloatField('New Width', validators=[DataRequired("Please Enter New Width")])
    location = StringField("Slab Location", validators=[Optional()])
    rem = BooleanField("Rem")
    notes = TextAreaField('Notes')


class SlabForm(FlaskForm):
    """ Form to add/edit slabs """
    picture = FileField('Picture')
    vendor = SelectField('Vendor')
    color = SelectField('Slab Color')
    batch_num = IntegerField("Batch Number", validators=[DataRequired()])
    slab_num = IntegerField("Slab Number", validators=[DataRequired()])
    length = FloatField('Length',validators=[Optional()])
    width = FloatField('Width', validators=[Optional()])
    location = StringField("Slab Location", validators=[Optional()])
    type_id = SelectField('Slab Type', validators=[DataRequired()])

class JobForm(FlaskForm):
    """ Form to Add/Edit Jobs """
    name=StringField('Name', validators=[DataRequired()])
    po_number=StringField('PO Number')
    contractor_id=SelectField('Contractor/Customer', validators=[DataRequired()])
    square_feet =FloatField('Square Feet')
    installation_date=DateField(' Installation Date yyyy-mm-dd', validators=[Optional()])
    fabrication_date=DateField('Fabrication Date yyyy-mm-dd', validators=[Optional()])
    notes=TextAreaField('Notes')

##### Adding Info to Jobs Forms ####

class AddCutoutForm(FlaskForm):
    """ Add Cutout to Job Form """

    cutout = SelectField('Cutout Name', validators=[DataRequired()])
    number = IntegerField('Number of Cutouts', validators=[DataRequired()])

class AddEdgeForm(FlaskForm):
    """" Add Edge Detail to Job Form """

    edge = SelectField('Edge Name', validators=[DataRequired()])
    lf = IntegerField('Linear Feet', validators=[DataRequired()])


##### Admin Page Forms #####

class adminPageForm(FlaskForm):
    """ form for thing on admin page """

    id=IntegerField('ID')
    name=StringField('Name', validators=[DataRequired('Please Enter a Name')])

class EdgeForm(FlaskForm):
    """ form for a new edge type """

    id=IntegerField('ID')
    name=StringField('Name', validators=[DataRequired('Please Enter a Name')])
    type=StringField(' Edge Type')
class BarcodeAndSFForm(FlaskForm):
    """ Form to scan in barcode and add sf to job """

    label = IntegerField('Barcode #', validators=[DataRequired()])
    job_sf=FloatField('Job Square Footage', validators=[DataRequired('Please Enter a number'), NumberRange(min=0)])

class AddSlabSF(FlaskForm):
    """ square footage used from this slab """

    job_sf=FloatField('Job Square Footage', validators=[DataRequired('Please Enter a number'), NumberRange(min=0)])