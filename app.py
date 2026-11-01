from flask import Flask, render_template, request, jsonify
from simulator import Simulator, ALGORITHMS

app = Flask(__name__)
sim = Simulator()

@app.get("/")
def index():
    return render_template("index.html", algorithms=ALGORITHMS)

@app.get("/api/state")
def state():
    return jsonify(sim.snapshot())

@app.post("/api/configure")
def configure():
    data = request.get_json(silent=True) or {}
    algorithm = data.get("algorithm", "mutex")
    count = int(data.get("process_count", 3))
    if algorithm not in ALGORITHMS:
        return jsonify({"error": "Unknown algorithm"}), 400
    if algorithm == "peterson":
        count = 2
    count = max(2, min(count, 6))
    sim.configure(algorithm, count)
    return jsonify(sim.snapshot())

@app.post("/api/step")
def step():
    return jsonify(sim.step())

@app.post("/api/run")
def run():
    data = request.get_json(silent=True) or {}
    steps = max(1, min(int(data.get("steps", 8)), 30))
    state = sim.snapshot()
    for _ in range(steps):
        state = sim.step()
    return jsonify(state)

@app.post("/api/reset")
def reset():
    sim.reset()
    return jsonify(sim.snapshot())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
