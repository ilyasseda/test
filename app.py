import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Logging ayarları
logging.basicConfig(level=logging.DEBUG, filename="kerykeion.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Kerykeion'u import et
try:
    from kerykeion import AstrologicalSubject, Report
    logging.info("Kerykeion successfully imported")
except ImportError as e:
    logging.error(f"Error importing Kerykeion: {e}")
    raise

@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    try:
        data = request.json
        logging.info(f"Received data: {data}")

        name = data.get('name')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        hour = data.get('hour')
        minute = data.get('minute')
        lat = data.get('lat')
        lng = data.get('lng')

        # AstrologicalSubject oluştur
        subject = AstrologicalSubject(name, year, month, day, hour, minute, 
                                      lat=lat, lng=lng, 
                                      tz_str="Europe/Istanbul")

        # Rapor oluştur
        report = Report(subject)
        
        # Raporu yazdır
        report_text = report.print_report()

        # Gezegen pozisyonlarını al
        planet_positions = {}
        for planet in subject.planets_list:
            planet_positions[planet.name] = {
                'sign': planet.sign,
                'position': planet.longitude
            }

        # Ev pozisyonlarını al
        house_positions = {}
        for i, house in enumerate(subject.houses_list, start=1):
            house_positions[f"House {i}"] = {
                'sign': house.sign,
                'position': house.longitude
            }

        # Sonuçları JSON olarak döndür
        result = {
            'report': report_text,
            'planet_positions': planet_positions,
            'house_positions': house_positions
        }
        logging.info("Calculation successful")
        return jsonify(result)

    except Exception as e:
        logging.exception("Bir hata oluştu:")
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
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)