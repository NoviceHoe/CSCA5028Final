#!/usr/bin/env python3

from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main():
    return '''
     <form action="/echo_user_input" method="POST">
         <input value= "Stay Hydrated Calculator">
         <br>
         <input value="Enter your weight (lbs)">
         <input name="user_weight">
         <br>
         <input value="Enter you latitude">
         <input name="user_lat">
         <br>
         <input value="Enter you longitude">
         <input name="user_lon">
         <br>
         <input type="submit" value="Submit!">
     </form>
     '''
    input_weight = request.form.get("user_weight", "")
    input_lat = request.form.get("user_lat", "")
    input_lon = request.form.get("user_lon", "")


@app.route("/echo_user_input", methods=["POST"])
def echo_input():

    return "You should be drinking" + calc_water+ "(oz) today given an daily high temp of" + high_temp
