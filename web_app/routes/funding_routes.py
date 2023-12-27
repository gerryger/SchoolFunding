from flask import Blueprint, render_template, current_app , session, redirect

from web_app.routes.wrappers import authenticated_route
from web_app.routes.forms.create_funding_form import CreateFundingForm

funding_routes = Blueprint("funding_routes", __name__)

@funding_routes.route("/create-funding", methods=['GET'])
@authenticated_route
def create_funding():
    service = current_app.config["FIREBASE_SERVICE"]
    fund_types = service.fetch_fund_types()
    form = CreateFundingForm()
    form.fundTypeSelect.choices = [(ft['type'], ft['type'].lower().replace("_"," ")) for ft in fund_types]
    return render_template("new_create_funding.html", form=form, fund_types=fund_types)

@funding_routes.route("/create-funding", methods=["POST"])
def handle_create_funding():
    form = CreateFundingForm()
    if form.validate_on_submit():
        title = form.fundraiserTitle.data
        print("TITLE: ", title)
    else:
        print(form.errors)
        return redirect("/create-funding")

@funding_routes.route("/donation", methods=['GET'])
def donate_now():
    return render_template("donation.html")