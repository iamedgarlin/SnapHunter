import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useWeatherStore = defineStore('weather', () => {
  const temp = ref(null)
  const desc = ref('')
  const suburb = ref('Melbourne')
  const weatherCode = ref(0)
  const isGoodWeather = ref(true)
  const uvIndex = ref(null)
  const loading = ref(false)
  const error = ref(false)

  function getUvLabel(uv) {
    if (uv === null) return { label: 'N/A', color: '#94a3b8' }
    if (uv <= 2)  return { label: 'Low',       color: '#16a34a' }
    if (uv <= 5)  return { label: 'Moderate',  color: '#ca8a04' }
    if (uv <= 7)  return { label: 'High',      color: '#ea580c' }
    if (uv <= 10) return { label: 'Very High', color: '#dc2626' }
    return { label: 'Extreme', color: '#7c3aed' }
  }

  async function fetchWeather() {
    loading.value = true
    try {
      const pos = await new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 })
      )
      const { latitude, longitude } = pos.coords

      const [weatherRes, geoRes] = await Promise.all([
        axios.get(`https://api.open-meteo.com/v1/forecast`, {
          params: {
            latitude,
            longitude,
            current: 'temperature_2m,weathercode,uv_index',
            timezone: 'auto'
          }
        }),
        axios.get(`https://nominatim.openstreetmap.org/reverse`, {
          params: { lat: latitude, lon: longitude, format: 'json' },
          headers: { 'Accept-Language': 'en' }
        })
      ])

      temp.value = Math.round(weatherRes.data.current.temperature_2m)
      weatherCode.value = weatherRes.data.current.weathercode
      uvIndex.value = Math.round(weatherRes.data.current.uv_index ?? 0)

      const address = geoRes.data.address
      suburb.value = address.suburb
        || address.neighbourhood
        || address.town
        || address.city
        || 'Melbourne'

      if (weatherCode.value === 0) {
        desc.value = 'Clear sky'
        isGoodWeather.value = true
      } else if (weatherCode.value <= 3) {
        desc.value = 'Partly cloudy'
        isGoodWeather.value = true
      } else if (weatherCode.value <= 67) {
        desc.value = 'Rainy'
        isGoodWeather.value = false
      } else {
        desc.value = 'Cloudy'
        isGoodWeather.value = true
      }

    } catch {
      temp.value = '--'
      desc.value = 'Melbourne'
      suburb.value = 'Melbourne'
      uvIndex.value = null
      isGoodWeather.value = true
      error.value = true
    } finally {
      loading.value = false
    }
  }

  return { temp, desc, suburb, weatherCode, isGoodWeather, uvIndex, getUvLabel, loading, error, fetchWeather }
})