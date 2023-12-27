import os
from flask import Blueprint, render_template, current_app , session, redirect

from web_app.routes.wrappers import authenticated_route
from web_app.routes.forms.create_funding_form import CreateFundingForm
from werkzeug.utils import secure_filename

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
        service = current_app.config["FIREBASE_SERVICE"]
        title = form.fundraiserTitle.data
        print("TITLE: ", title)
        imageFilename = secure_filename(form.fundingImageThumbnail.data.filename)
        temporaryImageFilePath = os.path.join(
                current_app.root_path, 'static', 'images', 'fundhub', 'upload-temp', imageFilename
            )
        form.fundingImageThumbnail.data.save(temporaryImageFilePath)

        # upload to firebase storage
        service.upload_to_bucket(imageFilename)
        os.remove(temporaryImageFilePath)

        fundType = form.fundTypeSelect.data
        currency = form.currencySelect.data
        country = form.countryText.data
        targetAmount = form.targetAmount.data
        description = form.fundingDescription.data

        endDate = form.finishedDate.data
        formattedEndDate = endDate.strftime('%Y-%m-%d %H:%M')

        
    else:
        print(form.errors)
        return redirect("/create-funding")

@funding_routes.route("/donation", methods=['GET'])
def donate_now():
    return render_template("donation.html")