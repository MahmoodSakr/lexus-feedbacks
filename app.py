from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)  # app instance of the Flask

# this var will play as a flag to switch between the development or production environment
# ENV = 'dev'
ENV = 'production'

# setup the development configuration
if ENV == 'dev':
    app.debug = True
    app.port = 5000
    # set the DB URI / DB Location : 'protocol://user:password@server:port/DB_name'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/lexusDB'
else:
    # setup the production configuration for the deployment server like heroku
    app.debug = False
    # production db url
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://yyaebbsekdtvmv:5f6d6b474b9bfe108f0efe39c27442e485b95c0d153292558d2807cae63cbef2@ec2-34-228-154-153.compute-1.amazonaws.com:5432/d40duk0nb1e0lp"

# setup mail credentials
sender = "sakrservices2020@gmail.com"
password = "a000000*"

# update app with mail configuration
app.config.update(
    DEBUG=True,
    # Email Setting
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=sender,
    MAIL_PASSWORD=password
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Integrate SQLAlchemy layer with the Flask app to control your db with it
db = SQLAlchemy(app)
""" 
db = SQLAlchemy()
db.init_app(app)
"""

# create the db model through an oop class to define the schema of your feedbacks table


class Feedback(db.Model):
    """sumary_line
    define your table name and the columns details (type,constrains), and there values will be added by the constrctor when an object of this class is instantiated
    """
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200))
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())  # Text hold data more than String

# constructor will construct an object/db row to assign the values to this row with respect
# to the class parameters representing the columns name
    def __init__(self, customer, dealer, rating, comments):
        # you don't need to add the id as PK , it will be added automatically
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments


@app.route("/", methods=['get'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['post'])
def submit():
    if request.method == 'POST':  # check the type of request through the request module
        # request can grap the form elements value through its attributes name
        customerName = request.form['customer']
        dealerName = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        #print(customerName, dealerName,rating,comments)
        # check for the non values for the customer text field or dealer select options
        if customerName == "" or dealerName == "":
            return render_template("index.html", message="Please enter the Cutomer and Dealer names !")
            # the message is sent as template parameter to the index page and you should access
            # its values by {{message}} or {{message|safe}} for the security means
        # check for if the customer is exist on the db
        if db.session.query(Feedback).filter(Feedback.customer == customerName).count() == 0:
            # the customer is not existed in the database, so we will add its details as new customer row
            newCustomer = Feedback(customerName, dealerName, rating, comments)
            db.session.add(newCustomer)
            db.session.commit()
            # send email with the feedback
            sendMail(customerName, dealerName, rating, comments)
            print("new customer has been added with its feedback successfuly")
            return render_template('success.html',
                                   message1="Thank you "+customerName,
                                   message2="Your feedback has been reached to us.")
        else:
            print("an existing customer feedback has been added successfuly")
            return render_template("success.html",
                                   message1="Thank you "+customerName,
                                   message2="Your feedback has been added to your previous feedbacks")

# update app configuration
app.config.update(
    DEBUG=True,
    # Email Setting
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=sender,
    MAIL_PASSWORD=password
)

# instatiate the Mail class
mail = Mail(app)

def sendMail(customerName, dealerName, rating, comments):
    sender = "sakrservices2020@gmail.com" 
    recipients = ["ma7mouedsakr@gmail.com"]
    subject = "New feedback from {}".format(customerName)
    body = f'''Customer name : {customerName} \n
    Deal Name : {dealerName} \n
    Customer Rating : {rating}
    Feedback : \n 
    {comments}   '''
    msg = Message(subject=subject,body=body, sender=sender, recipients=recipients)
    # other mail option field you can edit it with msg.field=value;
    # msg.add_recipient("mahmoudsakr@ci.menofia.edu.eg")
    # msg.html = body_html
    # with app.open_resource("myphoto.jpg") as fp:
    #     msg.attach("myphoto.jpg", "image/jpg", fp.read())
    mail.send(msg)


if __name__ == '__main__':
    app.run()