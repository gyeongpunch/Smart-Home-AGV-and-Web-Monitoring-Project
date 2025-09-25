<template>
    <!-- Vuetify 리스트로 사이드 메뉴 구성 -->
    <v-list dense nav>
      <v-list-item v-for="device in devices" :key="device.id"
                   :to="`/device/${device.id}/chart`" link>
        <v-list-item-title>{{ device.name }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </template>
  
  <script setup>
  // devices 목록을 상위로부터 prop으로 전달받음
  const props = defineProps({
    devices: { type: Array, required: true }
  });
  </script>
  
  <style scoped>
  /* 사이드바 폭이나 배경 등에 대한 스타일 커스터마이징 가능 */
  </style>
  