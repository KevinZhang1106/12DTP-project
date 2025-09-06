"""
Flask application for League of Legends champion statistics website.
"""

import sqlite3
from contextlib import contextmanager

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    abort,
)
import bcrypt

from config import ADMIN_PASSWORD_HASH

# Initialize Flask app and secret key for sessions
app = Flask(__name__)
app.secret_key = "secretkey"


# Context manager for database connection
@contextmanager
def get_db():
    conn = sqlite3.connect("champions.db")
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


# gets data for searchbar
def get_searchbar(cur):
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
    return cur.fetchall()


@app.route("/")
def home():
    return redirect(url_for("championrankingpage", lane_id=0))


# Champion stats page route
@app.route("/champions/<int:champ_id>/<int:lane_id>")
def championstatspage(champ_id, lane_id):
    session.clear()
    with get_db() as cur:

        searchbar = get_searchbar(cur)

        # gets stats for the specific champion and lane
        cur.execute(
            """
            SELECT cs.champ_id, cs.lane_id, cs.winrate, cs.pickrate,
                   cs.banrate, l.lane_name, c.champ_name, c.passive_ability,
                   c.q_ability, c.w_ability, c.e_ability, c.r_ability
            FROM ChampionStats cs
            JOIN Champions c ON cs.champ_id = c.champ_id
            JOIN Lanes l ON cs.lane_id = l.lane_id
            WHERE cs.champ_id = ? AND cs.lane_id = ?
            """,
            (champ_id, lane_id),
        )
        championstats = cur.fetchone()  # gets the next row as a tuple

        if championstats is None:
            abort(404)

        # gets all lanes for a specific champion
        cur.execute(
            "SELECT cs.lane_id FROM ChampionStats cs WHERE cs.champ_id = ?",
            (champ_id,),
        )
        available_lanes = [lane[0] for lane in cur.fetchall()]

        cur.execute("SELECT lane_id, lane_name FROM Lanes")  # gets all lanes
        all_lanes = cur.fetchall()

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
    sort_by = request.args.get("sort_by", "winrate")

    if sort_by not in ("winrate", "pickrate", "banrate"):
        abort(404)

    if lane_id < 0 or lane_id > 5:
        abort(404)

    with get_db() as cur:
        if lane_id == 0:
            query = f"""
                SELECT cs.champ_id, c.champ_name,
                cs.winrate, cs.pickrate, cs.banrate,
                l.lane_name
                FROM ChampionStats cs
                JOIN Champions c ON cs.champ_id = c.champ_id
                JOIN Lanes l ON cs.lane_id = l.lane_id
                ORDER BY cs.{sort_by} DESC
            """
            # gets all stats and sorts them by sort_by value
            cur.execute(query)
            ranking = cur.fetchall()
        else:

            query = f"""
                SELECT cs.champ_id, c.champ_name,
                cs.winrate, cs.pickrate, cs.banrate
                FROM ChampionStats cs
                JOIN Champions c ON cs.champ_id = c.champ_id
                WHERE cs.lane_id = ?
                ORDER BY cs.{sort_by} DESC
            """
            # gets stats for specific lane and sorts them by sort_by value
            cur.execute(query, (lane_id,))
            ranking = cur.fetchall()

        cur.execute("SELECT lane_id, lane_name FROM Lanes")
        all_lanes = cur.fetchall()

        searchbar = get_searchbar(cur)

    return render_template(
        "championranking.html",
        ranking=ranking,
        all_lanes=all_lanes,
        current_lane=lane_id,
        searchbar=searchbar,
        sort_by=sort_by,
    )


# Check admin password route
@app.route("/check-password", methods=["POST"])
def check_password():
    data = request.get_json()
    password = data.get("password")

    if bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH):
        session["is_admin"] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


# Update data page route
@app.route("/updatedata")
def updatedata_page():
    if session.get("is_admin") is not True:
        return redirect(url_for("home"))

    with get_db() as cur:
        # gets all champions for dropdown
        cur.execute("SELECT champ_id, champ_name FROM Champions")
        champions = cur.fetchall()

        searchbar = get_searchbar(cur)

    return render_template(
        "updatedata.html", champions=champions, searchbar=searchbar
    )


# Get available lanes for a champion
@app.route("/get-available-lanes/<int:champ_id>")
def get_available_lanes(champ_id):
    with get_db() as cur:
        cur.execute(
            """
            SELECT cs.lane_id, l.lane_name
            FROM ChampionStats cs
            JOIN Lanes l ON cs.lane_id = l.lane_id
            WHERE cs.champ_id = ?
            """,
            (champ_id,),
        )
        # puts lane data into a python dictionary
        lanes = [
            {"lane_id": lane_id, "lane_name": lane_name}
            for lane_id, lane_name in cur.fetchall()
        ]
    return jsonify({"lanes": lanes})


# Get champion stats for a specific lane
@app.route("/get-champion-stats/<int:champ_id>/<int:lane_id>")
def get_champion_stats(champ_id, lane_id):
    with get_db() as cur:
        cur.execute(
            "SELECT winrate, pickrate, banrate FROM ChampionStats "
            "WHERE champ_id = ? AND lane_id = ?",
            (champ_id, lane_id),
        )
        stats = cur.fetchone()

    return jsonify(
        {"winrate": stats[0], "pickrate": stats[1], "banrate": stats[2]}
    )


# Update champion stats route
@app.route("/update-champion", methods=["POST"])
def update_champion():
    data = request.get_json()
    champ_id = data["champId"]
    lane_id = data["laneId"]
    winrate = float(data["winrate"])
    pickrate = float(data["pickrate"])
    banrate = float(data["banrate"])

    with get_db() as cur:
        cur.execute(
            """
            UPDATE ChampionStats
            SET winrate = ?, pickrate = ?, banrate = ?
            WHERE champ_id = ? AND lane_id = ?
            """,
            (winrate, pickrate, banrate, champ_id, lane_id),
        )

    return jsonify({"success": True, "message": "Champion stats updated."})


# Handle 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
