from flask import Flask, render_template, request, redirect

print("!!! app detected !!!")
app = Flask(__name__)

links = {
    "home":"index.html",
    "impressum":'impressum.html',
    "dataprotection":"datenschutzerklaerung.html"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', debug=app.debug)
    elif request.method=='POST':
        firstarg = [l for l in request.form][0]
        if firstarg in links:
            print(f"{links[firstarg]}")
            return show_page(links[firstarg])
        if "command" in request.form:
            command = request.form["command"]
            if command == "mastrutils":
                return redirect("/mastrutils")
            elif command == "smardutils":
                return redirect("/smardutils")
    return render_template('index.html', debug=app.debug)

def show_page(page):
    return render_template(page)

def impressum():
    return render_template('impressum.html')
