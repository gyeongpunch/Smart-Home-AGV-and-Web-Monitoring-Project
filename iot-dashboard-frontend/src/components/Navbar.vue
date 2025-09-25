<template>
  <!-- Vuetify 앱바: primary 색상, 다크 테마 적용 -->
  <v-app-bar color="primary" dark flat app>
    <!-- 왼쪽 타이틀 -->
    <v-toolbar-title>Home IoT Dashboard</v-toolbar-title>
    <v-spacer></v-spacer>
    <!-- 우측 내비게이션 버튼들 -->
    <v-btn text to="/">Home</v-btn>
    <!-- Chart/Log 버튼: deviceId가 있을 때만 활성 -->
    <v-btn text :to="deviceId ? `/device/${deviceId}/chart` : '#'"
          :disabled="!deviceId">
      Chart 보기
    </v-btn>
    <v-btn text :to="deviceId ? `/device/${deviceId}/log` : '#'"
          :disabled="!deviceId">
      Log 보기
    </v-btn>
  </v-app-bar>
</template>

<script setup>
// Navbar은 상위(App.vue)로부터 현재 디바이스 ID를 prop으로 전달받음
const props = defineProps({
  deviceId: { type: String, default: null }
});
</script>

<style scoped>
/* 필요에 따라 내비게이션 바의 추가 스타일 지정 가능 */
</style>
