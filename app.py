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
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    logging.basicConfig(level=logging.DEBUG)

# Swiss Ephemeris dosyalarının tam yolunu belirtelim
sweph_path = os.path.join(os.path.dirname(__file__), "sweph")
os.environ["SWISSEPH_PATH"] = sweph_path

app.logger.info(f"Swiss Ephemeris dosyalarının konumu: {sweph_path}")

@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")
        
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

        app.logger.info(f"Input parameters: name={name}, year={year}, month={month}, day={day}, "
                        f"hour={hour}, minute={minute}, city={city}, nation={nation}, lat={lat}, lng={lng}")

        # AstrologicalSubject oluştur
        subject = AstrologicalSubject(name, year, month, day, hour, minute, 
                                      city=city, nation=nation,
                                      lat=lat, lng=lng, 
                                      tz_str="Europe/Istanbul")

        # Rapor oluştur
        report = Report(subject)
        report_text = report.get_full_report()  # get_full_report kullanıyoruz

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
        result = {
            'report': report_text,
            'planet_positions': planet_positions,
            'house_positions': house_positions
        }
        app.logger.info(f"Calculation successful. Returning result: {result}")
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(f"Error type: {type(e).__name__}")
        app.logger.exception("Exception details:")
        
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