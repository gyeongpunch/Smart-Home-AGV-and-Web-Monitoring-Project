<template>
    <v-card outlined class="device-card">
      <!-- 카드 제목: 디바이스 이름 표시 -->
      <v-card-title>{{ device.name }}</v-card-title>
      <!-- 카드 하단 액션: 상세보기 버튼 -->
      <v-card-actions>
        <v-btn color="primary" :to="`/device/${device.id}/chart`">
          상세 보기
        </v-btn>
      </v-card-actions>
    </v-card>
  </template>
  
  <script setup>
  // DeviceCard는 device 객체를 prop으로 전달받음
  const props = defineProps({
    device: { type: Object, required: true }
  });
  </script>
  
  <style scoped>
  .device-card {
    /* 카드 컴포넌트의 폭이나 여백 등을 조절 가능 */
    width: 100%;
  }
  </style>
  