from flask import Flask, render_template

# Flask uygulamasını başlat
app = Flask(__name__)

# Ana sayfa rotası (URL: /)
@app.route('/')
def index():
    """
    Ana sayfayı render eder.
    Flask, 'render_template' kullandığında varsayılan olarak 'templates' klasörüne bakar.
    """
    return render_template('base.html')

# Bu blok, dosya doğrudan çalıştırıldığında sunucuyu başlatır
# (Örn: python main.py)
if __name__ == '__main__':
    app.run(debug=True)