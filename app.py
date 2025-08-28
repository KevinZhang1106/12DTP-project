"""
Flask application for League of Legends champion statistics website.
"""

# Imports
import sqlite3                                                                                              

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
import bcrypt

from config import ADMIN_PASSWORD_HASH

# Initialize Flask app and secret key for sessions
app = Flask(__name__)
app.secret_key = "secretkey" 


# Home Page Route
@app.route("/") 
def home():
    session.clear() # clears any existing session data
    conn = sqlite3.connect("champions.db") # connects to database
    cur = conn.cursor()
    
    # gets the lane_id where the pickrate is the highest for each champ_id
    cur.execute( 
        """
        SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate
        FROM ChampionStats cs
        JOIN (
            SELECT champ_id, MAX(pickrate) AS max_pickrate
            FROM ChampionStats
            GROUP BY champ_id
        ) max_stats ON cs.champ_id = max_stats.champ_id
        JOIN Champions c ON cs.champ_id = c.champ_id
        WHERE cs.pickrate = max_stats.max_pickrate
        """
    )
    searchbar = cur.fetchall() # gets all rows as a list of tuples
    conn.close()
    return render_template("home.html", searchbar=searchbar) # renders home.html with searchbar data


# Champion stats page route
@app.route("/champions/<int:champ_id>/<int:lane_id>")
def championstatspage(champ_id, lane_id): # gets the champ_id and lane_id values from the url and passes them to the function
    session.clear()
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()

    # gets stats for the specific champion and lane
    cur.execute(
        """
        SELECT cs.champ_id, cs.lane_id, cs.winrate, cs.pickrate, cs.banrate,
               l.lane_name, c.champ_name, c.passive_ability,
               c.q_ability, c.w_ability, c.e_ability, c.r_ability
        FROM ChampionStats cs
        JOIN Champions c ON cs.champ_id = c.champ_id
        JOIN Lanes l ON cs.lane_id = l.lane_id
        WHERE cs.champ_id = ? AND cs.lane_id = ?
        """,
        (champ_id, lane_id),
    )
    championstats = cur.fetchone() # gets the next row as a tuple

    if championstats is None:
        abort(404)

    # gets the lane_id where the pickrate is the highest for each champion
    cur.execute( 
        """
        SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate
        FROM ChampionStats cs
        JOIN (
            SELECT champ_id, MAX(pickrate) AS max_pickrate
            FROM ChampionStats
            GROUP BY champ_id
        ) max_stats ON cs.champ_id = max_stats.champ_id
        JOIN Champions c ON cs.champ_id = c.champ_id
        WHERE cs.pickrate = max_stats.max_pickrate
        """
    )
    searchbar = cur.fetchall()

    cur.execute("SELECT cs.lane_id FROM ChampionStats cs WHERE cs.champ_id = ?", (champ_id,)) # gets all lanes for a specific champ_id
    available_lanes = [lane[0] for lane in cur.fetchall()] # puts all the lane_id into a list

    cur.execute("SELECT lane_id, lane_name FROM Lanes") # gets the all the lanes (top, jungle, mid, bot, support)
    all_lanes = cur.fetchall()

    conn.close()
    return render_template( 
        "champions.html",
        championstats=championstats,
        searchbar=searchbar,
        available_lanes=available_lanes,
        all_lanes=all_lanes,
        current_lane=lane_id,
        champ_id=champ_id,
    )


