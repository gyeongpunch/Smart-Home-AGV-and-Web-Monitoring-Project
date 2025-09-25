<template>
  <v-container fluid>
    <v-row>
      <!-- 디바이스 목록을 카드 컴포넌트로 렌더링 -->
      <v-col cols="12" sm="6" md="3"
            v-for="device in devices" :key="device.id">
        <DeviceCard :device="device" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import DeviceCard from '../components/DeviceCard.vue';

// (실제 앱에서는 이 데이터를 API 호출이나 글로벌 상태로부터 얻겠지만, 여기서는 예시를 위해 하드코딩합니다.)
const devices = [
  { id: 'AGV', name: 'AGV' },
  { id: 'AC',  name: '에어컨' },
  { id: 'WM',  name: '세탁기' },
  { id: 'AP',  name: '공기청정기' }
];
</script>

<style scoped>
/* 필요에 따라 메인 페이지 레이아웃에 대한 추가 스타일 */
</style>
