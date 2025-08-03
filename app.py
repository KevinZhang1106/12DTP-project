from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

ADMIN_PASSWORD = "password"

@app.route("/")
def home():
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate FROM ChampionStats cs "
        "JOIN (SELECT champ_id, MAX(pickrate) as max_pickrate FROM ChampionStats GROUP BY champ_id) max_stats " 
        "ON cs.champ_id=max_stats.champ_id JOIN Champions c ON cs.champ_id=c.champ_id "
        "WHERE cs.pickrate=max_stats.max_pickrate")
    searchbar = cur.fetchall()
    conn.close()
    return render_template("home.html", searchbar=searchbar)


@app.route("/champions/<int:champ_id>/<int:lane_id>")
def championstatspage(champ_id, lane_id):
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, cs.winrate, cs.pickrate, cs.banrate, l.lane_name, " 
        "c.champ_name, c.passive_ability, c.q_ability, c.w_ability, c.e_ability, c.r_ability "
        "FROM ChampionStats cs JOIN Champions c ON cs.champ_id=c.champ_id "
        "JOIN Lanes l ON cs.lane_id=l.lane_id "
        "WHERE cs.champ_id=? AND cs.lane_id=?", (champ_id, lane_id,)
    )
    championstats = cur.fetchone()

    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate FROM ChampionStats cs "
        "JOIN (SELECT champ_id, MAX(pickrate) as max_pickrate FROM ChampionStats GROUP BY champ_id) max_stats "
        "ON cs.champ_id=max_stats.champ_id JOIN Champions c ON cs.champ_id=c.champ_id "
        "WHERE cs.pickrate=max_stats.max_pickrate"
    )
    searchbar = cur.fetchall()

    cur.execute(
        "SELECT cs.lane_id FROM ChampionStats cs "
        "WHERE cs.champ_id=?", (champ_id, )
    )
    available_lanes = []
    for lanes in cur.fetchall():
        available_lanes.append(lanes[0])
    
    cur.execute(
        "SELECT lane_id, lane_name FROM Lanes"
    )
    all_lanes = cur.fetchall()

    conn.close()
    return render_template("champions.html", championstats=championstats, searchbar=searchbar, available_lanes=available_lanes, all_lanes=all_lanes, current_lane=lane_id, champ_id=champ_id)


@app.route('/championranking/<int:lane_id>')
def championrankingpage(lane_id):
    sort_by = request.args.get("sort_by", "winrate")
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()

    query = f"""SELECT cs.champ_id, c.champ_name, cs.winrate, cs.pickrate, cs.banrate FROM ChampionStats cs
                    JOIN Champions c ON cs.champ_id=c.champ_id      
                    WHERE cs.lane_id=?
                    ORDER BY cs.{sort_by} DESC"""
    
    cur.execute(query, (lane_id,)
                )
    ranking = cur.fetchall()

    cur.execute("SELECT lane_id, lane_name FROM Lanes")
    all_lanes = cur.fetchall()

    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate FROM ChampionStats cs "
        "JOIN (SELECT champ_id, MAX(pickrate) as max_pickrate FROM ChampionStats GROUP BY champ_id) max_stats "
        "ON cs.champ_id=max_stats.champ_id JOIN Champions c ON cs.champ_id=c.champ_id "
        "WHERE cs.pickrate=max_stats.max_pickrate"
    )
    searchbar = cur.fetchall()

    conn.close()
    return render_template("championranking.html", ranking=ranking, all_lanes=all_lanes, current_lane=lane_id, searchbar=searchbar, sort_by=sort_by)

@app.route("/check-password", methods=["POST"])
def check_password():
    data = request.get_json()
    password = data.get("password")

    if password == ADMIN_PASSWORD:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route("/updatedata")
def updatedata_page():
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute("SELECT champ_id, champ_name FROM Champions")
    champions = cur.fetchall()

    cur.execute(
        "SELECT cs.champ_id, cs.lane_id, c.champ_name, cs.pickrate FROM ChampionStats cs "
        "JOIN (SELECT champ_id, MAX(pickrate) as max_pickrate FROM ChampionStats GROUP BY champ_id) max_stats " 
        "ON cs.champ_id=max_stats.champ_id JOIN Champions c ON cs.champ_id=c.champ_id "
        "WHERE cs.pickrate=max_stats.max_pickrate")
    searchbar = cur.fetchall()

    conn.close()

    return render_template("updatedata.html", champions=champions, searchbar=searchbar)

@app.route("/get-available-lanes/<int:champ_id>")
def get_available_lanes(champ_id):
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT cs.lane_id, l.lane_name FROM ChampionStats cs
        JOIN Lanes l ON cs.lane_id = l.lane_id
        WHERE cs.champ_id = ?
    """, (champ_id,))

    lanes = []
    for lane_id, lane_name in cur.fetchall():
        lane = {"lane_id": lane_id, "lane_name": lane_name}
        lanes.append(lane)

    conn.close()
    return jsonify({"lanes": lanes})

@app.route("/get-champion-stats/<int:champ_id>/<int:lane_id>")
def get_champion_stats(champ_id, lane_id):
    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT winrate, pickrate, banrate 
        FROM ChampionStats 
        WHERE champ_id = ? AND lane_id = ?
    """, (champ_id, lane_id))
    stats = cur.fetchone()
    conn.close()

    return jsonify({
        "winrate": stats[0],
        "pickrate": stats[1],
        "banrate": stats[2]
    })

@app.route("/update-champion", methods=["POST"])
def update_champion():
    data = request.get_json()
    champ_id = data["champId"]
    lane_id = data["laneId"]
    winrate = float(data["winrate"])
    pickrate = float(data["pickrate"])
    banrate = float(data["banrate"])

    conn = sqlite3.connect("champions.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE ChampionStats 
        SET winrate = ?, pickrate = ?, banrate = ? 
        WHERE champ_id = ? AND lane_id = ?
    """, (winrate, pickrate, banrate, champ_id, lane_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Champion stats updated."})

if __name__ == "__main__":
    app.run(debug=True)