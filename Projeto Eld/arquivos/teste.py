from flask import Flask, session
app = Flask(__name__)
app.secret_key = "legal"


@app.route("/")
def paginainicial():
    a = session.get('acesso')
    print(a)
    return 'aaa'

if __name__ == "__main__":
    app.run(debug=True, port=3000)
