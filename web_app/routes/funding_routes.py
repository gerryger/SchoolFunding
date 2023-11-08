from flask import Blueprint, render_template, current_app , session

from web_app.routes.wrappers import authenticated_route

funding_routes = Blueprint("funding_routes", __name__)

@funding_routes.route("/create-funding")
@authenticated_route
def create_funding():
    service = current_app.config["FIREBASE_SERVICE"]
    fund_types = service.fetch_fund_types()
    return render_template("create_funding.html", fund_types=fund_types)