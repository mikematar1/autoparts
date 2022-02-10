from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///sales.db"
db = SQLAlchemy(app);
issignedin=False
password="1234"


    
class loan(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    model = db.Column(db.String(120))
    make=db.Column(db.String(120))
    year = db.Column(db.Integer)
    cname = db.Column(db.String(120))
    price = db.Column(db.Integer)
    date = db.Column(db.String(30))
    bodypart=db.Column(db.String(120))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __init__(self,make,model,year,cname,price,date,bodypart,userid):
        self.make=make
        self.model=model
        self.year=year
        self.cname=cname
        self.price=price
        self.date=date
        self.bodypart=bodypart
        self.user_id=userid
class paidloan(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    loanid = db.Column(db.Integer)
    model = db.Column(db.String(120))
    make=db.Column(db.String(120))
    year = db.Column(db.Integer)
    cname = db.Column(db.String(120))
    price = db.Column(db.Integer)
    date = db.Column(db.String(30))
    bodypart=db.Column(db.String(120))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __init__(self,make,model,year,cname,price,date,bodypart,userid,loanid):
        self.make=make
        self.model=model
        self.year=year
        self.cname=cname
        self.price=price
        self.date=date
        self.bodypart=bodypart
        self.user_id=userid
        self.loanid=loanid
class user(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120))
    number=db.Column(db.String(120))
    location=db.Column(db.String(300))
    loans = db.relationship('loan',backref='user',lazy=True)
    paidloans = db.relationship('paidloan',backref='user',lazy=True)
    def __init__(self,name,number,location):
        self.name=name
        self.number=number
        self.location=location

class item(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    model = db.Column(db.String(120))
    make=db.Column(db.String(120))
    year = db.Column(db.Integer)
    cname = db.Column(db.String(120))
    price = db.Column(db.Integer)
    date = db.Column(db.String(30))
    bodypart=db.Column(db.String(120))
    def __init__(self,make,model,year,cname,price,date,bodypart):
        self.make=make
        self.model=model
        self.year=year
        self.cname=cname
        self.price=price
        self.date=date
        self.bodypart=bodypart

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/admit",methods=['POST','GET'])
def admit():
    passs = request.form['pass']
    global issignedin
    if passs==password:

        issignedin=True
        return redirect("/admin")
    else:
        return redirect("/")


@app.route("/admin")
def admin():
    if issignedin:
        return render_template("admin.html")
    else:
        return redirect("/")

@app.route("/tsales")
def tsales():
    items = item.query.filter_by(date=datetime.now().strftime("%D")).all()
    users = user.query.all()
    loans = loan.query.filter_by(date=datetime.now().strftime("%D")).all()
    return render_template("tsales.html",items=items,users=users,loans=loans)

@app.route("/profile/<int:id>",methods=['POST','GET'])
def profile(id):
    loaner = user.query.get(id)
    return render_template("profile.html",loaner=loaner)
@app.route("/delete/<int:id>",methods=['POST','GET'])
def delete(id):
    loaner = user.query.get(id)
    for x in loaner.loans:
        db.session.delete(x)
    for x in loaner.paidloans:
        db.session.delete(x)
    db.session.commit()
    db.session.delete(loaner)
    db.session.commit()
    return redirect("/profiles")

@app.route("/makepayment/<int:id>",methods=['POST','GET'])
def makepayment(id):
    amount = request.form['money']
    amount=int(amount)
    loaner = user.query.get(id)
    loanlist = loaner.loans
    loannlist = list(map(lambda x: x.price,loanlist))
    idlist = list(map(lambda x: x.id,loanlist))
    loanslist = list(zip(idlist,loannlist))
    
    for x,y in loanslist:
        exists = paidloan.query.filter_by(loanid=x).all()!=[]
        if(amount>0):
            a=loan.query.get(x)
            if amount>=y:
                
                db.session.delete(a)
                if exists:
                    paidloan.query.filter_by(loanid=x).first().price+=y
                else:
                    i = paidloan(make=a.make,model=a.model,year=a.year,cname=a.cname,price=a.price,date=a.date,bodypart=a.bodypart,userid=a.user_id,loanid=x)
                    db.session.add(i)
                amount=amount-y
            else:
                y=y-amount
                loan.query.get(x).price=y
                if exists:
                    paidloan.query.filter_by(loanid=x).first().price+=amount
                else:
                    i = paidloan(make=a.make,model=a.model,year=a.year,cname=a.cname,price=amount,date=a.date,bodypart=a.bodypart,userid=a.user_id,loanid=x)
                    db.session.add(i)                 
                amount=0
                
        else:
            break
        db.session.commit()
    return redirect(f"/profile/{id}")
                



@app.route("/profiles")
def profiles():
    users = user.query.all()
    return render_template("profiles.html",users=users)

@app.route("/summary/<int:tframe>/<string:make>/<string:model>/<int:year>/<string:bodypart>",methods=['POST','GET'])
def summary(tframe,make,model,year,bodypart):
    output=[]
    date_list = [(datetime.today() - timedelta(days=x)).strftime("%D") for x in range(tframe) ]
    if tframe!=0:
        for d in date_list:
            if make=='None' and bodypart=='None' and year==0:
                f=item.query.filter_by(date=d).all()
            elif make=='None' and bodypart=='None':
                f=item.query.filter_by(date=d,year=year).all()
            elif make=='None' and year==0:
                f=item.query.filter_by(date=d,bodypart=bodypart).all()
            elif bodypart=='None' and year==0:
                f=item.query.filter_by(date=d,make=make,model=model).all()

            elif bodypart=='None':
                f=item.query.filter_by(date=d,make=make,year=year,model=model).all()
            elif make=='None':
                f=item.query.filter_by(date=d,bodypart=bodypart,year=year).all()
            elif year==0:
                f=item.query.filter_by(date=d,bodypart=bodypart,make=make,model=model).all()
            else:
                f=item.query.filter_by(date=d,bodypart=bodypart,make=make,model=model,year=year).all()
            output+=f
    else:
        if make=='None' and bodypart=='None' and year==0:
            f=item.query.all()
        elif make=='None' and bodypart=='None':
            f=item.query.filter_by(year=year).all()
        elif make=='None' and year==0:
            f=item.query.filter_by(bodypart=bodypart).all()
        elif bodypart=='None' and year==0:
            f=item.query.filter_by(make=make,model=model).all()

        elif bodypart=='None':
            f=item.query.filter_by(make=make,year=year,model=model).all()
        elif make=='None':
            f=item.query.filter_by(bodypart=bodypart,year=year).all()
        elif year==0:
            f=item.query.filter_by(bodypart=bodypart,make=make,model=model).all()
        else:
            f=item.query.filter_by(bodypart=bodypart,make=make,model=model,year=year).all()
        output+=f
    

    return render_template("summary.html",items=output)
@app.route("/CNL")
def CNL():
    return render_template("cnl.html")
@app.route("/loans")
def loans():
    tloans = loan.query.all()
    return render_template("loans.html",tloans=tloans)

@app.route("/adduser",methods=['POST','GET'])
def adduser():
    name= request.form['name']
    number=request.form['number']
    location=request.form['location']
    u = user(name=name,number=number,location=location)
    for i in range(15):
        db.session.add(u)
    db.session.commit()
    return redirect("/profiles")

@app.route("/additem",methods=['POST','GET'])
def additem():
    
    make= request.form['make']
    
    model=request.form['model']
    year=int(request.form['year'])
    cname=request.form['customername']
    price=request.form['itemprice']
    bodypart = request.form['test']
    date = datetime.now().strftime("%D")
    isloan = request.form['loanboolean']
    if int(isloan)==1:
        loanerid = request.form['loaner']
        loaner = user.query.get(loanerid)
        cname=loaner.name
        print(loaner.loans)
        l = loan(make=make,model=model,year=year,cname=cname,price=price,date=date,bodypart=bodypart,userid=int(loanerid))
        db.session.add(l)
        
        db.session.commit()
    else:
        loaner=None
        i = item(make=make,model=model,year=year,cname=cname,price=price,date=date,bodypart=bodypart)
        db.session.add(i)
        db.session.commit()
    return redirect('/tsales')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)