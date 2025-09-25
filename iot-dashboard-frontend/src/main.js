import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Vuetify 3 플러그인 임포트 및 설정
import 'vuetify/styles';                    // Vuetify 기본 스타일
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
const vuetify = createVuetify({
  components,
  directives,
});

// Vue 앱 생성 및 마운트
createApp(App)
  .use(router)    // Vue Router 사용
  .use(vuetify)   // Vuetify 사용 (머티리얼 UI 컴포넌트)
  .mount('#app');