# Champion ranking page route
@app.route("/championranking/<int:lane_id>") 
def championrankingpage(lane_id):
    session.clear()
    sort_by = request.args.get("sort_by", "winrate") # gets the sort_by value in the url, if there is none then default to winrate

    if sort_by not in ("winrate", "pickrate", "banrate"):
        abort(404)

    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    query = f""" 
        SELECT cs.champ_id, c.champ_name, cs.winrate, cs.pickrate, cs.banrate 
        FROM ChampionStats cs
        JOIN Champions c ON cs.champ_id = c.champ_id
        WHERE cs.lane_id = ?
        ORDER BY cs.{sort_by} DESC
    """
    cur.execute(query, (lane_id,)) # gets winrate, pickrate and banrate and sorts them by the sort_by value for a specific lane
    ranking = cur.fetchall()

    cur.execute("SELECT lane_id, lane_name FROM Lanes")
    all_lanes = cur.fetchall()

    cur.execute(
        """
        SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate
        FROM ChampionStats cs
        JOIN (
            SELECT champ_id, MAX(pickrate) AS max_pickrate
            FROM ChampionStats
            GROUP BY champ_id
        ) max_stats ON cs.champ_id = max_stats.champ_id
        JOIN Champions c ON cs.champ_id = c.champ_id
        WHERE cs.pickrate = max_stats.max_pickrate
        """
    )
    searchbar = cur.fetchall()

    conn.close()
    return render_template(
        "championranking.html",
        ranking=ranking,
        all_lanes=all_lanes,
        current_lane=lane_id,
        searchbar=searchbar,
        sort_by=sort_by,
    )


# Check admin password route
@app.route("/check-password", methods=["POST"]) # only post requests are accepted
def check_password(): 
    # Gets the JSON data sent in the request body and converts it to a python dictionary
    data = request.get_json() 
    password = data.get("password")

    # if statement that converts the password entered by the user to bytes and  compares it with the correcte password in bytes
    # if true, sets the session to true and returns python dictionary and converts it to JSON to use in JS
    if bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH): 
        session["is_admin"] = True 
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}) 


# Update data page route
@app.route("/updatedata") 
def updatedata_page(): 
    # if statement checking if the is_admin session is not true, if true then redirects to home page
    if session.get("is_admin") != True: 
        return redirect(url_for("home")) 

    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()

    cur.execute("SELECT champ_id, champ_name FROM Champions") # gets all champions for dropdown
    champions = cur.fetchall()

    cur.execute(
        """
        SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate
        FROM ChampionStats cs
        JOIN (
            SELECT champ_id, MAX(pickrate) AS max_pickrate
            FROM ChampionStats
            GROUP BY champ_id
        ) max_stats ON cs.champ_id = max_stats.champ_id
        JOIN Champions c ON cs.champ_id = c.champ_id
        WHERE cs.pickrate = max_stats.max_pickrate
        """
    )
    searchbar = cur.fetchall()

    conn.close()

    return render_template("updatedata.html", champions=champions, searchbar=searchbar)


# Get available lanes for a champion
@app.route("/get-available-lanes/<int:champ_id>")
def get_available_lanes(champ_id):
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        """
        SELECT cs.lane_id, l.lane_name
        FROM ChampionStats cs
        JOIN Lanes l ON cs.lane_id = l.lane_id
        WHERE cs.champ_id = ?
        """,
        (champ_id,),
    )
    lanes = [{"lane_id": lane_id, "lane_name": lane_name} for lane_id, lane_name in cur.fetchall()] # puts lane data into a python dictionary
    conn.close()
    return jsonify({"lanes": lanes}) 


# Get champion stats for a specific lane
@app.route("/get-champion-stats/<int:champ_id>/<int:lane_id>")
def get_champion_stats(champ_id, lane_id):
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT winrate, pickrate, banrate FROM ChampionStats WHERE champ_id = ? AND lane_id = ?",
        (champ_id, lane_id),
    )
    stats = cur.fetchone()
    conn.close()

    return jsonify({"winrate": stats[0], "pickrate": stats[1], "banrate": stats[2]})


# Update champion stats route
@app.route("/update-champion", methods=["POST"])
def update_champion(): # converts JSON to integer or float
    data = request.get_json()
    champ_id = data["champId"]
    lane_id = data["laneId"]
    winrate = float(data["winrate"])
    pickrate = float(data["pickrate"])
    banrate = float(data["banrate"])

    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE ChampionStats
        SET winrate = ?, pickrate = ?, banrate = ?
        WHERE champ_id = ? AND lane_id = ?
        """,
        (winrate, pickrate, banrate, champ_id, lane_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Champion stats updated."})


# Handle 404 errors
@app.errorhandler(404) # render 404 page if route not found
def page_not_found(error):
    return render_template("404.html"), 404


# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)