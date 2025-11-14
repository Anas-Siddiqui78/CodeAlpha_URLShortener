from flask import Flask, request, redirect, render_template_string, jsonify
import sqlite3
import string
import random

app = Flask(__name__)

# ------------------- Database -------------------
def init_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_url(long_url):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    existing = cursor.execute("SELECT short_code FROM urls WHERE long_url=?", (long_url,)).fetchone()
    if existing:
        conn.close()
        return existing[0]
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    while cursor.execute("SELECT * FROM urls WHERE short_code=?", (short_code,)).fetchone():
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
    conn.commit()
    conn.close()
    return short_code

def get_long_url(short_code):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_code=?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_urls():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute("SELECT short_code, long_url FROM urls ORDER BY id DESC")
    urls = cursor.fetchall()
    conn.close()
    return urls

# ------------------- Routes -------------------
@app.route('/')
def home():
    urls = get_all_urls()
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🌟 Fabulous URL Shortener 🌟</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/particles.js"></script>
<style>
  body, html { height: 100%; margin:0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#1b1b2f; display:flex; justify-content:center; align-items:center; overflow:hidden;}
  #particles-js { position:absolute; width:100%; height:100%; z-index:0; }
  .card { position:relative; z-index:1; border-radius:20px; padding:30px; width:100%; max-width:600px; background:rgba(255,255,255,0.1); backdrop-filter:blur(15px); box-shadow:0 10px 30px rgba(0,0,0,0.3); border:none;}
  h2 { color:#fff; text-shadow:0 2px 5px rgba(0,0,0,0.4); font-weight:bold; }
  .form-control { border-radius:50px; border:none; padding:15px 20px; transition: all 0.3s ease-in-out; }
  .form-control:focus { outline:none; box-shadow:0 0 15px rgba(110,142,251,0.8); transform:scale(1.02);}
  .btn-primary { border-radius:50px; font-weight:bold; background: linear-gradient(90deg,#6e8efb,#a777e3); border:none; transition: all 0.3s ease-in-out;}
  .btn-primary:hover { transform:scale(1.05); background: linear-gradient(90deg,#a777e3,#6e8efb); box-shadow:0 0 15px rgba(255,255,255,0.5);}
  .alert-success { border-radius:15px; font-weight:bold; color:#fff; background:rgba(46,204,113,0.8); border:none; text-shadow:0 1px 3px rgba(0,0,0,0.3);}
  table th, table td { vertical-align: middle; text-align:center; color:#fff; }
  table thead { background: rgba(0,0,0,0.3);}
  a { color:#fff; text-decoration:none; }
</style>
</head>
<body>

<div id="particles-js"></div>

<div class="container animate__animated animate__fadeInDown">
  <div class="card shadow animate__animated animate__fadeInUp animate__delay-1s">
    <h2 class="text-center mb-4 animate__animated animate__bounceIn">🌟 Fabulous URL Shortener 🌟</h2>

    <form method="POST" action="/shorten-url" class="animate__animated animate__fadeInUp animate__delay-2s d-flex mb-3">
      <input type="url" name="long_url" class="form-control me-2" placeholder="Enter your URL" required>
      <button type="submit" class="btn btn-primary">Shorten</button>
    </form>

    {% if short_url %}
    <div class="alert alert-success mt-3 animate__animated animate__fadeInDown">
      Short URL: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
      <button class="btn btn-sm btn-outline-light ms-2" onclick="copyURL('{{ short_url }}')">Copy</button>
    </div>
    {% endif %}

    {% if urls %}
    <h5 class="mt-4">All Stored URLs</h5>
    <div class="table-responsive">
      <table class="table table-striped table-bordered mt-2">
        <thead>
          <tr><th>Short URL</th><th>Original URL</th><th>Action</th></tr>
        </thead>
        <tbody>
          {% for short_code, long_url in urls %}
          <tr>
            <td><a href="{{ request.host_url }}{{ short_code }}" target="_blank">{{ request.host_url }}{{ short_code }}</a></td>
            <td>{{ long_url }}</td>
            <td><button class="btn btn-sm btn-outline-light" onclick="copyText('{{ request.host_url }}{{ short_code }}')">Copy</button></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}
  </div>
</div>

<script>
function copyURL(url){
  navigator.clipboard.writeText(url);
  alert("✅ URL copied!");
}
function copyText(text){
  navigator.clipboard.writeText(text);
  alert("✅ URL copied!");
}

// Particles.js configuration
particlesJS("particles-js", {
  "particles": {
    "number": { "value": 80, "density": { "enable": true, "value_area": 800 }},
    "color": { "value": "#ffffff" },
    "shape": { "type": "circle" },
    "opacity": { "value": 0.5, "random": true },
    "size": { "value": 3, "random": true },
    "line_linked": { "enable": true, "distance": 150, "color": "#ffffff", "opacity": 0.2, "width": 1 },
    "move": { "enable": true, "speed": 2, "direction": "none", "random": true, "straight": false, "out_mode": "out" }
  },
  "interactivity": {
    "detect_on": "canvas",
    "events": { "onhover": { "enable": true, "mode": "repulse" }, "onclick": { "enable": true, "mode": "push" } },
    "modes": { "repulse": { "distance": 100 }, "push": { "particles_nb": 4 } }
  },
  "retina_detect": true
});
</script>

</body>
</html>
''', short_url=request.args.get('short_url'), urls=urls)

@app.route('/shorten-url', methods=['POST'])
def shorten_url_form():
    long_url = request.form.get('long_url')
    if long_url:
        short_code = save_url(long_url)
        short_url = request.host_url + short_code
        return redirect(f"/?short_url={short_url}")
    return redirect('/')

@app.route('/shorten', methods=['POST'])
def shorten_url_api():
    data = request.get_json()
    long_url = data.get('long_url')
    if not long_url:
        return jsonify({"error": "Missing long_url"}), 400
    short_code = save_url(long_url)
    short_url = request.host_url + short_code
    return jsonify({"short_url": short_url})

@app.route('/<short_code>')
def redirect_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    return "URL not found", 404

# ------------------- Run -------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
