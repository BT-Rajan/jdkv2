import { createApp } from "vue";
import { createPinia } from "pinia";
import { router } from "./router";
import App from "./App.vue";

import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/components.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);

// Wait for the first navigation (and therefore the auth guard's identity
// check) to resolve before mounting, so there's no flash of the wrong
// screen (login vs. app shell) on load.
router.isReady().then(() => {
  app.mount("#app");
});
