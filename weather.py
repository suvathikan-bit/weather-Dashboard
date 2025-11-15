import streamlit as st
import requests
from datetime import datetime, timedelta


st.set_page_config(page_title="Suvathikan Weather Dashboard", page_icon="⛅", layout="wide")
st.image("logo.png", width=120)
st.markdown("<h1 style='color:#4FC3F7;'>🌦️ Suvathikan Weather Dashboard</h1>", unsafe_allow_html=True)


API_KEY = "3729667eb86355595d2be48f76ccc8b0"


city_name = st.text_input("Enter city:", "Colombo")


def weather_color(description):
    desc = description.lower()
    if "cloud" in desc:
        return "#B0BEC5"
    elif "rain" in desc or "drizzle" in desc:
        return "#4FC3F7"
    elif "sun" in desc or "clear" in desc:
        return "#FFD54F"
    elif "snow" in desc:
        return "#E1F5FE"
    else:
        return "#FFFFFF"

def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    return r

def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    return r

if st.button("Get Weather"):
    if city_name.strip() == "":
        st.markdown("<p style='color:red;'>Enter a valid city.</p>", unsafe_allow_html=True)
    else:
        current = get_current_weather(city_name)
        if "main" not in current:
            st.error("City not found. Check the spelling.")
        else:
           
            temp = current["main"]["temp"]
            feels = current["main"]["feels_like"]
            humidity = current["main"]["humidity"]
            wind = current["wind"]["speed"]
            desc = current["weather"][0]["description"].title()
            icon = current["weather"][0]["icon"]
            country_code = current["sys"]["country"]
            country_name = country_code
            timezone_offset = current.get("timezone", 0)  

            
            utc_now = datetime.utcnow()
            city_time = utc_now + timedelta(seconds=timezone_offset)
            city_time_str = city_time.strftime("%A, %d %b %Y | %I:%M %p")

            sunrise = datetime.utcfromtimestamp(current["sys"]["sunrise"] + timezone_offset).strftime("%I:%M %p")
            sunset = datetime.utcfromtimestamp(current["sys"]["sunset"] + timezone_offset).strftime("%I:%M %p")

            bg_color = weather_color(desc)
            st.markdown(f"<div style='background-color:{bg_color}; padding:20px; border-radius:10px;'>"
                        f"<h2>📍 {city_name.title()}, {country_name}</h2>"
                        f"<h3>🕒 Local Time: {city_time_str}</h3>"
                        f"<h3>🌡 Temperature: {temp}°C | 🤒 Feels Like: {feels}°C</h3>"
                        f"<h3>💧 Humidity: {humidity}% | 🌬 Wind: {wind} m/s</h3>"
                        f"<h3>🌈 Condition: {desc} <img src='http://openweathermap.org/img/wn/{icon}@2x.png'></h3>"
                        f"<h4>🌅 Sunrise: {sunrise} | 🌇 Sunset: {sunset}</h4>"
                        f"</div>", unsafe_allow_html=True)

            
            forecast = get_forecast(city_name)
            if "list" in forecast:
                st.markdown("<h2 style='color:#4DB6AC;'>📅 5-Day Forecast</h2>", unsafe_allow_html=True)
                daily_data = {}
                for entry in forecast["list"]:
                    date_txt = entry["dt_txt"].split()[0]
                    temp_min = entry["main"]["temp_min"]
                    temp_max = entry["main"]["temp_max"]
                    desc_entry = entry["weather"][0]["description"].title()
                    icon_entry = entry["weather"][0]["icon"]
                    if date_txt not in daily_data:
                        daily_data[date_txt] = {"min": temp_min, "max": temp_max, "desc": desc_entry, "icon": icon_entry}
                    else:
                        daily_data[date_txt]["min"] = min(daily_data[date_txt]["min"], temp_min)
                        daily_data[date_txt]["max"] = max(daily_data[date_txt]["max"], temp_max)

                count = 0
                for date_str, values in daily_data.items():
                    if count >= 5:
                        break
                    date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %b")
                    st.markdown(f"<p style='color:#FF7043;'>{date_formatted} - Hi: {values['max']}°C | Lo: {values['min']}°C - {values['desc']} <img src='http://openweathermap.org/img/wn/{values['icon']}.png'></p>", unsafe_allow_html=True)
                    count +=1

            
            st.markdown("<h2 style='color:#FFA726;'>⏰ Hourly Forecast (Next 12 Hours)</h2>", unsafe_allow_html=True)
            now = datetime.utcnow() + timedelta(seconds=timezone_offset)
            hourly_count = 0
            for entry in forecast["list"]:
                forecast_time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S") + timedelta(seconds=timezone_offset)
                if forecast_time > now and hourly_count < 12:
                    time_str = forecast_time.strftime("%I %p")
                    temp_h = entry["main"]["temp"]
                    desc_h = entry["weather"][0]["description"].title()
                    icon_h = entry["weather"][0]["icon"]
                    st.markdown(f"<p style='color:#4FC3F7;'>{time_str} - {temp_h}°C - {desc_h} <img src='http://openweathermap.org/img/wn/{icon_h}.png'></p>", unsafe_allow_html=True)
                    hourly_count += 1
