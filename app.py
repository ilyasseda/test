import os
import sys
from kerykeion import AstrologicalSubject, Report
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Logging ayarları
logging.basicConfig(level=logging.DEBUG, filename="kerykeion.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Swiss Ephemeris dosyalarının tam yolunu belirtelim
sweph_path = os.path.join(os.path.dirname(__file__), "sweph")
os.environ["SWISSEPH_PATH"] = sweph_path

print(f"Swiss Ephemeris dosyalarının konumu: {sweph_path}")

@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    try:
        data = request.json
        name = data.get('name')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        hour = data.get('hour')
        minute = data.get('minute')
        city = data.get('city', 'Unknown')
        nation = data.get('nation', 'Unknown')
        lat = data.get('lat')
        lng = data.get('lng')

        # AstrologicalSubject oluştur
        subject = AstrologicalSubject(name, year, month, day, hour, minute, 
                                      city=city, nation=nation,
                                      lat=lat, lng=lng, 
                                      tz_str="Europe/Istanbul")

        # Rapor oluştur
        report = Report(subject)
        report_text = report.get_full_report()

        # Gezegen pozisyonlarını al
        planet_positions = {}
        for planet in subject.planets_list:
            planet_positions[planet.name] = {
                'sign': planet.sign,
                'position': planet.position
            }

        # Ev pozisyonlarını al
        house_positions = {}
        for i, house in enumerate(subject.houses_list, start=1):
            house_positions[f"House {i}"] = {
                'sign': house.sign,
                'position': house.position
            }

        # Sonuçları JSON olarak döndür
        return jsonify({
            'report': report_text,
            'planet_positions': planet_positions,
            'house_positions': house_positions
        })

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        print(f"Hata türü: {type(e).__name__}")
        logging.exception("Bir hata oluştu:")
        
        # Hata stack trace'ini yazdıralım
        import traceback
        traceback.print_exc()

        return jsonify({'error': str(e)}), 500

@app.route('/version', methods=['GET'])
def get_version():
    try:
        import kerykeion
        kerykeion_version = kerykeion.__version__
    except AttributeError:
        kerykeion_version = "Belirlenemedi"

    return jsonify({
        'kerykeion_version': kerykeion_version,
        'python_version': sys.version
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))