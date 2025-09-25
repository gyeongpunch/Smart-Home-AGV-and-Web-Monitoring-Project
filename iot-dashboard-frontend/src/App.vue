<template>
  <!-- Vuetify v-app 컨테이너 -->
  <v-app>
    <!-- 상단 Navbar 컴포넌트 -->
    <Navbar :deviceId="currentDeviceId" />

    <!-- 좌측 Sidebar를 포함한 레이아웃 구조 -->
    <v-navigation-drawer app permanent>
      <!-- Sidebar 컴포넌트 (디바이스 목록) -->
      <Sidebar :devices="devices" />
    </v-navigation-drawer>

    <!-- 메인 콘텐츠 영역: 라우팅된 페이지가 표시됨 -->
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { reactive, computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';
import Sidebar from './components/Sidebar.vue';

// 디바이스 목록 (ID와 이름 정의)
const devices = reactive([
  { id: 'AGV', name: 'AGV' },
  { id: 'AC',  name: '에어컨' },
  { id: 'WM',  name: '세탁기' },
  { id: 'AP',  name: '공기청정기' }
]);

// 현재 라우트의 디바이스 ID 파라미터를 추출 (예: /device/AGV/chart -> AGV)
const route = useRoute();
const currentDeviceId = computed(() => route.params.id || null);
</script>

<style>
/* 전역 레이아웃 관련 스타일 설정 */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>
