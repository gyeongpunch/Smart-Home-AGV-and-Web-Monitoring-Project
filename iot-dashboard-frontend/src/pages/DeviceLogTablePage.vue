<template>
    <div class="log-page">
      <h2>{{ deviceName }} – 로그 데이터</h2>
  
      <div v-if="loading">데이터를 불러오는 중…</div>
      <div v-else-if="error" class="error">{{ error }}</div>
  
      <table v-else class="log-table">
        <thead>
          <tr><th>시간</th><th>값</th></tr>
        </thead>
        <tbody>
          <tr v-for="(log, i) in logs" :key="i">
            <td>{{ log.time }}</td>
            <td>{{ log.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute } from 'vue-router';
  
  const route = useRoute();
  
  // --- 1) 문자열 ID → 숫자 device_id 매핑
  const idMap = {
    AGV: 1,    // jetson-robot
    WM: 2,     // esp32-washer
    AC: 3,     // esp32-ac
    AP: 4      // esp32-purifier
  };
  
  const strId      = route.params.id;
  const numericId  = idMap[strId];
  const deviceName = computed(() => ({
    AGV: 'AGV',
    WM: '세탁기',
    AC: '에어컨',
    AP: '공기청정기'
  }[strId] || strId));
  
  const logs    = ref([]);
  const loading = ref(true);
  const error   = ref(null);
  
  onMounted(async () => {
    if (!numericId) {
      error.value = '알 수 없는 디바이스입니다.';
      loading.value = false;
      return;
    }
  
    try {
      // --- 2) 숫자 ID 로 요청
      const res = await fetch(`/api/devices/${numericId}/readings`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log('📥 fetched logs:', data);
  
      // --- 3) 화면용 포맷으로 변환
      logs.value = data.map(r => ({
        time:  r.reading_time,  // 백엔드 필드명에 맞춤
        value: r.value_float
      }));
    } catch (e) {
      console.error(e);
      error.value = `로그를 불러오는 중 오류: ${e.message}`;
    } finally {
      loading.value = false;
    }
  });
  </script>
  
  <style scoped>
  .log-page { padding:16px; }
  .error     { color:red; margin:16px 0; }
  .log-table {
    width:100%; border-collapse:collapse; margin-top:8px;
  }
  .log-table th, .log-table td {
    border:1px solid #ccc; padding:8px; text-align:left;
  }
  .log-table th { background:#f0f0f0; }
  </style>
  