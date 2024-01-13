import os
from flask import Blueprint, render_template, current_app , session, redirect

from datetime import datetime, timezone
from web_app.routes.wrappers import authenticated_route
from web_app.routes.forms.create_funding_form import CreateFundingForm
from werkzeug.utils import secure_filename

funding_routes = Blueprint("funding_routes", __name__)

def generate_timestamp():
    return datetime.now(tz=timezone.utc)

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
        service = current_app.config["FIREBASE_SERVICE"]
        title = form.fundraiserTitle.data
        print("TITLE: ", title)
        imageFilename = secure_filename(form.fundingImageThumbnail.data.filename)
        temporaryImageFilePath = os.path.join(
                current_app.root_path, 'static', 'images', 'fundhub', 'upload-temp', imageFilename
            )
        form.fundingImageThumbnail.data.save(temporaryImageFilePath)

        # upload to firebase storage
        imageUrl = service.upload_to_bucket(imageFilename)
        os.remove(temporaryImageFilePath)

        fundType = form.fundTypeSelect.data
        currency = form.currencySelect.data
        country = form.countryText.data
        targetAmount = float(form.targetAmount.data)
        description = form.fundingDescription.data
        funder = session["current_user"]["name"]

        endDate = form.finishedDate.data
        formattedEndDate = endDate.strftime('%Y-%m-%d %H:%M')

        funding_info = {
            "title": title,
            "description": description,
            "finished_at": endDate,
            "target_amount": targetAmount,
            "funder": funder,
            "current_amount": 0,
            "image_url": imageUrl,
            "currency": currency,
            "country": country,
            "type": fundType,
            "created_at": generate_timestamp()
        }

        service.create_funding(funding_info)

        return redirect("/new-home")
    else:
        print(form.errors)
        return redirect("/create-funding")

@funding_routes.route("/donation/<string:funding_id>", methods=['GET'])
def donate_now(funding_id):
    service = current_app.config["FIREBASE_SERVICE"]
    funding = service.fetch_funding_by_id(funding_id)
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
    return render_template("donation.html", funding=funding, paypal_client_id=paypal_client_id)

@funding_routes.route("/causes", methods=['GET'])
def causes():
    service = current_app.config["FIREBASE_SERVICE"]
    fundings = service.fetch_fundings()
    return render_template("causes.html", fundings=fundings)