<!-- src/pages/DeviceChartPage.vue -->
<template>
  <v-container fluid>
    <v-row>
      <v-col
        v-for="device in devices" :key="device.device_id"
        cols="12" md="4"
      >
        <div v-if="!deviceData[device.device_id].error" class="chart-card">
          <canvas :ref="el => canvasRefs[device.device_id] = el"></canvas>
        </div>
        <div v-else class="error-message">
          {{ deviceData[device.device_id].error }}
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

// 1️⃣ 먼저 실제 DB에 있는 디바이스 목록을 받아옵니다.
const devices = ref([])
onMounted(async () => {
  try {
    const res = await axios.get('/api/devices')
    // AGV 빼고 나머지 3개만 사용
    devices.value = res.data.filter(d => d.device_name !== 'AGV')
    await initCharts()
  } catch (e) {
    console.error('디바이스 목록 로드 실패', e)
  }
})

// 2️⃣ 각 디바이스별 데이터와 에러 상태를 보관할 reactive 객체
const deviceData = reactive({})
const canvasRefs = reactive({})
const chartInstances = []

// 3️⃣ 실제 차트 초기화 함수
async function initCharts() {
  for (const dev of devices.value) {
    const id = dev.device_id
    deviceData[id] = { readings: [], latestEvent: '', error: null }
    try {
      // 센서 리딩
      const r = await axios.get(`/api/devices/${id}/readings`)
      if (!r.data.length) throw new Error('No sensor data available')
      const readings = [...r.data].sort((a,b)=> new Date(a.reading_time)-new Date(b.reading_time))
      deviceData[id].readings = readings

      // 이벤트 (가장 최신 타입)
      let evType = 'No recent event'
      const e = await axios.get(`/api/devices/${id}/events`)
      if (e.data.length) {
        const sorted = [...e.data].sort((a,b)=>new Date(a.event_time)-new Date(b.event_time))
        evType = sorted[sorted.length-1].event_type
      }
      deviceData[id].latestEvent = evType

      // 차트 그리기
      const ctx = canvasRefs[id].getContext('2d')
      const labels = readings.map(r=>r.reading_time)
      const dataPoints = readings.map(r=>r.value_float)
      const chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: dev.device_name,
            data: dataPoints,
            borderColor: '#42A5F5',
            backgroundColor: 'rgba(66,165,245,0.1)',
            tension: 0.1,
            fill: false,
            pointRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: { display: true, text: evType, font: { size: 16 } },
            legend: { display: false }
          },
          scales: {
            x: { title: { display: true, text: 'Time' }, ticks:{ autoSkip:true, maxTicksLimit:5 } },
            y: { title: { display: true, text: 'Value' }, beginAtZero:true }
          }
        }
      })
      chartInstances.push(chart)

    } catch (err) {
      console.error(err)
      deviceData[id].error = err.message
    }
  }
}

// 4️⃣ 언마운트 시 차트 정리
onUnmounted(() => {
  chartInstances.forEach(c=>c.destroy())
})
</script>

<style scoped>
.chart-card {
  position: relative;
  height: 300px;
  padding: 16px;
}
.chart-card canvas {
  width: 100% !important;
  height: 100% !important;
}
.error-message {
  padding: 16px;
  color: #f44336;
  background: #ffebee;
  border: 1px solid #ffcdd2;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
