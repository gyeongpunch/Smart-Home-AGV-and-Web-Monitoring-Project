import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../pages/MainPage.vue';
import DeviceChartPage from '../pages/DeviceChartPage.vue';
import DeviceLogTablePage from '../pages/DeviceLogTablePage.vue';

const routes = [
  { path: '/', component: MainPage },                           // 홈: 디바이스 카드 목록
  { path: '/device/:id/chart', component: DeviceChartPage },    // 디바이스별 차트 페이지
  { path: '/device/:id/log', component: DeviceLogTablePage }    // 디바이스별 로그 테이블 페이지
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
